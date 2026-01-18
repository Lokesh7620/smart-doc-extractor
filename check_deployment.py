#!/usr/bin/env python3
"""
Pre-deployment checker - Verify your application is ready for production
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def print_status(check_name, passed, message=""):
    """Print check status with color"""
    status = "✅" if passed else "❌"
    print(f"{status} {check_name}")
    if message:
        print(f"   {message}")

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    passed = version >= (3, 8)
    print_status(
        "Python Version",
        passed,
        f"Python {version.major}.{version.minor}.{version.micro} {'(OK)' if passed else '(Need 3.8+)'}"
    )
    return passed

def check_env_file():
    """Check .env file exists and has required variables"""
    env_file = Path('.env')
    if not env_file.exists():
        print_status(".env File", False, ".env file not found. Run deploy script first.")
        return False
    
    secret_key = os.getenv('SECRET_KEY')
    if not secret_key or secret_key == 'your-secret-key-here-change-in-production':
        print_status("SECRET_KEY", False, "SECRET_KEY not set or using default. Update .env file.")
        return False
    
    print_status(".env File", True, "Configuration file exists and SECRET_KEY is set")
    return True

def check_database_config():
    """Check database configuration"""
    db_url = os.getenv('DATABASE_URL', 'sqlite:///smart_doc_extractor.db')
    
    if 'sqlite' in db_url.lower():
        print_status(
            "Database",
            True,
            f"Using SQLite (OK for development). Consider PostgreSQL/MySQL for production."
        )
        return True
    else:
        print_status("Database", True, f"Using production database: {db_url.split('@')[0]}...")
        return True

def check_upload_directory():
    """Check upload directory exists and is writable"""
    upload_dir = Path('static/uploads')
    
    if not upload_dir.exists():
        try:
            upload_dir.mkdir(parents=True, exist_ok=True)
            print_status("Upload Directory", True, "Created static/uploads/")
            return True
        except Exception as e:
            print_status("Upload Directory", False, f"Cannot create: {e}")
            return False
    
    # Check if writable
    test_file = upload_dir / '.test_write'
    try:
        test_file.touch()
        test_file.unlink()
        print_status("Upload Directory", True, "Writable")
        return True
    except Exception as e:
        print_status("Upload Directory", False, f"Not writable: {e}")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import flask
        import flask_sqlalchemy
        import flask_login
        print_status("Core Dependencies", True, "Flask and core packages installed")
        core_ok = True
    except ImportError as e:
        print_status("Core Dependencies", False, f"Missing: {e.name}")
        core_ok = False
    
    try:
        import gunicorn
        print_status("Gunicorn (Linux/Mac)", True, "Installed")
    except ImportError:
        print_status("Gunicorn (Linux/Mac)", False, "Not installed (OK if using Windows)")
    
    try:
        import waitress
        print_status("Waitress (Windows)", True, "Installed")
    except ImportError:
        print_status("Waitress (Windows)", False, "Not installed (OK if using Linux/Mac)")
    
    return core_ok

def check_wsgi_file():
    """Check WSGI entry point exists"""
    wsgi_file = Path('wsgi.py')
    if wsgi_file.exists():
        print_status("WSGI Entry Point", True, "wsgi.py exists")
        return True
    else:
        print_status("WSGI Entry Point", False, "wsgi.py not found")
        return False

def check_port_available():
    """Check if port 8000 is available"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('0.0.0.0', 8000))
        sock.close()
        print_status("Port 8000", True, "Available")
        return True
    except OSError:
        print_status("Port 8000", False, "Already in use. Stop existing service or use different port.")
        return False

def print_recommendations():
    """Print deployment recommendations"""
    print("\n" + "="*70)
    print("DEPLOYMENT RECOMMENDATIONS")
    print("="*70)
    
    db_url = os.getenv('DATABASE_URL', 'sqlite:///smart_doc_extractor.db')
    if 'sqlite' in db_url.lower():
        print("\n⚠️  Using SQLite Database")
        print("   Recommendation: Use PostgreSQL or MySQL for production")
        print("   Update DATABASE_URL in .env file")
    
    if not os.getenv('GROQ_API_KEY'):
        print("\n💡 Translation API Not Configured")
        print("   Optional: Get free API key from https://console.groq.com/")
        print("   Add GROQ_API_KEY to .env file for translation features")
    
    print("\n📋 Production Checklist:")
    print("   1. Use production database (PostgreSQL/MySQL)")
    print("   2. Set up HTTPS with Nginx and Let's Encrypt")
    print("   3. Configure firewall (allow only 80, 443)")
    print("   4. Set up automated backups")
    print("   5. Configure monitoring and logging")
    print("   6. Test all features thoroughly")

def main():
    """Run all checks"""
    print("="*70)
    print("PRE-DEPLOYMENT CHECKER - Smart Document Extractor")
    print("="*70)
    print()
    
    checks = []
    
    print("🔍 Running checks...\n")
    
    checks.append(("Python Version", check_python_version()))
    checks.append(("Environment Config", check_env_file()))
    checks.append(("Database Config", check_database_config()))
    checks.append(("Upload Directory", check_upload_directory()))
    checks.append(("Dependencies", check_dependencies()))
    checks.append(("WSGI Entry Point", check_wsgi_file()))
    checks.append(("Port Availability", check_port_available()))
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, status in checks if status)
    total = len(checks)
    
    print(f"\nPassed: {passed}/{total} checks")
    
    if passed == total:
        print("\n✅ All checks passed! Your application is ready to deploy.")
        print("\n🚀 Deploy with:")
        if sys.platform == 'win32':
            print("   waitress-serve --host=0.0.0.0 --port=8000 wsgi:app")
        else:
            print("   gunicorn --bind 0.0.0.0:8000 --workers 4 wsgi:app")
    else:
        print(f"\n⚠️  {total - passed} check(s) failed. Please fix the issues above.")
        print("\nRun deployment setup:")
        print("   python deploy.py")
    
    print_recommendations()
    
    print("\n📖 For detailed deployment guide, see: DEPLOYMENT.md")
    print("="*70 + "\n")
    
    return 0 if passed == total else 1

if __name__ == '__main__':
    sys.exit(main())
