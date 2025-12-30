# First UV Pro API

A small FastAPI demonstration API.

## Deployment

This repo includes:

- `Dockerfile` — builds a small container image for `main:app`.
- `.github/workflows/build-and-push-image.yml` — GitHub Actions workflow that builds and pushes the Docker image to GitHub Container Registry (GHCR) on pushes to `main`.

Quick deploy options:

- Render / Fly / Railway: connect your GitHub repo and use the `Dockerfile` or `Procfile` (`web: uvicorn main:app --host 0.0.0.0 --port $PORT`). These platforms will provide a public URL automatically.
- Google Cloud Run: build/push the image (or use the Actions workflow), then deploy to Cloud Run and set the container port to the value of `PORT` env var (commonly 8080).

Notes:
- For production, use a persistent database (Postgres) and set secrets via environment variables instead of committing them.
- The app reads `HOST`, `PORT`, `UVICORN_RELOAD`, and `LOG_LEVEL` environment variables for runtime configuration.

## Deploying to Google Cloud Run ☁️

This repo includes a GitHub Actions workflow (`.github/workflows/deploy-cloud-run.yml`) that builds the container using Cloud Build and deploys to Cloud Run on pushes to `main`.

Required GitHub repository secrets (create in Settings → Secrets → Actions):

- `GCP_SA_KEY` — JSON service account key (full JSON content). The service account must have permissions for Cloud Build, Cloud Run Admin, and Service Account User.
- `GCP_PROJECT_ID` — your GCP project ID.
- `CLOUD_RUN_SERVICE` — the name of the Cloud Run service to deploy to (will be created if missing).
- `CLOUD_RUN_REGION` — the region for Cloud Run (e.g., `us-central1`).

Manual deploy steps (alternatively):

1. Build and push the image locally:
   ```bash
   gcloud builds submit --tag gcr.io/<PROJECT_ID>/first-uv-pro:latest
   ```
2. Deploy to Cloud Run:
   ```bash
   gcloud run deploy <SERVICE_NAME> --image gcr.io/<PROJECT_ID>/first-uv-pro:latest --region <REGION> --platform managed --allow-unauthenticated
   ```


