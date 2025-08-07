# Setup Nginx Reverse Proxy for KabusAPI
# Run this script on Windows where KabusAPI is running

Write-Host "🔧 Setting up Nginx Reverse Proxy for KabusAPI" -ForegroundColor Green

# Check if nginx is installed
try {
    nginx -v
    Write-Host "✅ Nginx is already installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Nginx not found. Please install nginx first." -ForegroundColor Red
    Write-Host "💡 Download from: https://nginx.org/en/download.html" -ForegroundColor Yellow
    exit 1
}

# Create nginx configuration directory if it doesn't exist
$nginxConfDir = "C:\nginx\conf"
if (!(Test-Path $nginxConfDir)) {
    New-Item -ItemType Directory -Path $nginxConfDir -Force
    Write-Host "✅ Created nginx config directory" -ForegroundColor Green
}

# Copy the proxy configuration
$proxyConfig = "nginx-proxy.conf"
if (Test-Path $proxyConfig) {
    Copy-Item $proxyConfig "$nginxConfDir\nginx.conf" -Force
    Write-Host "✅ Copied nginx proxy configuration" -ForegroundColor Green
} else {
    Write-Host "❌ nginx-proxy.conf not found!" -ForegroundColor Red
    exit 1
}

# Test nginx configuration
try {
    nginx -t
    Write-Host "✅ Nginx configuration is valid" -ForegroundColor Green
} catch {
    Write-Host "❌ Nginx configuration test failed" -ForegroundColor Red
    exit 1
}

# Start nginx
try {
    nginx
    Write-Host "✅ Nginx reverse proxy started on port 8080" -ForegroundColor Green
    Write-Host "🌐 Proxy URL: http://localhost:8080/kabusapi/" -ForegroundColor Cyan
    Write-Host "📋 Update your .env file:" -ForegroundColor Yellow
    Write-Host "   KABUSAPI_HOST=host.containers.internal" -ForegroundColor White
    Write-Host "   KABUSAPI_PORT=8080" -ForegroundColor White
} catch {
    Write-Host "❌ Failed to start nginx" -ForegroundColor Red
    exit 1
}

Write-Host "🎉 Reverse proxy setup complete!" -ForegroundColor Green 