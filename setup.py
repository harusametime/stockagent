#!/usr/bin/env python3
"""
Setup script for StockAgent
"""

import os
import sys
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import streamlit
        import pandas
        import numpy
        import yfinance
        import plotly
        import requests
        print("✅ All required dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Run: pip install -r requirements.txt")
        return False

def setup_environment():
    """Set up the environment file"""
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if not env_example.exists():
        print("❌ .env.example file not found!")
        print("💡 Please ensure you're in the correct directory")
        return False
    
    if env_file.exists():
        print("⚠️ .env file already exists")
        response = input("Do you want to overwrite it? (y/N): ").lower()
        if response != 'y':
            print("📋 Keeping existing .env file")
            return True
    
    try:
        # Copy .env.example to .env
        import shutil
        shutil.copy('.env.example', '.env')
        print("✅ Created .env file from .env.example")
        print("💡 Please edit .env with your API credentials")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def show_next_steps():
    """Show next steps for the user"""
    print("\n" + "="*50)
    print("🚀 SETUP COMPLETE!")
    print("="*50)
    print("\n📋 Next steps:")
    print("1. Edit .env file with your API credentials:")
    print("   - KABUSAPI_PASSWORD=your_actual_password")
    print("   - KABUSAPI_ENV=dev (or prod)")
    print("\n2. Test your setup:")
    print("   python test_api_connection.py")
    print("\n3. Run the application:")
    print("   # Local: streamlit run app.py")
    print("   # Docker: docker-compose up -d")
    print("   # Podman: .\\podman-run.ps1 quick")
    print("\n4. Switch environments:")
    print("   python switch_env.py dev    # Development")
    print("   python switch_env.py prod   # Production")
    print("\n📖 For more information, see README.md")

def main():
    """Main setup function"""
    print("🔧 StockAgent Setup")
    print("="*30)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Set up environment
    if not setup_environment():
        return False
    
    # Show next steps
    show_next_steps()
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 