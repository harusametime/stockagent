# StockAgent Windows Setup Script
# This script automates the complete setup process for Windows

param(
    [string]$NginxVersion = "1.24.0",
    [string]$InstallPath = "C:\nginx",
    [string]$ProxyPort = "8080"
)

function Write-Status {
    param([string]$Message, [string]$Color = "Green")
    Write-Host "🔧 $Message" -ForegroundColor $Color
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️ $Message" -ForegroundColor Cyan
}

function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Install-Nginx {
    Write-Status "Installing Nginx..."
    
    # Check if nginx is already installed
    try {
        $nginxVersion = nginx -v 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Nginx is already installed: $nginxVersion"
            return $true
        }
    } catch {
        # Continue with installation
    }
    
    # Create installation directory
    if (!(Test-Path $InstallPath)) {
        New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
        Write-Success "Created installation directory: $InstallPath"
    }
    
    # Download nginx
    $nginxUrl = "http://nginx.org/download/nginx-$NginxVersion.zip"
    $zipPath = "$env:TEMP\nginx-$NginxVersion.zip"
    
    Write-Info "Downloading Nginx $NginxVersion..."
    try {
        Invoke-WebRequest -Uri $nginxUrl -OutFile $zipPath -UseBasicParsing
        Write-Success "Downloaded Nginx"
    } catch {
        Write-Error "Failed to download Nginx: $($_.Exception.Message)"
        return $false
    }
    
    # Extract nginx
    Write-Info "Extracting Nginx..."
    try {
        Expand-Archive -Path $zipPath -DestinationPath $env:TEMP -Force
        $extractedPath = Get-ChildItem -Path $env:TEMP -Name "nginx-*" | Select-Object -First 1
        Copy-Item -Path "$env:TEMP\$extractedPath\*" -Destination $InstallPath -Recurse -Force
        Write-Success "Extracted Nginx to $InstallPath"
    } catch {
        Write-Error "Failed to extract Nginx: $($_.Exception.Message)"
        return $false
    }
    
    # Add to PATH
    $currentPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")
    if ($currentPath -notlike "*$InstallPath*") {
        [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$InstallPath", "Machine")
        Write-Success "Added Nginx to PATH"
    }
    
    # Clean up
    Remove-Item $zipPath -Force -ErrorAction SilentlyContinue
    Remove-Item "$env:TEMP\$extractedPath" -Recurse -Force -ErrorAction SilentlyContinue
    
    return $true
}

function Setup-NginxProxy {
    Write-Status "Setting up Nginx reverse proxy..."
    
    # Create nginx configuration directory
    $nginxConfDir = "$InstallPath\conf"
    if (!(Test-Path $nginxConfDir)) {
        New-Item -ItemType Directory -Path $nginxConfDir -Force | Out-Null
        Write-Success "Created nginx config directory"
    }
    
    # Create logs directory
    $nginxLogsDir = "$InstallPath\logs"
    if (!(Test-Path $nginxLogsDir)) {
        New-Item -ItemType Directory -Path $nginxLogsDir -Force | Out-Null
        Write-Success "Created nginx logs directory"
    }
    
    # Create nginx proxy configuration
    $nginxConfig = @"
events {
    worker_connections 1024;
}

http {
    # Logging configuration
    log_format main '`$remote_addr - `$remote_user [`$time_local] "`$request" '
                    '`$status `$body_bytes_sent "`$http_referer" '
                    '"`$http_user_agent" "`$http_x_forwarded_for"';

    access_log $nginxLogsDir\access.log main;
    error_log $nginxLogsDir\error.log;

    upstream kabusapi {
        server 127.0.0.1:18081;
    }

    server {
        listen 0.0.0.0:$ProxyPort;
        
        location /kabusapi/ {
            proxy_pass http://kabusapi/;
            proxy_set_header Host `$host;
            proxy_set_header X-Real-IP `$remote_addr;
            proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto `$scheme;
        }
    }
}
"@
    
    # Write configuration file
    $nginxConfig | Out-File -FilePath "$nginxConfDir\nginx.conf" -Encoding UTF8
    Write-Success "Created nginx proxy configuration"
    
    # Test nginx configuration
    try {
        & "$InstallPath\nginx.exe" -t
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Nginx configuration is valid"
        } else {
            Write-Error "Nginx configuration test failed"
            return $false
        }
    } catch {
        Write-Error "Failed to test nginx configuration: $($_.Exception.Message)"
        return $false
    }
    
    return $true
}

function Start-NginxProxy {
    Write-Status "Starting Nginx reverse proxy..."
    
    # Stop any existing nginx processes
    try {
        & "$InstallPath\nginx.exe" -s stop 2>$null
        Start-Sleep -Seconds 2
    } catch {
        # Ignore errors if nginx wasn't running
    }
    
    # Check if port is already in use
    $portInUse = Get-NetTCPConnection -LocalPort $ProxyPort -ErrorAction SilentlyContinue
    if ($portInUse) {
        Write-Error "Port $ProxyPort is already in use. Please stop the service using this port first."
        return $false
    }
    
    # Start nginx
    try {
        # Change to nginx directory for proper log file paths
        Push-Location $InstallPath
        
        & "$InstallPath\nginx.exe"
        Start-Sleep -Seconds 3
        
        # Check if nginx is running
        $process = Get-Process -Name "nginx" -ErrorAction SilentlyContinue
        if ($process) {
            Write-Success "Nginx reverse proxy started on port $ProxyPort"
            
            # Check if nginx is listening on the port
            $listening = Get-NetTCPConnection -LocalPort $ProxyPort -ErrorAction SilentlyContinue
            if ($listening) {
                Write-Success "Nginx is listening on port $ProxyPort"
            } else {
                Write-Error "Nginx started but not listening on port $ProxyPort"
                return $false
            }
            
            Pop-Location
            return $true
        } else {
            Write-Error "Failed to start Nginx"
            
            # Check error log for details
            $errorLog = "$InstallPath\logs\error.log"
            if (Test-Path $errorLog) {
                Write-Info "Nginx error log:"
                Get-Content $errorLog -Tail 5 | ForEach-Object { Write-Host "   $_" -ForegroundColor Yellow }
            }
            
            Pop-Location
            return $false
        }
    } catch {
        Write-Error "Failed to start Nginx: $($_.Exception.Message)"
        Pop-Location
        return $false
    }
}

function Test-ProxyConnection {
    Write-Status "Testing proxy connection..."
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$ProxyPort/kabusapi/token" -Method POST -Body '{"APIPassword":"test"}' -ContentType "application/json" -TimeoutSec 10
        Write-Success "Proxy connection test successful (Status: $($response.StatusCode))"
        return $true
    } catch {
        Write-Error "Proxy connection test failed: $($_.Exception.Message)"
        return $false
    }
}

function Setup-Environment {
    Write-Status "Setting up environment configuration..."
    
    # Create .env file if it doesn't exist
    if (!(Test-Path ".env")) {
        Copy-Item "env-proxy-example.txt" ".env" -ErrorAction SilentlyContinue
        if (Test-Path ".env") {
            Write-Success "Created .env file from template"
        } else {
            Write-Error "Failed to create .env file"
            return $false
        }
    }
    
    # Update .env with proxy settings
    $envContent = Get-Content ".env" -Raw
    $envContent = $envContent -replace "KABUSAPI_HOST=.*", "KABUSAPI_HOST=host.containers.internal"
    $envContent = $envContent -replace "KABUSAPI_PORT=.*", "KABUSAPI_PORT=$ProxyPort"
    $envContent | Out-File ".env" -Encoding UTF8
    
    Write-Success "Updated .env file with proxy configuration"
    return $true
}

function Show-NextSteps {
    Write-Host "`n" + "="*60
    Write-Host "🎉 SETUP COMPLETE!" -ForegroundColor Green
    Write-Host "="*60
    Write-Host "`n📋 Next steps:"
    Write-Host "1. Test the proxy connection:"
    Write-Host "   python test_network_connectivity.py"
    Write-Host "   python test_api_connection.py"
    Write-Host ""
    Write-Host "2. Run the application:"
    Write-Host "   docker-compose up -d --build"
    Write-Host "   or"
    Write-Host "   .\podman-run.ps1 build"
    Write-Host "   .\podman-run.ps1 start"
    Write-Host ""
    Write-Host "3. Access the application:"
    Write-Host "   http://localhost:8501"
    Write-Host ""
    Write-Host "🔧 Nginx Management:"
    Write-Host "   Start: nginx"
    Write-Host "   Stop: nginx -s stop"
    Write-Host "   Reload: nginx -s reload"
    Write-Host "   Test: nginx -t"
    Write-Host ""
    Write-Host "📖 For more information, see README_REVERSE_PROXY.md"
    Write-Host "="*60
}

# Main execution
function Main {
    Write-Host "🚀 StockAgent Windows Setup" -ForegroundColor Green
    Write-Host "="*40
    
    # Check if running as administrator
    if (!(Test-Administrator)) {
        Write-Error "This script requires administrator privileges. Please run as administrator."
        exit 1
    }
    
    # Install nginx
    if (!(Install-Nginx)) {
        Write-Error "Failed to install Nginx"
        exit 1
    }
    
    # Setup nginx proxy
    if (!(Setup-NginxProxy)) {
        Write-Error "Failed to setup Nginx proxy"
        exit 1
    }
    
    # Start nginx proxy
    if (!(Start-NginxProxy)) {
        Write-Error "Failed to start Nginx proxy"
        exit 1
    }
    
    # Test proxy connection
    if (!(Test-ProxyConnection)) {
        Write-Error "Proxy connection test failed"
        Write-Info "Make sure KabusAPI is running on localhost:18081"
        exit 1
    }
    
    # Setup environment
    if (!(Setup-Environment)) {
        Write-Error "Failed to setup environment"
        exit 1
    }
    
    # Show next steps
    Show-NextSteps
}

# Run the main function
Main 