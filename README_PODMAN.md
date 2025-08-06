# StockAgent with Podman (Windows)

This guide explains how to run StockAgent using **Podman** on Windows, which is a great alternative to Docker.

## 🚀 Quick Start

```bash
# 1. Install Podman Desktop
# Download from: https://podman-desktop.io/

# 2. Clone the repository
git clone https://github.com/harusametime/stockagent.git
cd stockagent

# 3. Create environment file
cp env_example.txt .env
# Edit .env with your API credentials

# 4. Quick start with Podman
./podman-run.sh quick
```

## 📋 Prerequisites

### 1. Install Podman Desktop for Windows

**Download from:** https://podman-desktop.io/

**Installation Steps:**
1. Download the Windows installer
2. Run the installer as Administrator
3. Follow the installation wizard
4. Restart your computer
5. Open Podman Desktop

### 2. Verify Installation

```bash
# Check Podman version
podman --version

# Check Podman Compose
podman-compose --version
```

### 3. Create Environment File

```bash
# Copy the example environment file
cp env_example.txt .env

# Edit with your API credentials
notepad .env
```

## 🛠️ Podman Commands

### Basic Commands

```bash
# Build image
./podman-run.sh build

# Start container
./podman-run.sh start

# Stop container
./podman-run.sh stop

# View logs
./podman-run.sh logs

# Quick start (build + start)
./podman-run.sh quick
```

### Advanced Commands

```bash
# Run tests
./podman-run.sh test

# Run backtesting
./podman-run.sh backtest

# Check status
./podman-run.sh status

# Clean up everything
./podman-run.sh cleanup
```

## 🐳 Podman Compose (Alternative)

If you prefer using Podman Compose:

```bash
# Build and start with compose
podman-compose up -d

# View logs
podman-compose logs -f

# Stop services
podman-compose down

# Rebuild and start
podman-compose up -d --build
```

## 📊 Accessing the Application

Once running, access the application at:
- **Streamlit App**: http://localhost:8501
- **Container Logs**: `./podman-run.sh logs`

## 🔧 Troubleshooting

### Common Issues

**1. Podman not found**
```bash
# Check if Podman is installed
podman --version

# If not found, install Podman Desktop
# Download from: https://podman-desktop.io/
```

**2. Port already in use**
```bash
# Check what's using port 8501
netstat -ano | findstr :8501

# Stop the process or change port in podman-run.sh
```

**3. Permission denied**
```bash
# Run PowerShell as Administrator
# Or use WSL2 for better compatibility
```

**4. Build fails**
```bash
# Check Dockerfile syntax
# Ensure all files are present
# Try rebuilding: ./podman-run.sh cleanup && ./podman-run.sh build
```

### Windows-Specific Notes

**1. WSL2 Integration**
- Podman Desktop works best with WSL2
- Enable WSL2 in Windows Features
- Install Ubuntu from Microsoft Store

**2. File Permissions**
- Windows file permissions may cause issues
- Use WSL2 for better compatibility
- Or run PowerShell as Administrator

**3. Antivirus Interference**
- Some antivirus software may block Podman
- Add exceptions for Podman Desktop
- Temporarily disable real-time protection

## 🆚 Podman vs Docker

### Advantages of Podman

**1. Rootless Containers**
- Run containers without root privileges
- Better security model
- No daemon required

**2. Windows Native**
- Better Windows integration
- Native Windows containers
- Improved performance

**3. Open Source**
- Completely open source
- No licensing fees
- Community-driven development

**4. Docker Compatible**
- Same commands as Docker
- Same Dockerfile syntax
- Easy migration from Docker

### Migration from Docker

```bash
# If you have Docker containers running
docker stop stockagent
docker rm stockagent

# Switch to Podman
./podman-run.sh quick
```

## 📁 File Structure

```
stockagent/
├── podman-run.sh          # Podman management script
├── podman-compose.yml     # Podman Compose configuration
├── Dockerfile             # Container definition
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables
├── app.py                # Streamlit application
├── backtesting.py        # Backtesting engine
├── trading_algorithms.py # Trading strategies
└── README_PODMAN.md      # This file
```

## 🔍 Monitoring

### Container Status
```bash
# Check container status
./podman-run.sh status

# View running containers
podman ps

# View all containers
podman ps -a
```

### System Resources
```bash
# Check system info
podman system info

# Check disk usage
podman system df

# Prune unused resources
podman system prune
```

## 🚀 Production Deployment

### Using Podman Compose

```bash
# Create production compose file
cp podman-compose.yml podman-compose.prod.yml

# Edit for production settings
# - Add environment variables
# - Configure volumes
# - Set restart policies

# Deploy
podman-compose -f podman-compose.prod.yml up -d
```

### Using Podman Run

```bash
# Production run command
podman run -d \
  --name stockagent-prod \
  -p 8501:8501 \
  -v ./data:/app/data \
  -v ./logs:/app/logs \
  --env-file .env \
  --restart unless-stopped \
  stockagent:latest
```

## 📚 Additional Resources

- **Podman Documentation**: https://docs.podman.io/
- **Podman Desktop**: https://podman-desktop.io/
- **Podman Compose**: https://github.com/containers/podman-compose
- **Windows WSL2**: https://docs.microsoft.com/en-us/windows/wsl/

## 🤝 Support

If you encounter issues:

1. **Check the logs**: `./podman-run.sh logs`
2. **Verify installation**: `podman --version`
3. **Check system resources**: `podman system info`
4. **Try cleanup**: `./podman-run.sh cleanup`

## 🎉 Success!

Once everything is running, you should see:
- ✅ Podman container running
- 🌐 Streamlit app at http://localhost:8501
- 📊 Trading strategies available
- 🔧 Backtesting engine working

**Happy trading with Podman!** 🚀 