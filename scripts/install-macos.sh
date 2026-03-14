#!/usr/bin/env bash

# Voice Assistant Setup for macOS
# Target: macOS with Homebrew
# Python: 3.11

set -Eeuo pipefail

APP_NAME="Enhanced Voice Assistant"
PYTHON_FORMULA="python@3.11"
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
    print_err "Check the output above to see which step failed."
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

check_macos() {
    print_info "Checking operating system..."

    if [[ "$(uname -s)" != "Darwin" ]]; then
        print_err "This script is intended for macOS only."
        exit 1
    fi

    print_ok "macOS detected"
}

check_xcode_tools() {
    print_info "Checking Xcode Command Line Tools..."

    if xcode-select -p >/dev/null 2>&1; then
        print_ok "Xcode Command Line Tools already installed"
    else
        print_warn "Xcode Command Line Tools not found"
        print_info "Installing Xcode Command Line Tools..."
        xcode-select --install || true
        print_warn "If the installer dialog opened, finish that first, then run this script again."
        exit 1
    fi
}

check_homebrew() {
    print_info "Checking Homebrew..."

    if ! command -v brew >/dev/null 2>&1; then
        print_err "Homebrew is not installed."
        print_err "Install Homebrew first, then rerun this script."
        print_err "See: https://brew.sh"
        exit 1
    fi

    print_ok "Homebrew found"
}

check_python_311() {
    print_info "Checking for Python 3.11..."

    if command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
        local version
        version="$("${PYTHON_BIN}" -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')"
        print_ok "Found ${PYTHON_BIN} (${version})"
        return 0
    fi

    print_warn "${PYTHON_BIN} not found"
    return 1
}

install_brew_packages() {
    print_info "Installing Homebrew packages..."

    brew update
    brew install \
        "${PYTHON_FORMULA}" \
        portaudio \
        espeak-ng \
        ffmpeg \
        git \
        curl

    print_ok "Homebrew packages installed"
}

resolve_python_bin() {
    if command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
        return 0
    fi

    local candidate
    candidate="$(brew --prefix "${PYTHON_FORMULA}")/bin/${PYTHON_BIN}"

    if [[ -x "${candidate}" ]]; then
        PYTHON_BIN="${candidate}"
        print_ok "Using Python interpreter at ${PYTHON_BIN}"
        return 0
    fi

    print_err "Could not locate Python 3.11 after Homebrew installation."
    print_err "Try adding Homebrew's Python to your PATH and rerun the script."
    exit 1
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

print_path_hint() {
    local brew_prefix
    brew_prefix="$(brew --prefix "${PYTHON_FORMULA}")"

    echo
    print_info "If '${PYTHON_BIN}' is not found in future shells, add this to your shell profile:"
    echo "export PATH=\"${brew_prefix}/bin:\$PATH\""
}

print_summary() {
    echo
    print_ok "${APP_NAME} setup completed on macOS"
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
    echo "🎤 ${APP_NAME} Setup (macOS)"
    echo "=================================="

    check_macos
    check_xcode_tools
    check_homebrew

    if ! check_python_311; then
        install_brew_packages
    else
        print_info "Installing/updating required Homebrew packages..."
        brew update
        brew install \
            portaudio \
            espeak-ng \
            ffmpeg \
            git \
            curl
        print_ok "Required Homebrew packages are ready"
    fi

    resolve_python_bin
    create_venv
    upgrade_pip_tools
    install_python_dependencies
    setup_env_file
    setup_assets
    set_permissions
    print_path_hint
    print_summary
}

main "$@"