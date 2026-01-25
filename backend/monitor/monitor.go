package monitor

import (
	"bytes"
	"fmt"
	"io"
	"mime/multipart"
	"os"
	"path/filepath"
	"sync"
	"time"

	"github.com/rs/zerolog/log"

	"codeberg.org/pluja/whishper/api"
	"codeberg.org/pluja/whishper/models"
	"codeberg.org/pluja/whishper/utils"
)

func StartMonitor(s *api.Server) {
	log.Info().Msg("Starting monitor!")
	go func() {
		for {
			// Wait for new transcription to be added to the database
			// notification will be received through the NewTranscriptionCh channel
			<-s.NewTranscriptionCh
			pendingTranscriptions := s.Db.GetPendingTranscriptions()
			log.Debug().Msgf("Pending transcriptions: %v", len(pendingTranscriptions))
			for _, pt := range pendingTranscriptions {
				log.Debug().Msgf("Taking pending transcription %v", pt.ID)
				if pt.Status == models.TranscriptionStatusPending {
					err := transcribe(s, pt)
					if err != nil {
						log.Error().Err(err).Msg("Error transcribing")
						pt.Status = models.TranscriptionStatusError
						ut, err := s.Db.UpdateTranscription(pt)
						if err != nil {
							log.Error().Err(err).Msg("Error updating transcription")
						}
						s.BroadcastTranscription(ut)
						continue
					}
				}
			}
		}
	}()
}

func transcribe(s *api.Server, t *models.Transcription) error {
	// Update transcription status
	t.Status = models.TranscriptionStatusRunning
	log.Debug().Msgf("Updating transcription %v", t)
	_, err := s.Db.UpdateTranscription(t)
	if err != nil {
		log.Error().Err(err).Msg("Error updating transcription")
		return err
	}
	s.BroadcastTranscription(t)

	if t.SourceUrl != "" {
		// Download media
		fn, err := utils.DownloadMedia(t)
		if err != nil {
			log.Error().Err(err).Msg("Error downloading media")
			return err
		}
		t.FileName = fn
		s.BroadcastTranscription(t)
	}

	// Check file size/duration
	uploadDir := os.Getenv("UPLOAD_DIR")
	filePath := filepath.Join(uploadDir, t.FileName)
	fileInfo, err := os.Stat(filePath)
	if err != nil {
		log.Error().Err(err).Msg("Error stating file")
		return err
	}

	// Threshold: 19MB (to be safe under 20MB limit if any)
	// OR duration > 10m? Let's stick to size for now as that's the reported issue.
	const maxFileSize = 19 * 1024 * 1024 // 19MB

	if fileInfo.Size() > maxFileSize {
		log.Info().Msgf("File %s is larger than %d bytes, processing in chunks", t.FileName, maxFileSize)
		return processLargeTranscription(s, t)
	}

	// Prepare multipart form data
	body, writer, err := prepareMultipartFormData(t)
	if err != nil {
		log.Error().Err(err).Msg("Error preparing multipart form data")
		return err
	}

	// Send transcription request to transcription service
	res, err := utils.SendTranscriptionRequest(t, body, writer)
	if err != nil {
		log.Error().Err(err).Msg("Error sending transcription request")
		return err
	}

	t.Result = *res
	t.Translations = []models.Translation{}
	t.Status = models.TranscriptionStatusDone
	_, err = s.Db.UpdateTranscription(t)
	if err != nil {
		log.Error().Err(err).Msg("Error updating transcription")
		return err
	}

	// Calculate cost for analytical tracking
	// Estimated prices for Groq/Providers (can be adjusted)
	ratePerMinute := 0.001 // Default: $0.06 per hour
	if t.ModelSize == "groq:whisper-large-v3-turbo" {
		ratePerMinute = 0.0007 // $0.042 per hour
	} else if t.ModelSize == "groq:whisper-large-v3" {
		ratePerMinute = 0.0012 // $0.072 per hour
	}
	cost := (t.Result.Duration / 60.0) * ratePerMinute

	// Final sync to Supabase
	go func() {
		// Sync Transcription
		err := api.SupabaseSyncTranscription(map[string]interface{}{
			"id":         t.ID.Hex(),
			"user_id":    t.UserID,
			"text":       t.Result.Text,
			"duration":   t.Result.Duration,
			"language":   t.Result.Language,
			"model":      t.ModelSize,
			"created_at": time.Now(),
		})
		if err != nil {
			log.Error().Err(err).Msg("Error syncing transcription to Supabase")
		}

		// Sync Usage Log
		err = api.SupabaseSyncUsage(map[string]interface{}{
			"user_id":          t.UserID,
			"transcription_id": t.ID.Hex(),
			"usage_type":       "transcription",
			"amount":           t.Result.Duration,
			"cost":             cost,
			"details": map[string]interface{}{
				"model": t.ModelSize,
			},
			"created_at": time.Now(),
		})
		if err != nil {
			log.Error().Err(err).Msg("Error syncing usage log to Supabase")
		}
	}()

	s.BroadcastTranscription(t)
	return nil
}

func processLargeTranscription(s *api.Server, t *models.Transcription) error {
	uploadDir := os.Getenv("UPLOAD_DIR")
	filePath := filepath.Join(uploadDir, t.FileName)

	// Split file into 10-minute segments
	segmentTime := 600
	chunks, err := utils.SplitFile(filePath, segmentTime)
	if err != nil {
		log.Error().Err(err).Msg("Error splitting file")
		return err
	}
	defer func() {
		for _, chunk := range chunks {
			if err := os.Remove(chunk); err != nil {
				log.Warn().Err(err).Msgf("Failed to cleanup chunk: %s", chunk)
			}
		}
	}()

	results := make([]*models.WhisperResult, len(chunks))
	errs := make([]error, len(chunks))

	var wg sync.WaitGroup
	// Concurrency level (tuned for typical resource constraints)
	concurrencyLimit := 3
	semaphore := make(chan struct{}, concurrencyLimit)

	log.Info().Msgf("Starting parallel processing of %d chunks with concurrency %d", len(chunks), concurrencyLimit)

	for i, chunkPath := range chunks {
		wg.Add(1)
		go func(idx int, path string) {
			defer wg.Done()
			semaphore <- struct{}{}
			defer func() { <-semaphore }()

			log.Debug().Msgf("Transcribing chunk %d/%d: %s", idx+1, len(chunks), path)

			chunkFileName := filepath.Base(path)
			chunkTrans := &models.Transcription{
				ModelSize: t.ModelSize,
				Language:  t.Language,
				Device:    t.Device,
				Task:      t.Task,
				FileName:  chunkFileName,
			}

			body, writer, err := prepareMultipartFormData(chunkTrans)
			if err != nil {
				errs[idx] = fmt.Errorf("chunk %d: form prep error: %v", idx, err)
				return
			}

			res, err := utils.SendTranscriptionRequest(chunkTrans, body, writer)
			if err != nil {
				log.Error().Err(err).Msgf("Failed to process chunk %d", idx)
				errs[idx] = fmt.Errorf("chunk %d: API error: %v", idx, err)
				return
			}

			results[idx] = res
		}(i, chunkPath)
	}

	wg.Wait()

	// Aggregate errors
	var combinedErr error
	for _, e := range errs {
		if e != nil {
			if combinedErr == nil {
				combinedErr = e
			} else {
				combinedErr = fmt.Errorf("%v; %v", combinedErr, e)
			}
		}
	}

	if combinedErr != nil {
		return combinedErr
	}

	// Merge all transcription segments
	log.Info().Msg("Merging chunk results...")
	finalRes := utils.MergeTranscriptions(results, float64(segmentTime))

	t.Result = *finalRes
	t.Translations = []models.Translation{}
	t.Status = models.TranscriptionStatusDone
	_, err = s.Db.UpdateTranscription(t)
	if err != nil {
		log.Error().Err(err).Msg("Error finalizing transcription in DB")
		return err
	}

	s.BroadcastTranscription(t)
	log.Info().Msgf("Successfully processed large transcription: %s", t.FileName)

	// Calculate cost for analytical tracking - LARGE FILES
	ratePerMinute := 0.001 // Default: $0.06 per hour
	if t.ModelSize == "groq:whisper-large-v3-turbo" {
		ratePerMinute = 0.0007 // $0.042 per hour
	} else if t.ModelSize == "groq:whisper-large-v3" {
		ratePerMinute = 0.0012 // $0.072 per hour
	}
	cost := (t.Result.Duration / 60.0) * ratePerMinute

	// Final sync to Supabase for Large Files
	go func() {
		// Sync Transcription
		err := api.SupabaseSyncTranscription(map[string]interface{}{
			"id":         t.ID.Hex(),
			"user_id":    t.UserID,
			"text":       t.Result.Text,
			"duration":   t.Result.Duration,
			"language":   t.Result.Language,
			"model":      t.ModelSize,
			"created_at": time.Now(),
		})
		if err != nil {
			log.Error().Err(err).Msg("Error syncing large transcription to Supabase")
		}

		// Sync Usage Log
		err = api.SupabaseSyncUsage(map[string]interface{}{
			"user_id":          t.UserID,
			"transcription_id": t.ID.Hex(),
			"usage_type":       "transcription",
			"amount":           t.Result.Duration,
			"cost":             cost,
			"details": map[string]interface{}{
				"model": t.ModelSize,
			},
			"created_at": time.Now(),
		})
		if err != nil {
			log.Error().Err(err).Msg("Error syncing large transcription usage to Supabase")
		}
	}()

	return nil
}

func prepareMultipartFormData(t *models.Transcription) (*bytes.Buffer, *multipart.Writer, error) {
	body := &bytes.Buffer{}
	writer := multipart.NewWriter(body)

	part, err := writer.CreateFormFile("file", t.FileName)
	if err != nil {
		log.Error().Err(err).Msg("Error creating form file")
		return nil, nil, err
	}

	// Read file from disk
	filePath := filepath.Join(os.Getenv("UPLOAD_DIR"), t.FileName)
	file, err := os.Open(filePath)
	if err != nil {
		log.Error().Err(err).Msg("Error opening file")
		return nil, nil, err
	}
	defer file.Close()

	_, err = io.Copy(part, file)
	if err != nil {
		log.Error().Err(err).Msg("Error copying file")
		return nil, nil, err
	}

	err = writer.Close()
	if err != nil {
		log.Error().Err(err).Msg("Error closing writer")
		return nil, nil, err
	}

	return body, writer, nil
}
