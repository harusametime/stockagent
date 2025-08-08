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

# Create required directories
function Initialize-Directories {
    Write-Status "Checking and creating required directories..."
    
    $directories = @("./data", "./logs")
    
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force
            Write-Status "Created directory: $dir"
        } else {
            Write-Status "Directory exists: $dir"
        }
    }
}

# Build the Podman image
function Build-PodmanImage {
    Write-Header "Building Podman Image"
    
    if (-not (Test-Podman)) {
        exit 1
    }
    
    # Initialize directories before building
    Initialize-Directories
    
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
    
    # Create data and logs directories if they don't exist
    Write-Status "Creating data and logs directories..."
    if (-not (Test-Path "./data")) {
        New-Item -ItemType Directory -Path "./data" -Force
        Write-Status "Created ./data directory"
    }
    if (-not (Test-Path "./logs")) {
        New-Item -ItemType Directory -Path "./logs" -Force
        Write-Status "Created ./logs directory"
    }
    
    # Stop existing container if running
    $running = podman ps -q -f name=$ContainerName
    if ($running) {
        Write-Warning "Container already running. Stopping first..."
        podman stop $ContainerName
        podman rm $ContainerName
    }
    
    Write-Status "Starting stockagent container..."
    
    # Get host IP for reverse proxy connection
    $hostIP = Get-HostIP
    if (-not $hostIP) {
        Write-Error "Could not detect host IP. Please run setup-windows.ps1 first or manually specify your Windows IP."
        exit 1
    }
    
    Write-Status "Using host IP: $hostIP for reverse proxy connection"
    podman run -d `
        --name $ContainerName `
        -p $Port`:8501 `
        -v ./data:/app/data `
        -v ./logs:/app/logs `
        --env-file .env `
        --add-host "host.containers.internal:$hostIP" `
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

# Test reverse proxy connection
function Test-ReverseProxy {
    Write-Header "Testing Reverse Proxy Connection"
    
    if (-not (Test-Podman)) {
        exit 1
    }
    
    $hostIP = Get-HostIP
    if (-not $hostIP) {
        Write-Error "Could not detect host IP. Please run setup-windows.ps1 first."
        exit 1
    }
    
    Write-Status "Testing connection to reverse proxy..."
    Write-Status "Using host IP: $hostIP"
    
    # Test with curl from container
    $testCmd = "podman run --rm -it --add-host `"host.containers.internal:$hostIP`" curlimages/curl curl -v -H `"Content-Type: application/json`" -d `"{'APIPassword':'YOUR_API_PASSWORD'}`" http://host.containers.internal:8080/kabusapi/token"
    
    Write-Status "Running test command:"
    Write-Host $testCmd -ForegroundColor Cyan
    
    Invoke-Expression $testCmd
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "✅ Reverse proxy connection test successful!"
    } else {
        Write-Error "❌ Reverse proxy connection test failed"
        Write-Info "Make sure:"
        Write-Host "1. Nginx reverse proxy is running on port 8080" -ForegroundColor White
        Write-Host "2. KabusAPI is running on localhost:18081" -ForegroundColor White
        Write-Host "3. Windows Firewall allows port 8080" -ForegroundColor White
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
    
    # Create data and logs directories first
    Write-Status "Setting up directories..."
    if (-not (Test-Path "./data")) {
        New-Item -ItemType Directory -Path "./data" -Force
        Write-Status "Created ./data directory"
    }
    if (-not (Test-Path "./logs")) {
        New-Item -ItemType Directory -Path "./logs" -Force
        Write-Status "Created ./logs directory"
    }
    
    Build-PodmanImage
    Start-PodmanContainer
    Write-Status "🎉 StockAgent is ready!"
    Write-Status "🌐 Open: http://localhost:$Port"
}

function Get-HostIP {
    <#
    .SYNOPSIS
    Auto-detect Windows host IP for Podman containers
    #>
    try {
        # Get primary network adapter IP (skip loopback and link-local)
        $primaryIP = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "Ethernet*" | 
                     Where-Object {$_.IPAddress -notlike "169.254.*" -and $_.IPAddress -notlike "127.*"} | 
                     Select-Object -First 1).IPAddress
        
        if ($primaryIP) {
            Write-Host "✅ Detected host IP: $primaryIP" -ForegroundColor Green
            return $primaryIP
        } else {
            Write-Host "⚠️ Could not auto-detect IP, using fallback" -ForegroundColor Yellow
            return "192.168.1.100"  # Example fallback IP
        }
    } catch {
        Write-Host "⚠️ Error detecting IP, using fallback" -ForegroundColor Yellow
        return "192.168.1.100"  # Example fallback IP
    }
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
    Write-Host "  proxy     - Test reverse proxy connection"
    Write-Host "  backtest  - Run backtesting in container"
    Write-Host "  status    - Show container and system status"
    Write-Host "  cleanup   - Clean up all Podman resources"
    Write-Host "  init      - Initialize data and logs directories"
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
    "proxy" {
        Test-ReverseProxy
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
    "init" {
        Initialize-Directories
    }
    "quick" {
        Start-PodmanQuick
    }
    default {
        Show-PodmanHelp
    }
} 