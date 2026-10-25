
#!/usr/bin/env bash
set -euo pipefail

# Practice default; override IMAGE for production.
IMAGE="${NGC_IMAGE:-${IMAGE:-ubuntu:22.04}}"
DEST="${NGC_DEST:-./artifacts/containers}"
CONVERT_SQSH="${CONVERT_SQSH:-false}"
VALIDATE_SQSH="${VALIDATE_SQSH:-false}"

mkdir -p "$DEST"

echo "======================================"
echo "Container image preparation"
echo "Image: $IMAGE"
echo "Destination: $DEST"
echo "======================================"

# 1. Pull image
docker pull "$IMAGE"

# 2. Verify Docker knows the image
docker image inspect "$IMAGE" >/dev/null
echo "[OK] Docker image pulled and inspected."

# 3. Optional conversion to Enroot SquashFS
if [[ "$CONVERT_SQSH" == "true" ]]; then
    if ! command -v enroot >/dev/null 2>&1; then
        echo "ERROR: Enroot is required for .sqsh conversion."
        echo "Run this step in an approved Linux environment."
        exit 1
    fi

    # Make a filesystem-safe filename from the image reference.
    SAFE_NAME="$(printf '%s' "$IMAGE" |
        sed 's/[^a-zA-Z0-9_.-]/_/g')"
    SQSH_FILE="$DEST/${SAFE_NAME}.sqsh"

    echo "Converting image to: $SQSH_FILE"
    enroot import --output "$SQSH_FILE" "docker://$IMAGE"

    test -s "$SQSH_FILE"
    echo "[OK] .sqsh file created: $SQSH_FILE"

    # 4. Optional startup validation
    if [[ "$VALIDATE_SQSH" == "true" ]]; then
        echo "Checking converted image startup..."

        CONTAINER_NAME="image-check-$$"
        cleanup() {
            enroot remove "$CONTAINER_NAME" >/dev/null 2>&1 || true
        }
        trap cleanup EXIT

        enroot create --name "$CONTAINER_NAME" "$SQSH_FILE"
        enroot start "$CONTAINER_NAME" cat /etc/os-release

        echo "[OK] Converted image started successfully."
    fi
else
    echo "[INFO] .sqsh conversion skipped."
    echo "Set CONVERT_SQSH=true in Linux with Enroot to enable it."
fi

echo "Container preparation finished."
