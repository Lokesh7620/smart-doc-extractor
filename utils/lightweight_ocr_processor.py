"""
Lightweight OCR Processor for Cloud Deployment
Only uses Tesseract OCR to fit in free tier memory limits
"""
import os
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
from typing import Dict, List
import re

class LightweightOCRProcessor:
    """Simple OCR processor using only Tesseract"""
    
    def __init__(self):
        self.tesseract_available = self._check_tesseract()
        if self.tesseract_available:
            print("[INFO] Tesseract OCR initialized successfully")
        else:
            print("[WARN] Tesseract OCR not available")
    
    def _check_tesseract(self):
        """Check if Tesseract is available"""
        try:
            pytesseract.get_tesseract_version()
            return True
        except:
            return False
    
    def is_available(self):
        """Check if any OCR method is available"""
        return self.tesseract_available
    
    def get_available_methods(self):
        """Get list of available OCR methods"""
        methods = []
        if self.tesseract_available:
            methods.append('tesseract')
        return methods
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """Enhanced preprocessing for better OCR accuracy"""
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Apply adaptive thresholding
        binary = cv2.adaptiveThreshold(
            denoised, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Dilation and erosion to remove noise
        kernel = np.ones((1, 1), np.uint8)
        processed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        return processed
    
    def calculate_confidence(self, text: str) -> float:
        """Calculate confidence score based on text characteristics"""
        if not text:
            return 0.0
        
        # Check for readable characters
        readable_chars = sum(c.isalnum() or c.isspace() for c in text)
        total_chars = len(text)
        
        if total_chars == 0:
            return 0.0
        
        confidence = readable_chars / total_chars
        
        # Penalize if too many special characters
        special_chars = sum(not (c.isalnum() or c.isspace()) for c in text)
        if special_chars > total_chars * 0.3:
            confidence *= 0.7
        
        return min(confidence, 1.0)
    
    def extract_text_tesseract(self, image_path: str) -> Dict:
        """Extract text using Tesseract OCR"""
        if not self.tesseract_available:
            return {
                'text': '',
                'confidence': 0.0,
                'method': 'tesseract',
                'error': 'Tesseract not available'
            }
        
        try:
            # Preprocess image
            processed_img = self.preprocess_image(image_path)
            
            # Try multiple PSM modes for better results
            psm_modes = [3, 6, 4, 11]  # Different page segmentation modes
            best_result = {'text': '', 'confidence': 0.0}
            
            for psm in psm_modes:
                try:
                    # Configure Tesseract
                    custom_config = f'--oem 3 --psm {psm}'
                    text = pytesseract.image_to_string(processed_img, config=custom_config)
                    
                    # Clean text
                    text = text.strip()
                    confidence = self.calculate_confidence(text)
                    
                    if confidence > best_result['confidence']:
                        best_result = {'text': text, 'confidence': confidence}
                    
                    # If we got good results, break early
                    if confidence > 0.8:
                        break
                except Exception as e:
                    print(f"[WARN] Tesseract PSM {psm} failed: {e}")
                    continue
            
            return {
                'text': best_result['text'],
                'confidence': best_result['confidence'],
                'method': 'tesseract',
                'text_type': 'printed' if best_result['confidence'] > 0.6 else 'unknown',
                'word_count': len(best_result['text'].split())
            }
            
        except Exception as e:
            return {
                'text': '',
                'confidence': 0.0,
                'method': 'tesseract',
                'error': str(e)
            }
    
    def extract_text(self, image_path: str, force_method: str = None) -> Dict:
        """
        Extract text from image using available OCR method
        
        Args:
            image_path: Path to the image file
            force_method: Force a specific OCR method (currently only 'tesseract')
        
        Returns:
            Dictionary with extracted text and metadata
        """
        if not self.is_available():
            return {
                'text': '',
                'confidence': 0.0,
                'method': 'none',
                'error': 'No OCR methods available'
            }
        
        # Use Tesseract (only available method in lightweight version)
        result = self.extract_text_tesseract(image_path)
        
        # Add helpful message if confidence is low
        if result['confidence'] < 0.5:
            result['suggestion'] = (
                "Low confidence detected. For better results with handwritten text, "
                "consider using the full version with TrOCR and PaddleOCR support."
            )
        
        return result
    
    def detect_text_type(self, image_path: str) -> str:
        """
        Detect if text is handwritten or printed
        Simplified version for lightweight deployment
        """
        try:
            # Extract text
            result = self.extract_text(image_path)
            
            # Basic heuristic: if confidence is high, likely printed
            if result['confidence'] > 0.7:
                return 'printed'
            elif result['confidence'] > 0.4:
                return 'mixed'
            else:
                return 'handwritten'
                
        except Exception as e:
            print(f"[ERROR] Text type detection failed: {e}")
            return 'unknown'
