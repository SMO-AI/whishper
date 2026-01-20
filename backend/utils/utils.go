package utils

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"sort"
	"strconv"
	"strings"

	"github.com/rs/zerolog/log"
	"github.com/wader/goutubedl"
	"go.mongodb.org/mongo-driver/bson/primitive"

	"codeberg.org/pluja/whishper/models"
)

func SanitizeFilename(filename string) string {
	// First remove trailing spaces
	filename = strings.TrimSpace(filename)
	// Then remove quotes and dots
	filename = strings.Trim(filename, `"'.`)
	reg, _ := regexp.Compile("[^a-zA-Z0-9]+")
	filename = reg.ReplaceAllString(filename, "_")
	return filename
}

func DownloadMedia(t *models.Transcription) (string, error) {
	if t.SourceUrl == "" {
		log.Debug().Msg("Source URL is empty")
		return "", fmt.Errorf("source URL is empty")
	}

	if t.ID == primitive.NilObjectID {
		log.Debug().Msg("Transcription ID is empty")
		return "", fmt.Errorf("transcription ID is empty")
	}

	goutubedl.Path = "yt-dlp"
	result, err := goutubedl.New(context.Background(), t.SourceUrl, goutubedl.Options{})
	if err != nil {
		log.Debug().Err(err).Msg("Error creating goutubedl")
		return "", err
	}

	downloadResult, err := result.Download(context.Background(), "best")
	if err != nil {
		log.Debug().Err(err).Msg("Error downloading media")
		return "", err
	}

	filename := fmt.Sprintf("%v%v%v", t.ID.Hex(), models.FileNameSeparator, result.Info.Title)
	filename = SanitizeFilename(filename)

	defer downloadResult.Close()
	f, err := os.Create(filepath.Join(os.Getenv("UPLOAD_DIR"), filename))
	if err != nil {
		log.Debug().Err(err).Msg("Error creating file")
		return "", err
	}
	defer f.Close()
	io.Copy(f, downloadResult)

	return filename, nil
}

func SendTranscriptionRequest(t *models.Transcription, body *bytes.Buffer, writer *multipart.Writer) (*models.WhisperResult, error) {
	url := fmt.Sprintf("http://%v/transcribe/?model_size=%v&task=%v&language=%v&device=%v&diarize=%v&num_speakers=%v", os.Getenv("ASR_ENDPOINT"), t.ModelSize, t.Task, t.Language, t.Device, t.Diarize, t.NumSpeakers)
	// Send transcription request to transcription service
	req, err := http.NewRequest("POST", url, body)
	if err != nil {
		log.Debug().Err(err).Msg("Error creating request to transcription service")
		return nil, err
	}

	req.Header.Set("Content-Type", writer.FormDataContentType())
	req.Header.Set("Accept", "application/json")
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		log.Debug().Err(err).Msg("Error sending request")
		return nil, err
	}
	defer resp.Body.Close()
	b, err := io.ReadAll(resp.Body)
	if err != nil {
		log.Debug().Err(err).Msg("Error reading response body")
		return nil, err
	}

	if resp.StatusCode != http.StatusOK {
		log.Debug().Msgf("Response from %v: %v", url, string(b))
		log.Debug().Err(err).Msgf("Invalid response status %v:", resp.StatusCode)
		return nil, errors.New("invalid status")
	}

	var asrResponse *models.WhisperResult
	if err := json.Unmarshal(b, &asrResponse); err != nil {
		log.Debug().Err(err).Msg("Error decoding response")
		return nil, err
	}

	return asrResponse, nil
}

func GetDuration(filePath string) (float64, error) {
	// ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 input.mp4
	cmd := exec.Command("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filePath)
	out, err := cmd.Output()
	if err != nil {
		return 0, err
	}
	durationStr := strings.TrimSpace(string(out))
	return strconv.ParseFloat(durationStr, 64)
}

func SplitFile(filePath string, segmentTime int) ([]string, error) {
	// ffmpeg -i input.mp3 -f segment -segment_time 600 -vn -acodec libmp3lame -ar 16000 -ac 1 output_%03d.mp3
	dir := filepath.Dir(filePath)
	baseName := filepath.Base(filePath)
	ext := ".mp3" // Standardize output to mp3
	nameWithoutExt := strings.TrimSuffix(baseName, filepath.Ext(baseName))

	// Pattern for output files
	outputPattern := filepath.Join(dir, fmt.Sprintf("%s_part_%%03d%s", nameWithoutExt, ext))

	// Transcoding to mono 16kHz mp3 ensures small chunks (around 5MB for 10min)
	// and broad compatibility with ASR services like Groq and Faster-Whisper.
	cmd := exec.Command("ffmpeg", "-i", filePath, "-f", "segment", "-segment_time", fmt.Sprintf("%d", segmentTime), "-vn", "-acodec", "libmp3lame", "-ar", "16000", "-ac", "1", outputPattern)

	var stderr bytes.Buffer
	cmd.Stderr = &stderr

	log.Info().Msgf("Splitting file %s into %d-second segments", filePath, segmentTime)
	if err := cmd.Run(); err != nil {
		log.Error().Msgf("FFmpeg error: %s", stderr.String())
		return nil, fmt.Errorf("ffmpeg error: %v", err)
	}

	// Find generated files
	matches, err := filepath.Glob(filepath.Join(dir, fmt.Sprintf("%s_part_*%s", nameWithoutExt, ext)))
	if err != nil {
		return nil, err
	}

	// Sort matches to ensure temporal order
	sort.Strings(matches)

	return matches, nil
}

func MergeTranscriptions(results []*models.WhisperResult, segmentTime float64) *models.WhisperResult {
	finalResult := &models.WhisperResult{
		Segments: []models.Segment{},
	}

	var totalDuration float64
	var fullText strings.Builder

	for i, res := range results {
		offset := float64(i) * segmentTime

		// Append text
		if i > 0 {
			fullText.WriteString(" ")
		}
		fullText.WriteString(res.Text)

		// Adjust and append segments
		for _, seg := range res.Segments {
			seg.Start += offset
			seg.End += offset

			// Adjust word timestamps if available
			for j := range seg.Words {
				seg.Words[j].Start += offset
				seg.Words[j].End += offset
			}

			finalResult.Segments = append(finalResult.Segments, seg)
		}

		// Duration might be slightly different than segmentTime for the last chunk
		// providing a more accurate total duration would be sum of all durations
		totalDuration += res.Duration

		// Use the language detected in the first chunk as the overall language
		if i == 0 {
			finalResult.Language = res.Language
		}
	}

	finalResult.Text = fullText.String()
	finalResult.Duration = totalDuration

	return finalResult
}
