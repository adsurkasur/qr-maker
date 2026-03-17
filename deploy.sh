#!/bin/bash
set -e
echo "Pulling latest changes..."
git pull origin main
echo "Rebuilding Docker image..."
docker compose build --no-cache
echo "Restarting service..."
docker compose up -d
echo "Checking health..."
sleep 10
docker compose ps
echo "Done. Logs:"
docker compose logs --tail=20