package api

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
)

type SupabaseUser struct {
	ID    string `json:"id"`
	Email string `json:"email"`
}

type WhishperProfile struct {
	Status string `json:"status"`
}

func ValidateToken(token string) (*SupabaseUser, error) {
	supabaseUrl := os.Getenv("SUPABASE_URL")
	apiKey := os.Getenv("SUPABASE_ANON_KEY")

	if supabaseUrl == "" || apiKey == "" {
		return nil, fmt.Errorf("Supabase configuration missing")
	}

	req, err := http.NewRequest("GET", fmt.Sprintf("%s/auth/v1/user", supabaseUrl), nil)
	if err != nil {
		return nil, err
	}

	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("apikey", apiKey)

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return nil, fmt.Errorf("invalid token")
	}

	var user SupabaseUser
	if err := json.NewDecoder(resp.Body).Decode(&user); err != nil {
		return nil, err
	}

	return &user, nil
}

func CheckUserActive(token string, userID string) (bool, error) {
	supabaseUrl := os.Getenv("SUPABASE_URL")
	apiKey := os.Getenv("SUPABASE_ANON_KEY")

	req, err := http.NewRequest("GET", fmt.Sprintf("%s/rest/v1/whishper_profiles?select=status&id=eq.%s", supabaseUrl, userID), nil)
	if err != nil {
		return false, err
	}

	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("apikey", apiKey)

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return false, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return false, fmt.Errorf("failed to fetch profile")
	}

	var profiles []WhishperProfile
	if err := json.NewDecoder(resp.Body).Decode(&profiles); err != nil {
		return false, err
	}

	if len(profiles) == 0 {
		return false, fmt.Errorf("profile not found")
	}

	return profiles[0].Status == "active", nil
}

// SupabaseSyncTranscription sends a transcription record to Supabase
func SupabaseSyncTranscription(t map[string]interface{}) error {
	supabaseUrl := os.Getenv("SUPABASE_URL")
	apiKey := os.Getenv("SUPABASE_ANON_KEY")
	if supabaseUrl == "" || apiKey == "" {
		return nil // Skip if not configured
	}

	jsonData, _ := json.Marshal(t)
	req, err := http.NewRequest("POST", fmt.Sprintf("%s/rest/v1/whishper_transcriptions", supabaseUrl), bytes.NewBuffer(jsonData))
	if err != nil {
		return err
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("apikey", apiKey)
	req.Header.Set("Authorization", "Bearer "+apiKey)
	req.Header.Set("Prefer", "resolution=merge-duplicates") // UPSERT equivalent

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		return fmt.Errorf("supabase error: %v", resp.Status)
	}
	return nil
}

// SupabaseSyncUsage sends a usage log record to Supabase
func SupabaseSyncUsage(l map[string]interface{}) error {
	supabaseUrl := os.Getenv("SUPABASE_URL")
	apiKey := os.Getenv("SUPABASE_ANON_KEY")
	if supabaseUrl == "" || apiKey == "" {
		return nil
	}

	jsonData, _ := json.Marshal(l)
	req, err := http.NewRequest("POST", fmt.Sprintf("%s/rest/v1/whishper_usage_logs", supabaseUrl), bytes.NewBuffer(jsonData))
	if err != nil {
		return err
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("apikey", apiKey)
	req.Header.Set("Authorization", "Bearer "+apiKey)

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	return nil
}
