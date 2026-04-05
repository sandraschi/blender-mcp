#!/bin/bash
# Blender MCP Systemd Service Installer
# Installs Blender MCP as a system service on Linux

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVICE_NAME="blender-mcp"
SERVICE_USER="mcp"
INSTALL_DIR="/opt/blender-mcp"
VENV_DIR="$INSTALL_DIR/venv"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "This script should not be run as root for security reasons."
        log_info "It will use sudo when necessary."
        exit 1
    fi
}

# Check system requirements
check_requirements() {
    log_info "Checking system requirements..."

    # Check if systemd is available
    if ! command -v systemctl &> /dev/null; then
        log_error "systemd is required but not found."
        exit 1
    fi

    # Check if Python 3.8+ is available
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not found."
        exit 1
    fi

    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    if [[ $(echo "$PYTHON_VERSION < 3.8" | bc -l) -eq 1 ]]; then
        log_error "Python 3.8+ is required. Found: $PYTHON_VERSION"
        exit 1
    fi

    log_success "System requirements met"
}

# Create system user
create_user() {
    log_info "Creating system user: $SERVICE_USER"

    if id "$SERVICE_USER" &>/dev/null; then
        log_warning "User $SERVICE_USER already exists"
    else
        sudo useradd --system --shell /bin/bash --home-dir "$INSTALL_DIR" --create-home "$SERVICE_USER"
        log_success "Created user: $SERVICE_USER"
    fi
}

# Install Python package
install_package() {
    log_info "Installing Blender MCP package..."

    # Create installation directory
    sudo mkdir -p "$INSTALL_DIR"
    sudo chown "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"

    # Create virtual environment
    sudo -u "$SERVICE_USER" python3 -m venv "$VENV_DIR"

    # Install package
    sudo -u "$SERVICE_USER" "$VENV_DIR/bin/pip" install --upgrade pip
    sudo -u "$SERVICE_USER" "$VENV_DIR/bin/pip" install blender-mcp

    log_success "Package installed successfully"
}

# Install systemd service
install_service() {
    local service_mode=$1
    local service_file="systemd/blender-mcp.service"

    if [[ "$service_mode" == "http" ]]; then
        service_file="systemd/blender-mcp-http.service"
    fi

    log_info "Installing systemd service..."

    # Copy service file
    sudo cp "$service_file" "/etc/systemd/system/${SERVICE_NAME}.service"

    # Reload systemd
    sudo systemctl daemon-reload

    # Enable service
    sudo systemctl enable "$SERVICE_NAME"

    log_success "Service installed and enabled"
}

# Configure firewall (optional)
configure_firewall() {
    if command -v ufw &> /dev/null; then
        log_info "Configuring firewall..."
        sudo ufw allow 8000/tcp || true
        log_success "Firewall configured (port 8000)"
    fi
}

# Test service
test_service() {
    log_info "Testing service installation..."

    # Start service
    sudo systemctl start "$SERVICE_NAME"

    # Wait a moment
    sleep 3

    # Check status
    if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
        log_success "Service is running successfully"

        # Show service status
        sudo systemctl status "$SERVICE_NAME" --no-pager -l

        # Test basic functionality
        if command -v curl &> /dev/null; then
            log_info "Testing service health..."
            # For HTTP mode, test the health endpoint
            if curl -f http://localhost:8000/health &>/dev/null 2>&1; then
                log_success "Service health check passed"
            else
                log_warning "Service health check failed (may be normal for stdio mode)"
            fi
        fi
    else
        log_error "Service failed to start"
        sudo systemctl status "$SERVICE_NAME" --no-pager -l
        exit 1
    fi
}

# Show usage information
show_usage() {
    log_info "Service management commands:"
    echo "  Start service:   sudo systemctl start $SERVICE_NAME"
    echo "  Stop service:    sudo systemctl stop $SERVICE_NAME"
    echo "  Restart service: sudo systemctl restart $SERVICE_NAME"
    echo "  View logs:       sudo journalctl -u $SERVICE_NAME -f"
    echo "  Check status:    sudo systemctl status $SERVICE_NAME"
    echo ""
    log_info "Uninstall command:"
    echo "  sudo systemctl stop $SERVICE_NAME"
    echo "  sudo systemctl disable $SERVICE_NAME"
    echo "  sudo rm /etc/systemd/system/${SERVICE_NAME}.service"
    echo "  sudo systemctl daemon-reload"
    echo "  sudo userdel $SERVICE_USER"
    echo "  sudo rm -rf $INSTALL_DIR"
}

# Main installation function
main() {
    local service_mode="stdio"

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --http)
                service_mode="http"
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [--http]"
                echo "  --http    Install HTTP service instead of stdio service"
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done

    echo "========================================"
    echo "Blender MCP Systemd Service Installer"
    echo "========================================"
    echo ""

    check_root
    check_requirements
    create_user
    install_package
    install_service "$service_mode"
    configure_firewall
    test_service

    echo ""
    echo "========================================"
    log_success "Installation completed successfully!"
    echo "========================================"
    echo ""

    if [[ "$service_mode" == "http" ]]; then
        log_info "HTTP service is running on port 8000"
        log_info "Access at: http://localhost:8000"
    else
        log_info "Stdio service is running for MCP clients"
    fi

    echo ""
    show_usage
}

# Run main function
main "$@"





