#!/bin/bash
# Podman commands for Windows users
# Usage: ./podman-run.sh [command]

CONTAINER_NAME="stockagent"
IMAGE_NAME="stockagent:latest"
PORT="8501"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Check if Podman is installed
check_podman() {
    if ! command -v podman &> /dev/null; then
        print_error "Podman is not installed. Please install Podman Desktop for Windows."
        print_status "Download from: https://podman-desktop.io/"
        exit 1
    fi
    print_status "Podman is installed: $(podman --version)"
}

# Create required directories
init_directories() {
    print_status "Checking and creating required directories..."
    
    for dir in "./data" "./logs"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_status "Created directory: $dir"
        else
            print_status "Directory exists: $dir"
        fi
    done
}

# Build the Podman image
build_podman() {
    print_header "Building Podman Image"
    check_podman
    
    # Initialize directories before building
    init_directories
    
    print_status "Building stockagent image..."
    podman build -t $IMAGE_NAME .
    
    if [ $? -eq 0 ]; then
        print_status "✅ Image built successfully!"
    else
        print_error "❌ Failed to build image"
        exit 1
    fi
}

# Start the Podman container
start_podman() {
    print_header "Starting Podman Container"
    check_podman
    
    # Stop existing container if running
    if podman ps -q -f name=$CONTAINER_NAME | grep -q .; then
        print_warning "Container already running. Stopping first..."
        podman stop $CONTAINER_NAME
        podman rm $CONTAINER_NAME
    fi
    
    print_status "Starting stockagent container..."
    
    # Get host IP for reverse proxy connection (Windows IP)
    # Note: This script assumes you're running on Windows with WSL2
    # For Linux/macOS, you might need to adjust the IP detection
    HOST_IP=${HOST_IP:-"192.168.1.100"}  # Example Windows IP, can be overridden
    
    print_status "Using host IP: $HOST_IP for reverse proxy connection"
    print_status "To override, set HOST_IP environment variable"
    
    podman run -d \
        --name $CONTAINER_NAME \
        -p $PORT:8501 \
        -v ./data:/app/data \
        -v ./logs:/app/logs \
        --env-file .env \
        --add-host "host.containers.internal:$HOST_IP" \
        $IMAGE_NAME
    
    if [ $? -eq 0 ]; then
        print_status "✅ Container started successfully!"
        print_status "🌐 Streamlit app available at: http://localhost:$PORT"
        print_status "📊 Container logs: ./podman-run.sh logs"
    else
        print_error "❌ Failed to start container"
        exit 1
    fi
}

# Stop the Podman container
stop_podman() {
    print_header "Stopping Podman Container"
    check_podman
    
    if podman ps -q -f name=$CONTAINER_NAME | grep -q .; then
        print_status "Stopping container..."
        podman stop $CONTAINER_NAME
        podman rm $CONTAINER_NAME
        print_status "✅ Container stopped and removed"
    else
        print_warning "Container is not running"
    fi
}

# Show Podman container logs
logs_podman() {
    print_header "Podman Container Logs"
    check_podman
    
    if podman ps -q -f name=$CONTAINER_NAME | grep -q .; then
        print_status "Showing logs (Ctrl+C to exit)..."
        podman logs -f $CONTAINER_NAME
    else
        print_warning "Container is not running"
        print_status "To start: ./podman-run.sh start"
    fi
}

# Test the Podman container
test_podman() {
    print_header "Testing Podman Container"
    check_podman
    
    if podman ps -q -f name=$CONTAINER_NAME | grep -q .; then
        print_status "Running tests inside container..."
        podman exec $CONTAINER_NAME python test_docker.py
    else
        print_warning "Container is not running"
        print_status "To start: ./podman-run.sh start"
    fi
}

# Run backtesting in Podman container
backtest_podman() {
    print_header "Running Backtesting in Podman Container"
    check_podman
    
    if podman ps -q -f name=$CONTAINER_NAME | grep -q .; then
        print_status "Running backtesting..."
        podman exec $CONTAINER_NAME python test_backtesting.py
    else
        print_warning "Container is not running"
        print_status "To start: ./podman-run.sh start"
    fi
}

# Show Podman container status
status_podman() {
    print_header "Podman Container Status"
    check_podman
    
    print_status "Container status:"
    podman ps -a -f name=$CONTAINER_NAME
    
    print_status "Image status:"
    podman images $IMAGE_NAME
    
    print_status "System info:"
    podman system info --format=table
}

# Clean up Podman resources
cleanup_podman() {
    print_header "Cleaning Up Podman Resources"
    check_podman
    
    print_warning "This will remove all containers and images!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Stopping and removing containers..."
        podman stop $(podman ps -aq) 2>/dev/null || true
        podman rm $(podman ps -aq) 2>/dev/null || true
        
        print_status "Removing images..."
        podman rmi $(podman images -q) 2>/dev/null || true
        
        print_status "Pruning system..."
        podman system prune -f
        
        print_status "✅ Cleanup completed!"
    else
        print_status "Cleanup cancelled"
    fi
}

# Quick start - build and run
quick_start_podman() {
    print_header "Quick Start - Build and Run"
    
    # Create data and logs directories first
    print_status "Setting up directories..."
    init_directories
    
    build_podman
    start_podman
    print_status "🎉 StockAgent is ready!"
    print_status "🌐 Open: http://localhost:$PORT"
}

# Show help
show_help() {
    print_header "Podman Commands for StockAgent"
    echo
    echo "Usage: ./podman-run.sh [command]"
    echo
    echo "Commands:"
    echo "  build     - Build Podman image"
    echo "  start     - Start container"
    echo "  stop      - Stop container"
    echo "  logs      - Show container logs"
    echo "  test      - Run tests in container"
    echo "  backtest  - Run backtesting in container"
    echo "  status    - Show container and system status"
    echo "  cleanup   - Clean up all Podman resources"
    echo "  init      - Initialize data and logs directories"
    echo "  quick     - Quick start (build + start)"
    echo "  help      - Show this help"
    echo
    echo "Examples:"
    echo "  ./podman-run.sh quick     # Build and start"
    echo "  ./podman-run.sh logs      # View logs"
    echo "  ./podman-run.sh stop      # Stop container"
    echo
    echo "Prerequisites:"
    echo "  - Install Podman Desktop for Windows"
    echo "  - Download from: https://podman-desktop.io/"
    echo "  - Create .env file with your API credentials"
}

# Main script logic
case "${1:-help}" in
    build)
        build_podman
        ;;
    start)
        start_podman
        ;;
    stop)
        stop_podman
        ;;
    logs)
        logs_podman
        ;;
    test)
        test_podman
        ;;
    backtest)
        backtest_podman
        ;;
    status)
        status_podman
        ;;
    cleanup)
        cleanup_podman
        ;;
    init)
        init_directories
        ;;
    quick)
        quick_start_podman
        ;;
    help|*)
        show_help
        ;;
esac 