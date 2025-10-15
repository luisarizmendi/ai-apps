#!/bin/bash
set -euo pipefail

FORCE_DOWNLOAD="${FORCE_DOWNLOAD:-false}"

IMAGE_NAME="${1:-${IMAGE_NAME:-}}"
if [ -z "$IMAGE_NAME" ]; then
    echo "Error: No image specified. Pass it as an argument or set IMAGE_NAME."
    exit 1
fi

# File to store the last downloaded image digest
SOURCE_DIR="${SOURCE_DIR:-/models}"
DIGEST_DIR="${DIGEST_DIR:-/models}"
DIGEST_FILE="${DIGEST_DIR}/.last_image_digest"

# Get the current image digest from the registry
echo "Checking for updates to ${IMAGE_NAME}..."
CURRENT_DIGEST=$(podman inspect --format='{{.Digest}}' ${IMAGE_NAME} 2>/dev/null || echo "")

# If we couldn't get digest from local image, pull it to get the latest digest
if [ -z "$CURRENT_DIGEST" ]; then
    echo "Image not found locally, pulling to check digest..."
    podman pull ${IMAGE_NAME} >/dev/null 2>&1
    CURRENT_DIGEST=$(podman inspect --format='{{.Digest}}' ${IMAGE_NAME})
fi

# Read the last downloaded digest if it exists
LAST_DIGEST=""
if [ -f "$DIGEST_FILE" ]; then
    LAST_DIGEST=$(cat "$DIGEST_FILE")
fi

# Check if we need to download
NEED_DOWNLOAD=false

if [ "$FORCE_DOWNLOAD" = true ]; then
    echo "Force download requested - downloading model..."
    NEED_DOWNLOAD=true
elif [ -z "$LAST_DIGEST" ]; then
    echo "First run detected - downloading model..."
    NEED_DOWNLOAD=true
elif [ "$CURRENT_DIGEST" != "$LAST_DIGEST" ]; then
    echo "Image has been updated - downloading new model..."
    NEED_DOWNLOAD=true
else
    echo "Model is up to date, skipping download."
fi

if [ "$NEED_DOWNLOAD" = true ]; then
    # Ensure directory exists
    mkdir -p ${DIGEST_DIR}

    echo "Downloading model from ${IMAGE_NAME}"
    podman create --name temp-container ${IMAGE_NAME}
    podman --storage-driver=overlay cp temp-container:${SOURCE_DIR}/. ${DIGEST_DIR}/
    podman rm temp-container

    # Store the current digest for future comparisons
    echo "$CURRENT_DIGEST" > "$DIGEST_FILE"

    echo "Download complete!"
else
    # Clean up the pulled image if we didn't need it
    if [ -n "$CURRENT_DIGEST" ]; then
        podman rmi ${IMAGE_NAME} >/dev/null 2>&1 || true
    fi
fi

echo "Done!"
