#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Check that WEATHER_API_KEY is set (either from env or docker run --env)
if [ -z "$API_KEY" ]; then
  echo "❌ ERROR: API_KEY is not set. Please pass it as an environment variable."
  exit 1
fi

# Clone or pull the latest repo
if [ ! -d "$WORKDIR/data/website" ]; then
  git clone "$REPO_URL" "$WORKDIR/data/website"
else
  cd "$WORKDIR/data/website" && GIT_DISCOVERY_ACROSS_FILESYSTEM=1 git pull origin main
fi

cd "$WORKDIR/data/website" || exit


# Create .env file from the environment
echo "API_KEY=${API_KEY}" > .env
echo $TRACKING_KEY > tracking.html

# Create tracking.html if not exists
if [ ! -f "tracking.html" ]; then
  echo "<!-- Tracking script goes here -->" > tracking.html
fi

# Start Python HTTP server
echo "✅ Starting server on port 8000..."
python3 ./generate_weather_json.py
