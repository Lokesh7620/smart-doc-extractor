#!/usr/bin/env python3
"""Quick test script to verify OCR functionality"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("🧪 OCR Functionality Test")
print("=" * 60)

# Test 1: Check Python version
print(f"\n✓ Python version: {sys.version}")

# Test 2: Check imports
print("\n📦 Testing imports...")
try:
    import cv2
    print("  ✓ OpenCV")
except ImportError as e:
    print(f"  ✗ OpenCV: {e}")

try:
    from PIL import Image
    print("  ✓ Pillow")
except ImportError as e:
    print(f"  ✗ Pillow: {e}")

try:
    import easyocr
    print("  ✓ EasyOCR")
except ImportError as e:
    print(f"  ✗ EasyOCR: {e}")

try:
    import pytesseract
    print("  ✓ Pytesseract")
except ImportError as e:
    print(f"  ✗ Pytesseract: {e}")

# Test 3: Test OCR processor initialization
print("\n🔧 Testing OCR Processor initialization...")
try:
    from utils.advanced_ocr_processor import AdvancedOCRProcessor
    processor = AdvancedOCRProcessor()
    print(f"  ✓ OCR Processor initialized")
    print(f"  Available methods: {processor.get_available_methods()}")
    
    # Check if we have at least one method
    if processor.get_available_methods():
        print(f"  ✓ At least one OCR method available")
    else:
        print(f"  ✗ NO OCR methods available!")
        
except Exception as e:
    print(f"  ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Test with a simple image if one exists
print("\n📁 Looking for test images...")
test_images = [
    'static/uploads/test.png',
    'static/uploads/test.jpg',
    'images/test.png',
]

for img_path in test_images:
    if os.path.exists(img_path):
        print(f"  Found: {img_path}")
        try:
            result = processor.extract_text(img_path)
            print(f"  Result: {result}")
            if result.get('text'):
                print(f"  ✓ Successfully extracted text")
            else:
                print(f"  ✗ No text extracted")
        except Exception as e:
            print(f"  ✗ Error: {e}")

print("\n" + "=" * 60)
print("✅ Test complete!")
print("=" * 60)
