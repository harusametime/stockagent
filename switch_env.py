#!/usr/bin/env python3
"""
Helper script to switch between dev and prod environments
"""

import os
import sys
from pathlib import Path

def read_env_file():
    """Read current .env file"""
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found!")
        print("💡 Please copy env_example.txt to .env first")
        return None
    
    with open(env_file, 'r') as f:
        return f.read()

def write_env_file(content):
    """Write content to .env file"""
    with open('.env', 'w') as f:
        f.write(content)

def update_env_environment(environment):
    """Update KABUSAPI_ENV in .env file"""
    content = read_env_file()
    if content is None:
        return False
    
    lines = content.split('\n')
    updated = False
    port_line_removed = False
    
    # Remove old KABUSAPI_PORT line and update/add KABUSAPI_ENV
    for i, line in enumerate(lines):
        if line.startswith('KABUSAPI_ENV='):
            lines[i] = f'KABUSAPI_ENV={environment}'
            updated = True
        elif line.startswith('KABUSAPI_PORT='):
            # Remove old port configuration
            lines[i] = None
            port_line_removed = True
    
    # Remove None lines
    lines = [line for line in lines if line is not None]
    
    if not updated:
        # Add KABUSAPI_ENV if it doesn't exist
        lines.append(f'KABUSAPI_ENV={environment}')
    
    write_env_file('\n'.join(lines))
    return True

def show_current_config():
    """Show current environment configuration"""
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found!")
        return
    
    content = read_env_file()
    if content is None:
        return
    
    print("📋 Current Configuration:")
    print("="*40)
    
    for line in content.split('\n'):
        if line.strip() and not line.startswith('#'):
            if 'PASSWORD' in line:
                # Hide password
                key, value = line.split('=', 1)
                print(f"{key}=***")
            else:
                print(line)
    
    print("="*40)

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("🌐 Environment Switcher")
        print("="*30)
        print("Usage:")
        print("  python switch_env.py dev    # Switch to development (port 18081)")
        print("  python switch_env.py prod   # Switch to production (port 18080)")
        print("  python switch_env.py show   # Show current configuration")
        print("")
        show_current_config()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'show':
        show_current_config()
        return
    
    if command not in ['dev', 'prod']:
        print(f"❌ Invalid environment: {command}")
        print("💡 Use 'dev' or 'prod'")
        return
    
    # Determine port based on environment
    port = '18081' if command == 'dev' else '18080'
    
    print(f"🔄 Switching to {command.upper()} environment...")
    print(f"📡 Port: {port}")
    
    if update_env_environment(command):
        print(f"✅ Successfully switched to {command.upper()} environment!")
        print("")
        show_current_config()
        print("")
        print("💡 Next steps:")
        print(f"  1. Restart your container: docker-compose down && docker-compose up -d")
        print(f"  2. Test connection: python test_api_connection.py")
    else:
        print("❌ Failed to update .env file")

if __name__ == "__main__":
    main() 