#!/usr/bin/env bash

set -Eeuo pipefail

# ==========================================
# MyTube automatic Ubuntu deployment
# ==========================================

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

log() {
    echo
    echo "[$(date '+%H:%M:%S')] $1"
}

fail() {
    echo
    echo "[ERROR] $1"
    exit 1
}

# ------------------------------------------
# 1. Check operating system
# ------------------------------------------

if [[ ! -f /etc/os-release ]]; then
    fail "Cannot determine Linux distribution."
fi

source /etc/os-release

if [[ "${ID}" != "ubuntu" ]]; then
    fail "This installer supports Ubuntu only."
fi

log "Ubuntu detected: ${PRETTY_NAME}"

# ------------------------------------------
# 2. Check privileges
# ------------------------------------------

if [[ "$EUID" -eq 0 ]]; then
    SUDO=""
else
    command -v sudo >/dev/null 2>&1 \
        || fail "sudo is required."

    SUDO="sudo"
fi

# ------------------------------------------
# 3. Install Docker Engine
# ------------------------------------------

log "Installing Docker dependencies..."

$SUDO apt-get update

$SUDO apt-get install -y \
    ca-certificates \
    curl \
    openssl

log "Adding official Docker repository..."

$SUDO install -m 0755 -d /etc/apt/keyrings

$SUDO curl -fsSL \
    https://download.docker.com/linux/ubuntu/gpg \
    -o /etc/apt/keyrings/docker.asc

$SUDO chmod a+r /etc/apt/keyrings/docker.asc

ARCH="$(dpkg --print-architecture)"
CODENAME="${UBUNTU_CODENAME:-$VERSION_CODENAME}"

$SUDO tee /etc/apt/sources.list.d/docker.sources \
    > /dev/null <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: ${CODENAME}
Components: stable
Architectures: ${ARCH}
Signed-By: /etc/apt/keyrings/docker.asc
EOF

$SUDO apt-get update

log "Installing Docker Engine and Compose..."

$SUDO apt-get install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin

# ------------------------------------------
# 4. Start Docker
# ------------------------------------------

log "Starting Docker service..."

$SUDO systemctl enable docker
$SUDO systemctl start docker

$SUDO docker version
$SUDO docker compose version

# ------------------------------------------
# 5. Check project configuration
# ------------------------------------------

cd "$PROJECT_DIR"

[[ -f docker-compose.yaml ]] \
    || fail "docker-compose.yaml not found."

[[ -f Dockerfile ]] \
    || fail "Dockerfile not found."

[[ -f .env.example ]] \
    || fail ".env.example not found."

# ------------------------------------------
# 6. Prepare environment
# ------------------------------------------

if [[ ! -f .env ]]; then
    log "Creating .env from .env.example..."

    cp .env.example .env

    # Generate unique secrets for fresh installation
    set_env() {
        local key="$1"
        local value="$2"

        if grep -q "^${key}=" .env; then
            sed -i "s|^${key}=.*|${key}=${value}|" .env
        else
            echo "${key}=${value}" >> .env
        fi
    }

    set_env POSTGRES_PASSWORD "$(openssl rand -hex 32)"
    set_env SECRET_KEY "$(openssl rand -hex 32)"
    set_env CSRF_SECRET_KEY "$(openssl rand -hex 32)"

    log ".env created with generated secrets."
else
    log "Existing .env found. Keeping it unchanged."
fi

# ------------------------------------------
# 7. Validate Docker Compose configuration
# ------------------------------------------

log "Validating Docker Compose configuration..."

$SUDO docker compose config --quiet \
    || fail "Invalid Docker Compose configuration."

SERVICES="$($SUDO docker compose config --services)"

echo "$SERVICES"

echo "$SERVICES" | grep -qx "postgres" \
    || fail "PostgreSQL service is missing."

echo "$SERVICES" | grep -qx "api" \
    || fail "API service is missing."

if echo "$SERVICES" | grep -qx "garage"; then
    fail "Garage is still enabled in docker-compose.yaml. Configure filesystem storage before deployment."
fi


# ------------------------------------------
# 8. Build and start application
# ------------------------------------------

log "Building MyTube images..."

$SUDO docker compose build

log "Starting MyTube services..."

$SUDO docker compose up -d --wait --wait-timeout 180

# ------------------------------------------
# 9. Create test data
# ------------------------------------------

log "Creating test data..."

[[ -f scripts/seed_data.py ]] \
    || fail "scripts/seed_data.py not found in project."

$SUDO docker compose exec -T api \
    python scripts/seed_data.py \
    || fail "Failed to create test data."

log "Test data created successfully."

# ------------------------------------------
# 10. Show status
# ------------------------------------------

log "Deployment completed."

$SUDO docker compose ps

echo
echo "=========================================="
echo " MyTube deployment finished!"
echo "=========================================="
echo
echo " Application: http://localhost:8000"
echo " API docs:    http://localhost:8000/docs"
echo
echo " Useful commands:"
echo " docker compose logs -f"
echo " docker compose ps"
echo " docker compose down"
echo
echo "=========================================="
