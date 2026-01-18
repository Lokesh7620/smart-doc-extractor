#!/usr/bin/env python3
"""
Quick Public Deployment using ngrok
This provides immediate public access for testing/demo purposes
"""
import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def check_ngrok():
    """Check if ngrok is installed"""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_ngrok():
    """Guide user to install ngrok"""
    print("\n" + "="*70)
    print("NGROK INSTALLATION REQUIRED")
    print("="*70)
    print("\nngrok provides instant public URLs for your local server.")
    print("\nInstallation steps:")
    print("1. Download from: https://ngrok.com/download")
    print("2. Extract the zip file")
    print("3. Move ngrok.exe to C:\\Windows\\System32\\ (or add to PATH)")
    print("4. Sign up at https://dashboard.ngrok.com/signup")
    print("5. Run: ngrok config add-authtoken YOUR_AUTH_TOKEN")
    print("\nAfter installation, run this script again.")
    print("="*70)
    return False

def start_waitress():
    """Start Waitress server in background"""
    print("\n🚀 Starting Waitress production server...")
    
    # Activate virtual environment and start Waitress
    venv_path = Path(__file__).parent / 'venv'
    waitress_cmd = str(venv_path / 'Scripts' / 'waitress-serve.exe')
    
    if not Path(waitress_cmd).exists():
        print("❌ Waitress not found. Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'waitress'])
        waitress_cmd = 'waitress-serve'
    
    # Start Waitress
    cmd = [
        waitress_cmd if Path(waitress_cmd).exists() else 'waitress-serve',
        '--host=127.0.0.1',  # Only local for ngrok tunneling
        '--port=8000',
        '--threads=4',
        'wsgi:app'
    ]
    
    try:
        process = subprocess.Popen(
            cmd,
            cwd=str(Path(__file__).parent),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(3)  # Wait for server to start
        
        if process.poll() is None:
            print("✅ Waitress server started on http://127.0.0.1:8000")
            return process
        else:
            print("❌ Waitress failed to start")
            return None
    except Exception as e:
        print(f"❌ Error starting Waitress: {e}")
        return None

def start_ngrok():
    """Start ngrok tunnel"""
    print("\n🌐 Starting ngrok tunnel...")
    
    try:
        # Start ngrok
        process = subprocess.Popen(
            ['ngrok', 'http', '8000', '--log=stdout'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for ngrok to start and get URL
        time.sleep(3)
        
        # Get ngrok public URL from API
        import json
        import urllib.request
        
        try:
            with urllib.request.urlopen('http://127.0.0.1:4040/api/tunnels') as response:
                data = json.loads(response.read())
                public_url = data['tunnels'][0]['public_url']
                
                print("\n" + "="*70)
                print("✅ PUBLIC URL READY!")
                print("="*70)
                print(f"\n🌍 Your app is now publicly accessible at:")
                print(f"\n    {public_url}")
                print(f"\n📱 Share this URL with anyone to access your app")
                print("\n⚠️  This URL is temporary and will change when you restart ngrok")
                print("⚠️  For permanent URLs, upgrade to ngrok paid plan or use cloud deployment")
                print("\n📊 View traffic dashboard: http://127.0.0.1:4040")
                print("\nPress Ctrl+C to stop the server")
                print("="*70 + "\n")
                
                # Open browser
                webbrowser.open(public_url)
                
                return process
        except Exception as e:
            print(f"⚠️  ngrok started but couldn't fetch URL: {e}")
            print("Check http://127.0.0.1:4040 for your public URL")
            return process
            
    except Exception as e:
        print(f"❌ Error starting ngrok: {e}")
        return None

def main():
    """Main deployment function"""
    print("\n" + "="*70)
    print("PUBLIC DEPLOYMENT - NGROK TUNNEL")
    print("="*70)
    
    # Check if .env exists
    env_file = Path(__file__).parent / '.env'
    if not env_file.exists():
        print("❌ .env file not found. Run deploy.py first.")
        return
    
    # Check ngrok installation
    if not check_ngrok():
        install_ngrok()
        return
    
    print("\n✅ ngrok is installed")
    
    # Start Waitress server
    waitress_process = start_waitress()
    if not waitress_process:
        print("\n❌ Failed to start Waitress. Check the error above.")
        return
    
    # Start ngrok tunnel
    ngrok_process = start_ngrok()
    if not ngrok_process:
        print("\n❌ Failed to start ngrok. Check the error above.")
        waitress_process.terminate()
        return
    
    # Keep running
    try:
        print("✅ Server is running. Press Ctrl+C to stop.\n")
        ngrok_process.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping servers...")
        ngrok_process.terminate()
        waitress_process.terminate()
        print("✅ Servers stopped.")

if __name__ == '__main__':
    main()
