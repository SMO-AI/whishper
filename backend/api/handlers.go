package api

import (
	"bytes"
	"fmt"
	"net/http"
	"os"
	"strconv"
	"time"

	"github.com/goccy/go-json"
	"github.com/gofiber/fiber/v2"
	"github.com/rs/zerolog/log"

	"codeberg.org/pluja/whishper/models"
)

func (s *Server) handleGetAllTranscriptions(c *fiber.Ctx) error {
	token := c.Get("Authorization")
	if len(token) > 7 && token[:7] == "Bearer " {
		token = token[7:]
	} else {
		return fiber.NewError(fiber.StatusUnauthorized, "Unauthorized")
	}

	user, err := ValidateToken(token)
	if err != nil {
		log.Error().Err(err).Msg("Invalid token")
		return fiber.NewError(fiber.StatusUnauthorized, "Unauthorized")
	}

	// Check if user is active
	active, err := CheckUserActive(token, user.ID)
	if err != nil {
		log.Error().Err(err).Msg("Error checking user active status")
		return fiber.NewError(fiber.StatusInternalServerError, "Internal Server Error")
	}
	if !active {
		return fiber.NewError(fiber.StatusForbidden, "Subscription required")
	}

	transcriptions := s.Db.GetAllTranscriptions(user.ID)

	// Convert the transcriptions to JSON.
	json, err := json.Marshal(transcriptions)
	if err != nil {
		// 503 On vacation!
		return fiber.NewError(fiber.StatusServiceUnavailable, "On vacation!")
	}

	// Write the JSON to the response body.
	c.Set("Content-Type", "application/json")
	c.Write(json)
	return nil
}

func (s *Server) handleGetTranscriptionById(c *fiber.Ctx) error {
	token := c.Get("Authorization")
	if len(token) > 7 && token[:7] == "Bearer " {
		token = token[7:]
	} else {
		return fiber.NewError(fiber.StatusUnauthorized, "Unauthorized")
	}

	user, err := ValidateToken(token)
	if err != nil {
		return fiber.NewError(fiber.StatusUnauthorized, "Unauthorized")
	}

	id := c.Params("id")
	t := s.Db.GetTranscription(id)
	if t == nil {
		log.Warn().Msgf("Transcription with id %v not found", id)
		return fiber.NewError(fiber.StatusNotFound, "Not found")
	}

	if t.UserID != user.ID {
		return fiber.NewError(fiber.StatusForbidden, "Forbidden")
	}

	// Convert the transcription to JSON.
	json, err := json.Marshal(t)
	if err != nil {
		// 503 On vacation!
		return fiber.NewError(fiber.StatusServiceUnavailable, "On vacation!")
	}

	// Write the JSON to the response body.
	c.Set("Content-Type", "application/json")
	c.Write(json)
	return nil
}

// This function receives data from a form to create a new transcription.
// If the transcription is created successfully, it returns a 201 Created status code and
// broadcasts the new transcription to all ws clients.
func (s *Server) handlePostTranscription(c *fiber.Ctx) error {
	log.Debug().Msg("POST /api/transcriptions")

	token := c.Get("Authorization")
	if len(token) > 7 && token[:7] == "Bearer " {
		token = token[7:]
	} else {
		return fiber.NewError(fiber.StatusUnauthorized, "Unauthorized")
	}

	user, err := ValidateToken(token)
	if err != nil {
		return fiber.NewError(fiber.StatusUnauthorized, "Unauthorized")
	}

	// Check if user is active
	active, err := CheckUserActive(token, user.ID)
	if err != nil {
		log.Error().Err(err).Msg("Error checking user active status")
		return fiber.NewError(fiber.StatusInternalServerError, "Internal Server Error")
	}
	if !active {
		return fiber.NewError(fiber.StatusForbidden, "Subscription required")
	}

	var transcription models.Transcription
	transcription.UserID = user.ID

	// we get the filename from the from
	var filename string
	if c.FormValue("sourceUrl") == "" {
		// Get the form file from the request.
		file, err := c.FormFile("file")
		if err != nil {
			log.Error().Err(err).Msg("Error getting file field from the form")
			return fiber.NewError(fiber.StatusBadRequest, "Bad request")
		}
		timeid := time.Now().Format("2006_01_02-150405000")
		filename = timeid + models.FileNameSeparator + file.Filename
		// if it's empty and there is no sourceurl we set a timestamp-based filename
		if filename == timeid+models.FileNameSeparator {
			filename = timeid + models.FileNameSeparator + time.Now().Format("2006_01_02-150405")
		}

		// Save the file to the uploads directory.
		err = c.SaveFile(file, fmt.Sprintf("%v/%v", os.Getenv("UPLOAD_DIR"), filename))
		if err != nil {
			log.Error().Err(err).Msgf("Error saving the form file to disk into %v", os.Getenv("UPLOAD_DIR"))
			return fiber.NewError(fiber.StatusInternalServerError, "Internal server error")
		}
	}

	// Parse the body into the transcription struct.
	transcription.Language = c.FormValue("language")
	transcription.ModelSize = c.FormValue("modelSize")
	transcription.FileName = filename
	transcription.Status = models.TranscriptionStatusPending
	transcription.Diarize = c.FormValue("diarize") == "true"
	if numSpeakers := c.FormValue("numSpeakers"); numSpeakers != "" {
		if n, err := strconv.Atoi(numSpeakers); err == nil {
			transcription.NumSpeakers = n
		}
	}
	transcription.Task = c.FormValue("task")
	if transcription.Task == "" {
		transcription.Task = "transcribe"
	}
	transcription.SourceUrl = c.FormValue("sourceUrl")
	transcription.Device = c.FormValue("device")
	if transcription.Device != "cpu" && transcription.Device != "cuda" {
		log.Warn().Msgf("Device %v not supported, using cpu", transcription.Device)
		transcription.Device = "cpu"
	}

	log.Debug().Msgf("Transcription: %+v", transcription)
	// Save transcription to database
	res, err := s.Db.NewTranscription(&transcription)
	if err != nil {
		log.Error().Err(err).Msg("Error saving transcription to database")
		return fiber.NewError(fiber.StatusInternalServerError, "Internal server error")
	}

	// Broadcast transcription to websocket clients
	s.BroadcastTranscription(res)
	s.NewTranscriptionCh <- true

	// Convert the transcription to JSON.
	json, err := json.Marshal(res)
	if err != nil {
		// 503 On vacation!
		return fiber.NewError(fiber.StatusServiceUnavailable, "On vacation!")
	}

	// Write the JSON to the response body.
	c.Set("Content-Type", "application/json")
	c.Write(json)
	return nil
}

func (s *Server) handleDeleteTranscription(c *fiber.Ctx) error {
	token := c.Get("Authorization")
	if len(token) > 7 && token[:7] == "Bearer " {
		token = token[7:]
	} else {
		return fiber.NewError(fiber.StatusUnauthorized, "Unauthorized")
	}

	user, err := ValidateToken(token)
	if err != nil {
		return fiber.NewError(fiber.StatusUnauthorized, "Unauthorized")
	}

	// First get the transcription from the database
	id := c.Params("id")
	t := s.Db.GetTranscription(id)
	if t == nil {
		log.Warn().Msgf("Transcription with id %v not found", id)
		return fiber.NewError(fiber.StatusNotFound, "Not found")
	}

	if t.UserID != user.ID {
		return fiber.NewError(fiber.StatusForbidden, "Forbidden")
	}

	// Then delete the file from disk
	err = os.Remove(fmt.Sprintf("%v/%v", os.Getenv("UPLOAD_DIR"), t.FileName))
	if err != nil {
		log.Error().Err(err).Msgf("Error deleting file %v", t.FileName)
	}

	// Finally delete the transcription from the database
	err = s.Db.DeleteTranscription(id)
	if err != nil {
		log.Error().Err(err).Msgf("Error deleting transcription %v", id)
		return fiber.NewError(fiber.StatusInternalServerError, "Internal server error")
	}

	// Return status deleted
	c.Status(fiber.StatusOK)
	return nil
}

func (s *Server) handlePatchTranscription(c *fiber.Ctx) error {
	var transcription models.Transcription
	// Parse the body into the transcription struct.
	err := json.Unmarshal(c.Body(), &transcription)
	if err != nil {
		log.Error().Err(err).Msg("Error parsing JSON body")
		return fiber.NewError(fiber.StatusBadRequest, "Bad request")
	}

	// Update the transcription in the database
	ut, err := s.Db.UpdateTranscription(&transcription)
	if err != nil {
		log.Error().Err(err).Msgf("Error updating transcription")
		if err.Error() == "no documents were modified" {
			return fiber.NewError(fiber.StatusNotModified, "Not found")
		}
		return fiber.NewError(fiber.StatusInternalServerError, "Internal server error")
	}

	// Write the JSON to the response body.
	s.BroadcastTranscription(ut)

	// Return status ok
	json, err := json.Marshal(&ut)
	if err != nil {
		// 503 On vacation!
		return fiber.NewError(fiber.StatusInternalServerError, "Error parsing json!")
	}

	c.Status(fiber.StatusOK)
	c.Write(json)
	return nil
}

func (s *Server) handleTranslate(c *fiber.Ctx) error {
	token := c.Get("Authorization")
	if len(token) > 7 && token[:7] == "Bearer " {
		token = token[7:]
	} else {
		return fiber.NewError(fiber.StatusUnauthorized, "Unauthorized")
	}

	user, err := ValidateToken(token)
	if err != nil {
		return fiber.NewError(fiber.StatusUnauthorized, "Unauthorized")
	}

	id := c.Params("id")
	targetLang := c.Params("target")

	transcription := s.Db.GetTranscription(id)
	if transcription == nil {
		return fiber.NewError(fiber.StatusNotFound, "Not found")
	}

	if transcription.UserID != user.ID {
		return fiber.NewError(fiber.StatusForbidden, "Forbidden")
	}

	// Set status as translating
	transcription.Status = models.TrannscriptionStatusTranslating
	s.Db.UpdateTranscription(transcription)
	s.BroadcastTranscription(transcription)

	err = transcription.Translate(targetLang)
	if err != nil {
		log.Debug().Err(err).Msg("Error with translation")
		return err
	}

	// Set as done
	transcription.Status = models.TranscriptionStatusDone
	s.Db.UpdateTranscription(transcription)
	s.BroadcastTranscription(transcription)
	return nil
}

func (s *Server) handleDownloadFile(c *fiber.Ctx) error {
	token := c.Get("Authorization")
	if len(token) > 7 && token[:7] == "Bearer " {
		token = token[7:]
	} else {
		return fiber.NewError(fiber.StatusUnauthorized, "Unauthorized")
	}

	user, err := ValidateToken(token)
	if err != nil {
		return fiber.NewError(fiber.StatusUnauthorized, "Unauthorized")
	}

	filename := c.Params("filename")
	if filename == "" {
		return fiber.NewError(fiber.StatusBadRequest, "Bad Request")
	}

	// Security: Prevent path traversal
	if filename == "." || filename == ".." || filename[0] == '/' || filename[0] == '\\' {
		return fiber.NewError(fiber.StatusForbidden, "Forbidden")
	}

	// We need to check if the file belongs to the user.
	// Since we don't have an easy lookup by filename in DB interface, we have to iterate or add a method.
	// Adding GetTranscriptionByFilename to DB interface is better, but for now we iterate (inefficient but safe) or trust the filename structure if it contains user ID?
	// Filename structure: timeid_WHSHPR_filename. It doesn't contain UserID.
	// So we must look up in DB.

	// Ideally execute a finding query.
	// For now, let's implement GetTranscriptionByFilename or similar.
	// Or use GetAllTranscriptions(userID) and check if filename is in there.

	transcriptions := s.Db.GetAllTranscriptions(user.ID)
	found := false
	for _, t := range transcriptions {
		if t.FileName == filename {
			found = true
			break
		}
	}

	if !found {
		// Try pending?
		pending := s.Db.GetPendingTranscriptions()
		for _, t := range pending {
			if t.UserID == user.ID && t.FileName == filename {
				found = true
				break
			}
		}
	}

	if !found {
		return fiber.NewError(fiber.StatusForbidden, "Forbidden")
	}

	filepath := fmt.Sprintf("%v/%v", os.Getenv("UPLOAD_DIR"), filename)
	return c.SendFile(filepath)
}
func (s *Server) handlePostDiarize(c *fiber.Ctx) error {
	token := c.Get("Authorization")
	if len(token) > 7 && token[:7] == "Bearer " {
		token = token[7:]
	} else {
		return fiber.NewError(fiber.StatusUnauthorized, "Unauthorized")
	}

	user, err := ValidateToken(token)
	if err != nil {
		return fiber.NewError(fiber.StatusUnauthorized, "Unauthorized")
	}

	id := c.Params("id")
	transcription := s.Db.GetTranscription(id)
	if transcription == nil {
		return fiber.NewError(fiber.StatusNotFound, "Not found")
	}

	if transcription.UserID != user.ID {
		return fiber.NewError(fiber.StatusForbidden, "Forbidden")
	}

	var body struct {
		NumSpeakers int `json:"num_speakers"`
	}
	if err := c.BodyParser(&body); err != nil {
		return fiber.NewError(fiber.StatusBadRequest, "Invalid request body")
	}

	// Prepare request to Python service
	pythonDiarizeURL := fmt.Sprintf("http://%v/diarize/", os.Getenv("ASR_ENDPOINT"))

	payload := map[string]interface{}{
		"segments":     transcription.Result.Segments,
		"num_speakers": body.NumSpeakers,
	}

	jsonPayload, _ := json.Marshal(payload)

	// Create request
	req, _ := http.NewRequest("POST", pythonDiarizeURL, bytes.NewBuffer(jsonPayload))
	req.Header.Set("Content-Type", "application/json")
	if token != "" {
		req.Header.Set("Authorization", "Bearer "+token)
	}

	client := &http.Client{Timeout: 60 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		log.Error().Err(err).Msg("Error calling Python diarize endpoint")
		return fiber.NewError(fiber.StatusInternalServerError, "Internal Server Error")
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		log.Error().Int("status", resp.StatusCode).Msg("Python diarize endpoint returned non-200")
		return fiber.NewError(fiber.StatusInternalServerError, "Diarization failed")
	}

	var diarizeResult struct {
		Segments []models.Segment `json:"segments"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&diarizeResult); err != nil {
		return fiber.NewError(fiber.StatusInternalServerError, "Error decoding result")
	}

	// Update segments in transcription
	transcription.Result.Segments = diarizeResult.Segments

	// Save to DB
	ut, err := s.Db.UpdateTranscription(transcription)
	if err != nil {
		return fiber.NewError(fiber.StatusInternalServerError, "Error saving to database")
	}

	s.BroadcastTranscription(ut)
	return c.JSON(ut)
}
