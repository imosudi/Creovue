#!/bin/bash

# Create Matplotlib cache directory with proper permissions
echo "Setting up Matplotlib cache directory..."
CACHE_DIR="/tmp/mpl_cache"

# Create directory if it doesn't exist
sudo mkdir -p "$CACHE_DIR"

# Set ownership to www-data (common web server user)
sudo chown www-data:www-data "$CACHE_DIR"

# Set permissions (rwx for owner, rx for group/others)
sudo chmod 755 "$CACHE_DIR"

# Verify the setup
if [ -d "$CACHE_DIR" ] && [ -w "$CACHE_DIR" ]; then
    echo "✅ Matplotlib cache directory setup successfully at $CACHE_DIR"
else
    echo "❌ Failed to setup Matplotlib cache directory"
    exit 1
fi

# Set environment variable for current session
export MPLCONFIGDIR="$CACHE_DIR"
echo "Environment variable MPLCONFIGDIR set to $MPLCONFIGDIR"