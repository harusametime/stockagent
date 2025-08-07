# Windows Setup Automation

This guide explains how to use the automated Windows setup script for StockAgent.

## 🚀 **Quick Start**

### **Step 1: Run as Administrator**

Open PowerShell as Administrator and navigate to your StockAgent directory:

```powershell
# Navigate to StockAgent directory
cd C:\path\to\stockagent

# Run the setup script
.\setup-windows.ps1
```

### **Step 2: What the Script Does**

The script automatically:

1. ✅ **Installs Nginx** (downloads and configures)
2. ✅ **Sets up reverse proxy** (configures nginx for KabusAPI)
3. ✅ **Starts the proxy** (runs nginx on port 8080)
4. ✅ **Tests the connection** (verifies proxy works)
5. ✅ **Configures environment** (updates .env file)
6. ✅ **Shows next steps** (provides guidance)

## 📋 **Prerequisites**

- **Windows 10/11** or **Windows Server**
- **PowerShell 5.1+** (included with Windows 10/11)
- **Administrator privileges**
- **Internet connection** (for nginx download)
- **KabusAPI running** on localhost:18081

## 🔧 **Script Parameters**

You can customize the setup:

```powershell
# Use custom parameters
.\setup-windows.ps1 -NginxVersion "1.24.0" -InstallPath "D:\nginx" -ProxyPort "8080"
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `NginxVersion` | "1.24.0" | Nginx version to install |
| `InstallPath` | "C:\nginx" | Installation directory |
| `ProxyPort` | "8080" | Proxy port number |

## 📊 **What Gets Installed**

### **Nginx Installation:**
- **Download**: Official nginx from nginx.org
- **Install**: Extracts to `C:\nginx\`
- **PATH**: Adds nginx to system PATH
- **Cleanup**: Removes temporary files

### **Configuration:**
- **Proxy**: Listens on `0.0.0.0:8080`
- **Backend**: Forwards to `localhost:18081`
- **Headers**: Proper proxy headers for KabusAPI

### **Environment:**
- **Host**: `host.containers.internal`
- **Port**: `8080` (proxy port)
- **Template**: Uses `env-proxy-example.txt`

## 🔍 **Troubleshooting**

### **Administrator Privileges Required**
```powershell
# Error: "This script requires administrator privileges"
# Solution: Right-click PowerShell → "Run as administrator"
```

### **Nginx Already Installed**
```powershell
# Script detects existing nginx installation
# Will skip download and use existing version
```

### **Port Already in Use**
```powershell
# Error: "Failed to start Nginx"
# Solution: Change port or stop existing service
.\setup-windows.ps1 -ProxyPort "8081"
```

### **KabusAPI Not Running**
```powershell
# Error: "Proxy connection test failed"
# Solution: Start KabusAPI on localhost:18081 first
```

## 🛠️ **Manual Override**

If the script fails, you can run steps manually:

```powershell
# 1. Install nginx manually
# Download from: https://nginx.org/en/download.html

# 2. Run individual functions
.\setup-windows.ps1 -Function "Install-Nginx"
.\setup-windows.ps1 -Function "Setup-NginxProxy"
.\setup-windows.ps1 -Function "Start-NginxProxy"
```

## 📝 **Post-Setup**

After successful setup:

### **Test the Proxy:**
```powershell
# Test locally
curl http://localhost:8080/kabusapi/token

# Test from container
docker run --rm curlimages/curl curl http://host.containers.internal:8080/kabusapi/token
```

### **Run the Application:**
```powershell
# Docker
docker-compose up -d --build

# Podman
.\podman-run.ps1 build
.\podman-run.ps1 start
```

### **Access the App:**
```
http://localhost:8501
```

## 🔧 **Nginx Management**

After setup, manage nginx with:

```powershell
# Start nginx
nginx

# Stop nginx
nginx -s stop

# Reload configuration
nginx -s reload

# Test configuration
nginx -t

# Check status
nginx -s status
```

## 📖 **Files**

- `setup-windows.ps1` - Main automation script
- `nginx-proxy.conf` - Nginx configuration template
- `env-proxy-example.txt` - Environment template
- `README_WINDOWS_SETUP.md` - This guide

## 🎯 **Success Indicators**

When setup is complete, you should see:

```
🎉 SETUP COMPLETE!
============================================================

📋 Next steps:
1. Test the proxy connection:
   python test_network_connectivity.py
   python test_api_connection.py

2. Run the application:
   docker-compose up -d --build
   or
   .\podman-run.ps1 build
   .\podman-run.ps1 start

3. Access the application:
   http://localhost:8501
```

## 🚨 **Security Notes**

- **Administrator privileges** required for installation
- **Windows Firewall** may need to allow port 8080
- **Antivirus software** may block nginx download
- **Corporate networks** may restrict downloads 