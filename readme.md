# Smart Document Extractor 📄

AI-Powered OCR & Translation System for Documents

## 🚀 Quick Start

### Option 1: PowerShell (Recommended)
```powershell
.\run_app.ps1
```

### Option 2: Batch File
```cmd
run_app.bat
```

### Option 3: Python Script
```bash
python run_app.py
```

### Option 4: Manual Setup
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

# Step 1: Create virtual environment
python -m venv venv

# Step 2: Activate virtual environment
.\venv\Scripts\activate

# Step 3: Install dependencies
pip install -r requirements.txt

# Step 4: Run the application
python app.py
```

The app will be available at: **http://127.0.0.1:5000**

---

## ✨ Features

### 📸 Advanced OCR Processing
- **Multiple OCR Engines**: EasyOCR + Tesseract (with fallbacks for TrOCR & PaddleOCR)
- **Intelligent Preprocessing**: Specialized image enhancement for handwritten and printed text
- **Confidence Scoring**: Detailed confidence metrics for extracted text
- **Text Quality Analysis**: Automatic detection of text quality issues

### 🔍 Text Extraction Improvements
- **Advanced Text Cleanup**: Fixes 50+ common OCR errors
- **Language Detection**: Automatic text type (handwritten/printed/mixed) detection
- **Multi-Method Voting**: Compares results from multiple OCR engines
- **Smart Result Selection**: Chooses the best result based on quality and confidence

### 🌐 Translation (Optional)
- Translate extracted text to any language
- Requires: Free Groq API key from https://console.groq.com/keys

### 📄 PDF Generation
- Convert extracted text to professional PDF documents
- Customizable formatting and styling

### 👥 User Management
- Secure login and registration
- Per-user document management
- Document history and tracking

---

## 🛠️ System Requirements

- **Python**: 3.8+
- **RAM**: 4GB minimum (8GB recommended)
- **Disk**: 2GB for models and cache
- **GPU**: Optional (CPU works fine)

### Optional System Dependencies
- **Tesseract-OCR**: For improved text extraction
  - Windows: Download installer from https://github.com/UB-Mannheim/tesseract/wiki
  - Linux: `sudo apt-get install tesseract-ocr`
  - macOS: `brew install tesseract`

---

## 📦 Installation

```bash
# 1. Clone or download the project
cd project-folder

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the application
python app.py
```

---

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
# Translation API (optional)
GROQ_API_KEY=your_groq_api_key_here

# Tesseract Path (auto-detected, override if needed)
TESSERACT_CMD=C:/Program Files/Tesseract-OCR/tesseract.exe

# Database (optional)
DATABASE_URL=sqlite:///smart_doc_extractor.db
```

### API Configuration
All APIs are optional and free:
- **Groq**: https://console.groq.com/keys (free)
- **Tesseract**: Open-source OCR engine (free)
- **EasyOCR**: ML-based OCR (free, downloads ~500MB on first use)

---

## 📊 Accuracy Improvements

### Text Extraction Enhancements
- ✅ Advanced preprocessing with CLAHE (Contrast Limited Adaptive Histogram Equalization)
- ✅ Bilateral filtering for noise reduction
- ✅ Morphological operations for text connectivity
- ✅ Adaptive thresholding for better text separation
- ✅ Automatic text type detection (handwritten vs printed)
- ✅ 50+ common OCR error fixes
- ✅ Confidence-weighted result selection
- ✅ Multi-engine voting system

### Quality Metrics
- **Confidence Score**: 0-100% reliability of extraction
- **Quality Level**: Poor/Fair/Good classification
- **Text Type**: Handwritten/Printed/Mixed detection
- **Issue Detection**: Automatic warning for problematic text

---

## 🎯 How It Works

### 1. Image Upload
- Drop image or use camera
- Supported formats: PNG, JPG, JPEG, PDF

### 2. Preprocessing
- Enhance contrast and sharpness
- Remove noise
- Apply adaptive thresholding
- Optimize for text recognition

### 3. OCR Processing
- Run multiple OCR engines in parallel
- Each engine processes the image independently
- Results scored by confidence and quality

### 4. Result Selection
- Compare results from all engines
- Select best based on confidence + quality
- Apply aggressive text cleanup

### 5. Final Output
- Clean, readable text
- Confidence metrics
- Quality assessment
- Text type classification

---

## 🐛 Troubleshooting

### Error: "No OCR service is available"
**Solution**: Ensure EasyOCR is installed
```bash
pip install easyocr
```

### Error: "Module not found"
**Solution**: Reinstall dependencies
```bash
pip install -r requirements.txt --upgrade --force-reinstall
```

### Slow text extraction
**Solution**: Enable GPU acceleration (if you have NVIDIA GPU)
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Tesseract not found
**Solution**: Install Tesseract or set TESSERACT_CMD in .env
```bash
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
# Then add to .env:
TESSERACT_CMD=C:/Program Files/Tesseract-OCR/tesseract.exe
```

---

## 📈 Performance Tips

1. **Use High-Quality Images**: Better lighting = better results
2. **Position Documents Flat**: Avoid angles and shadows
3. **Increase Image Resolution**: 300+ DPI recommended
4. **Keep Text Black on White**: Best for OCR
5. **Avoid Watermarks**: They interfere with extraction

---

## 🤝 API Endpoints

### Authentication
- `POST /login` - User login
- `POST /register` - New user registration
- `GET /logout` - User logout

### Document Management
- `POST /upload` - Upload and extract text
- `GET /dashboard` - View your documents
- `POST /delete_document/<id>` - Delete document
- `POST /reprocess/<id>` - Reprocess with different method

### Processing
- `POST /translate` - Translate extracted text
- `POST /generate_pdf/<id>` - Generate PDF
- `GET /extract` - Extract page

---

## 📝 License

This project is provided as-is for educational and commercial use.

## 🙏 Credits

- **EasyOCR**: https://github.com/JaidedAI/EasyOCR
- **Tesseract**: https://github.com/UB-Mannheim/tesseract/wiki
- **Flask**: https://flask.palletsprojects.com/
- **Groq API**: https://console.groq.com/

---

## � Production Deployment

Ready to deploy? See the comprehensive [DEPLOYMENT.md](DEPLOYMENT.md) guide for:

### Quick Deploy Options:
1. **Windows**: `.\deploy.ps1`
2. **Linux/Mac**: `./deploy.sh`
3. **Docker**: `docker-compose up -d`
4. **Python**: `python deploy.py`

### Deployment Methods:
- ⭐ **Gunicorn** (Linux/Mac) - Production WSGI server
- ⭐ **Waitress** (Windows) - Windows-compatible server
- 🐳 **Docker** - Containerized deployment
- ☁️ **Cloud**: Heroku, AWS, Google Cloud, Azure

### Production Features:
- Secure configuration with environment variables
- PostgreSQL/MySQL database support
- SSL/HTTPS setup with Nginx
- Systemd service configuration
- Automated deployment scripts
- Monitoring and logging
- Docker containerization

**📖 Full deployment guide**: [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the Flask debug output in console
3. Ensure all dependencies are installed: `pip install -r requirements.txt`
4. For deployment issues, see [DEPLOYMENT.md](DEPLOYMENT.md)

---

**Version**: 2.0 (Enhanced with Improved OCR Accuracy)
**Last Updated**: January 2026