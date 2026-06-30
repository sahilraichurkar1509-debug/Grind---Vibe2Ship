Deployment notes — Vibe2Ship

This document shows quick steps to deploy the Docker image produced by the GitHub Actions workflow (pushed to GHCR) to two example platforms: Google Cloud (AI/Studio / Cloud Run) and Antigravity.

1) Build & publish (already configured in `.github/workflows/ci-docker.yml`)
   - On push to `main`, the image is built and pushed to `ghcr.io/<OWNER>/vibe2ship:latest`.

2) Google Cloud / AI Studio (container image)
   - Ensure you have a Google Cloud project and `gcloud` authenticated.
   - Example deploy to Cloud Run:

```bash
# pull image locally (optional)
docker pull ghcr.io/<OWNER>/vibe2ship:latest

# deploy to Cloud Run
gcloud run deploy vibe2ship \
  --image=ghcr.io/<OWNER>/vibe2ship:latest \
  --platform=managed \
  --region=us-central1 \
  --allow-unauthenticated
```

3) Antigravity
   - Antigravity accepts container images; consult Antigravity docs for exact deploy steps.
   - Typical flow: create an app in Antigravity UI, point it to `ghcr.io/<OWNER>/vibe2ship:latest`, set port `8000` and start.

4) Pulling the image manually
```bash
docker login ghcr.io
docker pull ghcr.io/<OWNER>/vibe2ship:latest
docker run -p 8000:8000 ghcr.io/<OWNER>/vibe2ship:latest
```

Notes
- Replace `<OWNER>` with your GitHub username or organization.
- For private GHCR images, configure authentication (Personal Access Token) as needed on the target platform.
- The image exposes a FastAPI app on port 8000 and serves `grind.html` at `/`.

## Automated Cloud Run deployment from GitHub Actions

The repository includes `.github/workflows/deploy-cloudrun.yml` which deploys the published GHCR image to Cloud Run when you push to `main`.

Prerequisites (one-time):

1. Create a Google Cloud service account and grant roles:

```bash
gcloud iam service-accounts create gha-deployer --display-name "GitHub Actions Deployer"
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
   --member "serviceAccount:gha-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
   --role roles/run.admin
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
   --member "serviceAccount:gha-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
   --role roles/iam.serviceAccountUser
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
   --member "serviceAccount:gha-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
   --role roles/storage.admin
```

2. Create and download a key for that service account (JSON):

```bash
gcloud iam service-accounts keys create sa-key.json \
   --iam-account gha-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

3. Add two repository secrets on GitHub: `GCP_SA_KEY` (contents of `sa-key.json`), `GCP_PROJECT_ID` (your project id), and `GCP_REGION` (e.g. `us-central1`).

Use the GitHub UI: Settings → Secrets → Actions → New repository secret. Paste the JSON for `GCP_SA_KEY`.

4. Push to `main` — the `ci-docker.yml` will build and push the image to GHCR, then `deploy-cloudrun.yml` will deploy that image to Cloud Run.

Notes:
- Replace `YOUR_PROJECT_ID` with your real GCP project id in the commands above.
- If you prefer to use Artifact Registry or Container Registry, adjust the workflow image reference accordingly.
