# Coolify Environment Configuration Guide

To enable the new Diarization features (Pyannote + Faster Whisper), you need to add the **Hugging Face Token** to your Coolify environment variables.

## Steps

1.  **Login to Coolify**: Access your Coolify dashboard.
2.  **Navigate to Project**: Open the project where `scriptus-app` (or your Whishper instance) is deployed.
3.  **Select Service**: Click on the `scriptus-app` service.
4.  **Configuration / Environment Variables**:
    *   Find the **Environment Variables** tab (sometimes labeled "Env").
    *   Click **Add New Variable** (or "Edit Environment Variables").
5.  **Add the Token**:
    *   **Key**: `HF_TOKEN`
    *   **Value**: `hf_...` (Insert your actual token here)
6.  **Save & Redeploy**:
    *   Click **Save**.
    *   Click **Redeploy** (or "Deploy") to apply the changes. The container needs to restart to pick up the new variable.

## Verification

After redeployment:
1.  Upload a file for transcription.
2.  Ensure you select "Diarization" (or pass `diarize=true` in the API).
3.  Check the logs if it fails; you should see "Running Pyannote Diarization...".
