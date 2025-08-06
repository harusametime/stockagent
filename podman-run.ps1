# Podman commands for Windows PowerShell
# Usage: .\podman-run.ps1 [command]

param(
    [string]$Command = "help"
)

$ContainerName = "stockagent"
$ImageName = "stockagent:latest"
$Port = "8501"

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"
$White = "White"

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor $Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Red
}

function Write-Header {
    param([string]$Message)
    Write-Host "=================================" -ForegroundColor $Blue
    Write-Host $Message -ForegroundColor $Blue
    Write-Host "=================================" -ForegroundColor $Blue
}

# Check if Podman is installed
function Test-Podman {
    try {
        $version = podman --version
        Write-Status "Podman is installed: $version"
        return $true
    }
    catch {
        Write-Error "Podman is not installed. Please install Podman Desktop for Windows."
        Write-Status "Download from: https://podman-desktop.io/"
        return $false
    }
}

# Build the Podman image
function Build-PodmanImage {
    Write-Header "Building Podman Image"
    
    if (-not (Test-Podman)) {
        exit 1
    }
    
    Write-Status "Building stockagent image..."
    podman build -t $ImageName .
    
    if ($LASTEXITCODE -eq 0) {
        Write-Status "✅ Image built successfully!"
    }
    else {
        Write-Error "❌ Failed to build image"
        exit 1
    }
}

# Start the Podman container
function Start-PodmanContainer {
    Write-Header "Starting Podman Container"
    
    if (-not (Test-Podman)) {
        exit 1
    }
    
    # Stop existing container if running
    $running = podman ps -q -f name=$ContainerName
    if ($running) {
        Write-Warning "Container already running. Stopping first..."
        podman stop $ContainerName
        podman rm $ContainerName
    }
    
    Write-Status "Starting stockagent container..."
    podman run -d `
        --name $ContainerName `
        -p $Port`:8501 `
        -v ./data:/app/data `
        -v ./logs:/app/logs `
        --env-file .env `
        $ImageName
    
    if ($LASTEXITCODE -eq 0) {
        Write-Status "✅ Container started successfully!"
        Write-Status "🌐 Streamlit app available at: http://localhost:$Port"
        Write-Status "📊 Container logs: .\podman-run.ps1 logs"
    }
    else {
        Write-Error "❌ Failed to start container"
        exit 1
    }
}

# Stop the Podman container
function Stop-PodmanContainer {
    Write-Header "Stopping Podman Container"
    
    if (-not (Test-Podman)) {
        exit 1
    }
    
    $running = podman ps -q -f name=$ContainerName
    if ($running) {
        Write-Status "Stopping container..."
        podman stop $ContainerName
        podman rm $ContainerName
        Write-Status "✅ Container stopped and removed"
    }
    else {
        Write-Warning "Container is not running"
    }
}

# Show Podman container logs
function Show-PodmanLogs {
    Write-Header "Podman Container Logs"
    
    if (-not (Test-Podman)) {
        exit 1
    }
    
    $running = podman ps -q -f name=$ContainerName
    if ($running) {
        Write-Status "Showing logs (Ctrl+C to exit)..."
        podman logs -f $ContainerName
    }
    else {
        Write-Warning "Container is not running"
        Write-Status "To start: .\podman-run.ps1 start"
    }
}

# Test the Podman container
function Test-PodmanContainer {
    Write-Header "Testing Podman Container"
    
    if (-not (Test-Podman)) {
        exit 1
    }
    
    $running = podman ps -q -f name=$ContainerName
    if ($running) {
        Write-Status "Running tests inside container..."
        podman exec $ContainerName python test_docker.py
    }
    else {
        Write-Warning "Container is not running"
        Write-Status "To start: .\podman-run.ps1 start"
    }
}

# Run backtesting in Podman container
function Invoke-PodmanBacktest {
    Write-Header "Running Backtesting in Podman Container"
    
    if (-not (Test-Podman)) {
        exit 1
    }
    
    $running = podman ps -q -f name=$ContainerName
    if ($running) {
        Write-Status "Running backtesting..."
        podman exec $ContainerName python test_backtesting.py
    }
    else {
        Write-Warning "Container is not running"
        Write-Status "To start: .\podman-run.ps1 start"
    }
}

# Show Podman container status
function Show-PodmanStatus {
    Write-Header "Podman Container Status"
    
    if (-not (Test-Podman)) {
        exit 1
    }
    
    Write-Status "Container status:"
    podman ps -a -f name=$ContainerName
    
    Write-Status "Image status:"
    podman images $ImageName
    
    Write-Status "System info:"
    podman system info --format=table
}

# Clean up Podman resources
function Clear-PodmanResources {
    Write-Header "Cleaning Up Podman Resources"
    
    if (-not (Test-Podman)) {
        exit 1
    }
    
    Write-Warning "This will remove all containers and images!"
    $confirm = Read-Host "Are you sure? (y/N)"
    
    if ($confirm -eq "y" -or $confirm -eq "Y") {
        Write-Status "Stopping and removing containers..."
        podman stop $(podman ps -aq) 2>$null
        podman rm $(podman ps -aq) 2>$null
        
        Write-Status "Removing images..."
        podman rmi $(podman images -q) 2>$null
        
        Write-Status "Pruning system..."
        podman system prune -f
        
        Write-Status "✅ Cleanup completed!"
    }
    else {
        Write-Status "Cleanup cancelled"
    }
}

# Quick start - build and run
function Start-PodmanQuick {
    Write-Header "Quick Start - Build and Run"
    Build-PodmanImage
    Start-PodmanContainer
    Write-Status "🎉 StockAgent is ready!"
    Write-Status "🌐 Open: http://localhost:$Port"
}

# Show help
function Show-PodmanHelp {
    Write-Header "Podman Commands for StockAgent"
    Write-Host ""
    Write-Host "Usage: .\podman-run.ps1 [command]"
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "  build     - Build Podman image"
    Write-Host "  start     - Start container"
    Write-Host "  stop      - Stop container"
    Write-Host "  logs      - Show container logs"
    Write-Host "  test      - Run tests in container"
    Write-Host "  backtest  - Run backtesting in container"
    Write-Host "  status    - Show container and system status"
    Write-Host "  cleanup   - Clean up all Podman resources"
    Write-Host "  quick     - Quick start (build + start)"
    Write-Host "  help      - Show this help"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\podman-run.ps1 quick     # Build and start"
    Write-Host "  .\podman-run.ps1 logs      # View logs"
    Write-Host "  .\podman-run.ps1 stop      # Stop container"
    Write-Host ""
    Write-Host "Prerequisites:"
    Write-Host "  - Install Podman Desktop for Windows"
    Write-Host "  - Download from: https://podman-desktop.io/"
    Write-Host "  - Create .env file with your API credentials"
}

# Main script logic
switch ($Command.ToLower()) {
    "build" {
        Build-PodmanImage
    }
    "start" {
        Start-PodmanContainer
    }
    "stop" {
        Stop-PodmanContainer
    }
    "logs" {
        Show-PodmanLogs
    }
    "test" {
        Test-PodmanContainer
    }
    "backtest" {
        Invoke-PodmanBacktest
    }
    "status" {
        Show-PodmanStatus
    }
    "cleanup" {
        Clear-PodmanResources
    }
    "quick" {
        Start-PodmanQuick
    }
    default {
        Show-PodmanHelp
    }
} 