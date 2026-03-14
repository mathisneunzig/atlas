#!/usr/bin/env bash

# Voice Assistant Setup for Raspberry Pi
# Target: Raspberry Pi OS / Debian Bookworm
# Python: 3.11

set -Eeuo pipefail

APP_NAME="Enhanced Voice Assistant"
PYTHON_BIN="python3.11"
VENV_DIR=".venv"
ENV_TEMPLATE=".env.example"
ENV_FILE=".env"
ASSETS_DIR="assets"
PLOP_FILE="${ASSETS_DIR}/plop.mp3"
MAIN_FILE="main.py"
REQUIREMENTS_FILE="requirements.txt"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_ok() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_err() {
    echo -e "${RED}[ERROR]${NC} $1"
}

cleanup_on_error() {
    local exit_code=$?
    print_err "Setup failed (exit code ${exit_code})."
    print_err "Check the message above for the failing step."
    exit "${exit_code}"
}

trap cleanup_on_error ERR

require_file() {
    local file="$1"
    if [[ ! -f "${file}" ]]; then
        print_err "Required file not found: ${file}"
        exit 1
    fi
}

check_os() {
    print_info "Checking operating system..."

    if [[ ! -f /etc/os-release ]]; then
        print_warn "Could not detect OS from /etc/os-release."
        return
    fi

    # shellcheck disable=SC1091
    source /etc/os-release

    print_ok "Detected OS: ${PRETTY_NAME:-unknown}"
}

check_apt() {
    if ! command -v apt-get >/dev/null 2>&1; then
        print_err "This script currently supports apt-based systems only."
        print_err "Please use Raspberry Pi OS / Debian, or adapt the package install section."
        exit 1
    fi
}

check_python_311() {
    print_info "Checking for Python 3.11..."

    if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
        print_warn "${PYTHON_BIN} is not installed yet."
        return 1
    fi

    local version
    version="$("${PYTHON_BIN}" -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')"
    print_ok "Found ${PYTHON_BIN} (${version})"
    return 0
}

install_system_packages() {
    print_info "Installing system packages..."

    sudo apt-get update
    sudo apt-get install -y \
        python3.11 \
        python3.11-venv \
        python3-pip \
        build-essential \
        gcc \
        pkg-config \
        portaudio19-dev \
        libasound2-dev \
        espeak \
        ffmpeg \
        git \
        curl

    print_ok "System packages installed"
}

create_venv() {
    print_info "Creating virtual environment with ${PYTHON_BIN}..."

    if [[ -d "${VENV_DIR}" ]]; then
        print_warn "Virtual environment already exists: ${VENV_DIR}"
    else
        "${PYTHON_BIN}" -m venv "${VENV_DIR}"
        print_ok "Created virtual environment: ${VENV_DIR}"
    fi
}

upgrade_pip_tools() {
    print_info "Upgrading pip tooling in virtual environment..."

    "${VENV_DIR}/bin/python" -m pip install --upgrade pip setuptools wheel

    print_ok "pip tooling upgraded"
}

install_python_dependencies() {
    require_file "${REQUIREMENTS_FILE}"

    print_info "Installing Python dependencies from ${REQUIREMENTS_FILE}..."
    "${VENV_DIR}/bin/pip" install -r "${REQUIREMENTS_FILE}"
    print_ok "Python dependencies installed"
}

setup_env_file() {
    print_info "Setting up environment file..."

    if [[ -f "${ENV_FILE}" ]]; then
        print_warn "${ENV_FILE} already exists"
        return
    fi

    if [[ -f "${ENV_TEMPLATE}" ]]; then
        cp "${ENV_TEMPLATE}" "${ENV_FILE}"
        print_ok "Created ${ENV_FILE} from ${ENV_TEMPLATE}"
    else
        print_warn "${ENV_TEMPLATE} not found; creating empty ${ENV_FILE}"
        touch "${ENV_FILE}"
    fi
}

setup_assets() {
    print_info "Preparing assets..."

    mkdir -p "${ASSETS_DIR}"

    if [[ -f "${PLOP_FILE}" ]]; then
        print_ok "Activation sound already exists: ${PLOP_FILE}"
        return
    fi

    if command -v ffmpeg >/dev/null 2>&1; then
        print_info "Creating placeholder activation sound..."
        ffmpeg -y \
            -f lavfi -i "sine=frequency=880:duration=0.20" \
            -ac 1 \
            -q:a 9 \
            "${PLOP_FILE}" \
            >/dev/null 2>&1 || true

        if [[ -f "${PLOP_FILE}" ]]; then
            print_ok "Created ${PLOP_FILE}"
        else
            print_warn "Could not create ${PLOP_FILE} automatically"
        fi
    else
        print_warn "ffmpeg not available; skipping placeholder sound creation"
    fi
}

set_permissions() {
    print_info "Setting file permissions..."

    if [[ -f "${MAIN_FILE}" ]]; then
        chmod +x "${MAIN_FILE}" || true
        print_ok "Updated permissions for ${MAIN_FILE}"
    else
        print_warn "${MAIN_FILE} not found; skipping chmod"
    fi
}

print_summary() {
    echo
    print_ok "${APP_NAME} setup completed"
    echo
    echo "Next steps:"
    echo "  1. Edit your environment file:"
    echo "     nano ${ENV_FILE}"
    echo
    echo "  2. Activate the virtual environment:"
    echo "     source ${VENV_DIR}/bin/activate"
    echo
    echo "  3. Start the assistant:"
    echo "     python ${MAIN_FILE}"
    echo
    print_warn "Make sure your API keys and audio configuration are set in ${ENV_FILE}"
}

main() {
    echo "🎤 ${APP_NAME} Setup"
    echo "=================================="

    check_os
    check_apt

    if ! check_python_311; then
        install_system_packages
        check_python_311
    else
        print_info "Installing/updating required system libraries..."
        sudo apt-get update
        sudo apt-get install -y \
            python3.11-venv \
            python3-pip \
            build-essential \
            gcc \
            pkg-config \
            portaudio19-dev \
            libasound2-dev \
            espeak \
            ffmpeg \
            git \
            curl
        print_ok "System libraries ready"
    fi

    create_venv
    upgrade_pip_tools
    install_python_dependencies
    setup_env_file
    setup_assets
    set_permissions
    print_summary
}

main "$@"