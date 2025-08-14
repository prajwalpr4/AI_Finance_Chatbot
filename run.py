#!/usr/bin/env python3
"""
Launcher script for FINOVA - AI Financial Chatbot
Handles environment setup and runs the application
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()



def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}")
        return False
    return True

def check_requirements():
    """Check if required packages are installed"""
    required_packages = [
        'streamlit', 'pandas', 'requests', 'numpy', 'plotly'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install"
            ] + missing_packages)
            print("✅ Packages installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install packages")
            return False
    
    return True

def check_api_key():
    """Check if HuggingFace API key is configured"""
    api_key = os.getenv('HUGGINGFACE_API_KEY')
    
    if not api_key or api_key == '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':
        print("⚠️  HuggingFace API key not found!")
        print("\nTo get an API key:")
        print("1. Go to https://huggingface.co/")
        print("2. Create a free account")
        print("3. Go to Settings → Access Tokens")
        print("4. Create a new token")
        print("5. Set environment variable:")
        
        if os.name == 'nt':  # Windows
            print("   set HUGGINGFACE_API_KEY=your_token_here")
        else:  # macOS/Linux
            print("   export HUGGINGFACE_API_KEY=your_token_here")
        
        # Try to read from config.py as fallback
        try:
            from config import HUGGINGFACE_API_KEY as config_key
            if config_key and config_key != 'YOUR_API_KEY_HERE':
                print("✅ Found API key in config.py")
                return True
        except ImportError:
            pass
        
        response = input("\nContinue anyway? (y/N): ").lower().strip()
        return response == 'y'
    
    print("✅ HuggingFace API key found")
    return True

def check_files():
    """Check if required files exist"""
    required_files = ['enhanced_app.py', 'config.py', 'utils.py']
    missing_files = []
    
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        print("\nPlease ensure all project files are in the current directory:")
        for file in required_files:
            print(f"  - {file}")
        return False
    
    print("✅ All required files found")
    return True

def run_application():
    """Run the Streamlit application"""
    try:
        print("\n🚀 Starting FINOVA - AI Financial Chatbot...")
        print("📱 Opening browser...")
        
        # Start Streamlit
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "enhanced_app.py",
            "--server.headless", "true",
            "--browser.serverAddress", "localhost"
        ])
        
        # Open browser after a short delay
        import time
        time.sleep(3)
        webbrowser.open("http://localhost:8501")
        
        print("✅ FINOVA started successfully!")
        print("🌐 Browser should open automatically at http://localhost:8501")
        print("\nPress Ctrl+C to stop the application")
        
        # Wait for the process
        process.wait()
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down FINOVA...")
        process.terminate()
    except Exception as e:
        print(f"❌ Error starting FINOVA: {e}")
        return False
    
    return True

def main():
    """Main launcher function"""
    print("🤖 FINOVA - AI Financial Chatbot Launcher")
    print("=" * 45)
    
    # Check system requirements
    if not check_python_version():
        sys.exit(1)
    
    # Check and install packages
    if not check_requirements():
        sys.exit(1)
    
    # Check files
    if not check_files():
        sys.exit(1)
    
    # Check API key
    if not check_api_key():
        print("⚠️  Continuing without API key - some features may not work")
    
    # Run the application
    if not run_application():
        sys.exit(1)

if __name__ == "__main__":
    main()