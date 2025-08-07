# Reverse Proxy Setup for KabusAPI

This guide explains how to set up a reverse proxy to access KabusAPI from containers.

## 🎯 **Problem**

KabusAPI only accepts connections from `localhost`, but containers can't access the host's localhost directly.

## 🔧 **Solution: Nginx Reverse Proxy**

### **Step 1: Install Nginx on Windows**

Download and install nginx from: https://nginx.org/en/download.html

### **Step 2: Set up the Reverse Proxy**

1. **Copy the configuration files to your Windows machine:**
   ```powershell
   # Copy these files to your Windows machine
   nginx-proxy.conf
   setup-proxy.ps1
   ```

2. **Run the setup script:**
   ```powershell
   .\setup-proxy.ps1
   ```

3. **Verify the proxy is working:**
   ```powershell
   # Test locally on Windows
   curl http://localhost:8080/kabusapi/token
   ```

### **Step 3: Update Environment Configuration**

Create a new `.env` file with reverse proxy settings:

```bash
# Copy the proxy example
cp env-proxy-example.txt .env

# Edit with your settings
KABUSAPI_HOST=192.168.1.20  # Your Windows IP
KABUSAPI_PORT=8080           # Reverse proxy port
KABUSAPI_PASSWORD=your_password
```

### **Step 4: Test from Container**

```bash
# Test network connectivity
python test_network_connectivity.py

# Test API connection
python test_api_connection.py
```

## 🌐 **How It Works**

```
Container → 192.168.1.20:8080 → Nginx Proxy → localhost:18081 → KabusAPI
```

1. **Container** connects to Windows IP on proxy port
2. **Nginx** forwards request to localhost:18081
3. **KabusAPI** accepts the localhost connection

## 📋 **Configuration Options**

| Environment | Proxy Port | KabusAPI Port |
|-------------|------------|---------------|
| `dev` | 8080 | 18081 |
| `prod` | 8081 | 18080 |

## 🔍 **Troubleshooting**

### **Proxy not accessible:**
- Check Windows Firewall allows port 8080
- Verify nginx is running: `nginx -s status`

### **Connection refused:**
- Ensure KabusAPI is running on Windows
- Check nginx configuration: `nginx -t`

### **Authentication errors:**
- Verify KabusAPI password is correct
- Check proxy headers are being forwarded

## 🚀 **Running the Application**

```bash
# Build and start with reverse proxy
docker-compose up -d --build

# Or with Podman
./podman-run.sh build
./podman-run.sh start
```

## 📝 **Files**

- `nginx-proxy.conf` - Nginx reverse proxy configuration
- `setup-proxy.ps1` - Windows setup script
- `env-proxy-example.txt` - Environment template for proxy
- `README_REVERSE_PROXY.md` - This guide 