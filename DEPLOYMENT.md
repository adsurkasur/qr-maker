# Local Docker Deployment Guide

## Prerequisites

- Ubuntu Server machine (for example HP Thin Client T530)
- Docker installed
- Docker Compose installed (`docker compose` command available)
- Git installed

## Initial Setup

1. Clone the repository:

   ```bash
   git clone <your-repo-url>
   cd qr-maker
   ```

2. Create your local environment file:

   ```bash
   cp .env.example .env
   ```

3. Edit `.env` and set real values for:
- `QR_API_KEY`
- `FLASK_SECRET_KEY`
- `ALLOWED_ORIGINS`
- `PORT` (keep as `7860` unless you intentionally change mapping)

## Run the Service

Start in detached mode:

```bash
docker compose up -d
```

## Check Logs

```bash
docker compose logs -f qr-api
```

## Update Deployment

Use the provided script:

```bash
./deploy.sh
```

## Cloudflare Tunnel Note

Cloudflare Tunnel configuration is separate and is not managed in this repository.