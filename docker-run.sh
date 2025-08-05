#!/bin/bash

# Stock Trading Agent Docker Runner
# This script provides easy commands to run the trading system in Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to check if docker-compose is available
check_docker_compose() {
    if ! command -v docker-compose > /dev/null 2>&1; then
        print_error "docker-compose is not installed. Please install it and try again."
        exit 1
    fi
}

# Function to create .env file if it doesn't exist
create_env_file() {
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from template..."
        cp env_example.txt .env
        print_success ".env file created. Please edit it with your API credentials."
    fi
}

# Function to create necessary directories
create_directories() {
    mkdir -p data logs
    print_success "Created data and logs directories"
}

# Function to build the Docker image
build_image() {
    print_status "Building Docker image..."
    docker-compose build
    print_success "Docker image built successfully"
}

# Function to start the application
start_app() {
    print_status "Starting Stock Trading Agent..."
    docker-compose up -d
    print_success "Application started successfully"
    print_status "Access the web interface at: http://localhost:8501"
}

# Function to stop the application
stop_app() {
    print_status "Stopping Stock Trading Agent..."
    docker-compose down
    print_success "Application stopped successfully"
}

# Function to view logs
view_logs() {
    print_status "Showing application logs..."
    docker-compose logs -f
}

# Function to run tests in Docker
run_tests() {
    print_status "Running tests in Docker..."
    docker-compose run --rm stockagent python test_system.py
}

# Function to run backtesting in Docker
run_backtesting() {
    print_status "Running backtesting in Docker..."
    docker-compose run --rm stockagent python test_backtesting.py
}

# Function to run Docker environment test
run_docker_test() {
    print_status "Running Docker environment test..."
    docker-compose run --rm stockagent python test_docker.py
}

# Function to show status
show_status() {
    print_status "Checking application status..."
    docker-compose ps
}

# Function to clean up
cleanup() {
    print_status "Cleaning up Docker resources..."
    docker-compose down --volumes --remove-orphans
    docker system prune -f
    print_success "Cleanup completed"
}

# Function to show help
show_help() {
    echo "Stock Trading Agent Docker Runner"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build     - Build the Docker image"
    echo "  start     - Start the application"
    echo "  stop      - Stop the application"
    echo "  restart   - Restart the application"
    echo "  logs      - View application logs"
    echo "  test      - Run tests in Docker"
    echo "  backtest  - Run backtesting in Docker"
    echo "  docker-test - Run Docker environment test"
    echo "  status    - Show application status"
    echo "  cleanup   - Clean up Docker resources"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build"
    echo "  $0 start"
    echo "  $0 logs"
}

# Main script logic
case "${1:-help}" in
    "build")
        check_docker
        check_docker_compose
        create_env_file
        create_directories
        build_image
        ;;
    "start")
        check_docker
        check_docker_compose
        create_env_file
        create_directories
        start_app
        ;;
    "stop")
        check_docker_compose
        stop_app
        ;;
    "restart")
        check_docker_compose
        stop_app
        sleep 2
        start_app
        ;;
    "logs")
        check_docker_compose
        view_logs
        ;;
    "test")
        check_docker
        check_docker_compose
        create_directories
        run_tests
        ;;
    "backtest")
        check_docker
        check_docker_compose
        create_directories
        run_backtesting
        ;;
    "docker-test")
        check_docker
        check_docker_compose
        create_directories
        run_docker_test
        ;;
    "status")
        check_docker_compose
        show_status
        ;;
    "cleanup")
        check_docker_compose
        cleanup
        ;;
    "help"|*)
        show_help
        ;;
esac 