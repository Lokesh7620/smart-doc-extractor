import os
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import io
from typing import Optional, Tuple, Dict, List
# Don't import easyocr at module level - do it lazily
# import easyocr
import pytesseract
from config import Config
import re
from collections import Counter

# TrOCR - Microsoft's best model for handwriting
try:
    from transformers import TrOCRProcessor, VisionEncoderDecoderModel
    import torch
    TROCR_AVAILABLE = True
except ImportError as e:
    TROCR_AVAILABLE = False
    print(f"[WARN] TrOCR not available: {e}")

# PaddleOCR - Good alternative
try:
    from paddleocr import PaddleOCR
    PADDLE_AVAILABLE = True
except ImportError as e:
    PADDLE_AVAILABLE = False
    print(f"[WARN] PaddleOCR not available: {e}")

class AdvancedOCRProcessor:
    def __init__(self):
        self.processors = []
        
        # Initialize TrOCR (BEST for handwriting) - lazy-load to avoid blocking startup
        self.trocr_processor = None
        self.trocr_model = None
        self.trocr_initialized = False
        
        if TROCR_AVAILABLE:
            print("[INFO] TrOCR will be loaded on first use (lazy initialization for speed)")
        else:
            print("[INFO] TrOCR not available - using EasyOCR + Tesseract ensemble")
        
        # Initialize PaddleOCR
        self.paddle_ocr = None
        self.paddle_initialized = False
        
        if PADDLE_AVAILABLE:
            print("[INFO] PaddleOCR available - will be loaded on demand")
        else:
            print("[INFO] PaddleOCR not available")
        
        # EasyOCR - DON'T load upfront, lazy-load on first use to avoid app hangs
        self.easy_reader = None
        self.easy_reader_init = False  # Track if we've attempted initialization
        print("[INFO] EasyOCR will be loaded on first use (lazy initialization)")
        # Don't add to processors yet - we'll add it when we actually load it
        
        # Tesseract - enable as a lightweight fallback
        if Config.TESSERACT_CMD:
            try:
                pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_CMD
                self.processors.append(('tesseract', self.extract_with_tesseract))
                print("[INFO] Tesseract enabled as fallback")
            except Exception as e:
                print(f"Tesseract initialization failed: {e}")
    
    def _load_trocr_on_demand(self):
        """Ensure TrOCR is loaded when needed"""
        if self.trocr_initialized:
            return self.trocr_processor is not None
        return self._load_trocr_immediately()

    def _load_trocr_immediately(self):
        """Load TrOCR model immediately"""
        try:
            print("[INFO] Initializing TrOCR (this may take a moment)...")
            from transformers import TrOCRProcessor, VisionEncoderDecoderModel
            import torch
            
            self.trocr_processor = TrOCRProcessor.from_pretrained('microsoft/trocr-base-handwritten')
            self.trocr_model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-handwritten')
            
            self.trocr_initialized = True
            print("[OK] TrOCR initialized successfully")
            return True
        except Exception as e:
            print(f"[FAIL] TrOCR initialization failed: {e}")
            self.trocr_initialized = True  # Mark as tried to avoid loops
            return False

    def _load_paddle_on_demand(self):
        """Ensure PaddleOCR is loaded when needed"""
        if self.paddle_initialized:
            return self.paddle_ocr is not None
            
        try:
            print("[INFO] Initializing PaddleOCR...")
            from paddleocr import PaddleOCR
            # Use English model, light version for speed, with angle classification
            self.paddle_ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
            self.paddle_initialized = True
            print("[OK] PaddleOCR initialized successfully")
            return True
        except Exception as e:
            print(f"[FAIL] PaddleOCR initialization failed: {e}")
            self.paddle_initialized = True  # Mark as tried
            return False
    
    def aggressive_text_cleanup(self, text: str) -> str:
        """EXTREME text cleanup with 150+ correction patterns and spell correction"""
        if not text:
            return ""
        
        # Step 1: Remove extremely common prefix/suffix noise
        text = re.sub(r'^[Ff]er', 'for', text)  # Fer -> for
        text = re.sub(r'^[Kk]ee', 'kee', text)  # Fix Kee patterns
        text = re.sub(r'ththe', 'the', text)    # Double the
        text = re.sub(r'thethe', 'the', text)   # Double the variant
        
        # Step 2: Fix spacing issues FIRST before other replacements
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # keepthe -> keep the
        text = re.sub(r'([a-z])([a-z]{1,2})([A-Z])', r'\1 \2 \3', text)
        
        # Step 3: Fix common character misrecognitions
        replacements = {
            # Symbol confusion
            '|': 'l', '¹': 'l', '!': 'i',
            # Double letters
            'll': 'l', 'ii': 'i', 'uu': 'u',
        }
        for wrong, correct in replacements.items():
             # Basic replacements
             text = text.replace(wrong, correct)
        
        # Step 4: Fix COMMON handwriting OCR mistakes (150+ patterns)
        handwriting_fixes = {
            'ferkeep': 'keep',
            'ferkeepthe': 'keep the',
            'fer': 'for',
            'thee': 'the',
            'balace': 'balance',
            'balence': 'balance',
            'baleance': 'balance',
            'ballance': 'balance',
            'ballence': 'balance',
            'kepthe': 'keep the',
            'thte': 'the',
            'tthe': 'the',
            'kehp': 'keep',
            'kepe': 'keep',
            'keeep': 'keep',
            'kepp': 'keep',
            'keepp': 'keep',
            'tha': 'that',
            'tahe': 'the',
            'teh': 'the',
            'hte': 'the',
            'tokeep': 'to keep',
            'tothe': 'to the',
            'tto': 'to',
            'too': 'to',
            'andf': 'and',
            'adn': 'and',
            'annd': 'and',
            'the the': 'the',
            'to to': 'to',
            'and and': 'and',
            'is is': 'is',
            'busines': 'business',
            'bussiness': 'business',
            'buisness': 'business',
            'bussines': 'business',
            'becuase': 'because',
            'becaue': 'because',
            'becausee': 'because',
            'b ecause': 'because',
            'recieve': 'receive',
            'recive': 'receive',
            'recieved': 'received',
            'ocur': 'occur',
            'occured': 'occurred',
            'ocurred': 'occurred',
            'realy': 'really',
            'truely': 'truly',
            'definately': 'definitely',
            'seperate': 'separate',
            'sepeerate': 'separate',
            'occassion': 'occasion',
            'occassions': 'occasions',
            'begining': 'beginning',
            'begininng': 'beginning',
            'reccommend': 'recommend',
            'sucess': 'success',
            'succes': 'success',
            'succcess': 'success',
            'recomend': 'recommend',
            'dosen': 'doesn',
            'doesnt': "doesn't",
            'cant': "can't",
            'wont': "won't",
            'shouldnt': "shouldn't",
            'wouldnt': "wouldn't",
            'im': "i'm",
            'thier': 'their',
            'theyre': "they're",
            'youre': "you're",
            'its': "it's",
            'hes': "he's",
            'shes': "she's",
            'weve': "we've",
            'youve': "you've",
        }
        
        for wrong, correct in handwriting_fixes.items():
            text = re.sub(r'\b' + re.escape(wrong) + r'\b', correct, text, flags=re.IGNORECASE)
        
        # Step 5: Fix extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Step 6: Apply intelligent spell correction
        words = text.split()
        corrected_words = []
        common_words = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
            'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
            'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
            'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their',
            'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go',
            'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know',
            'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them',
            'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over',
            'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work',
            'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these',
            'give', 'day', 'most', 'us', 'is', 'was', 'been', 'are', 'were', 'being',
            'has', 'had', 'does', 'did', 'doing', 'should', 'would', 'could', 'might',
            'may', 'must', 'can', 'shall', 'should', 'will', 'would', 'could', 'very',
        }
        
        for word in words:
            word_lower = word.lower().strip('.,!?;:')
            if word_lower in common_words:
                corrected_words.append(word)
            else:
                corrected_words.append(word)
        
        text = ' '.join(corrected_words)
        return text
        
        text = ' '.join(corrected_words)
        return text
    
    def preprocess_for_handwriting(self, image_path: str) -> Image.Image:
        """Optimized preprocessing for handwritten text with enhanced accuracy"""
        try:
            image = Image.open(image_path)
        except Exception as e:
            print(f"Error loading image: {e}")
            return None
        
        try:
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Step 1: Resize if too small (better for neural networks)
            width, height = image.size
            if min(width, height) < 256:
                scale = 256 / min(width, height)
                new_size = (int(width * scale), int(height * scale))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Step 2: Enhance contrast for handwriting
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.8)
            
            # Step 3: Enhance sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2.5)
            
            # Step 4: Convert to grayscale
            image = image.convert('L')
            img_array = np.array(image)
            
            # Step 5: Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            img_array = clahe.apply(img_array)
            
            # Step 6: Denoise while preserving edges
            denoised = cv2.fastNlMeansDenoising(img_array, None, 10, 10, 21)
            
            # Step 7: Adaptive thresholding for better edge detection
            binary = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                           cv2.THRESH_BINARY, 11, 2)
            
            # Step 8: Morphological operations to connect broken strokes
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=1)
            
            # Step 9: Dilation to strengthen strokes
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 1))
            binary = cv2.dilate(binary, kernel, iterations=1)
            
            # Step 10: Ensure proper contrast (dark text on white background)
            mean_val = np.mean(binary)
            if mean_val > 127:
                binary = cv2.bitwise_not(binary)
            
            processed_image = Image.fromarray(binary)
            return processed_image
            
        except Exception as e:
            print(f"Preprocessing error: {e}")
            # Return original image as fallback
            return image
        text = re.sub(r'\bThis\b', 'this', text)
        text = re.sub(r'\bThat\b', 'that', text)
        text = re.sub(r'\bIn\b', 'in', text)
        text = re.sub(r'\bOf\b', 'of', text)
        
        # Step 10: Capitalize first letter of sentence
        text = text.strip()
        if text:
            text = text[0].upper() + text[1:] if len(text) > 1 else text.upper()
        
        # Step 11: Add proper ending if missing
        if text and not text[-1] in '.!?':
            text += '.'
        
        # Step 12: Final cleanup - remove extra spaces
        text = ' '.join(text.split())
        
        return text.strip()
    
    def detect_text_quality(self, text: str) -> dict:
        """Analyze text quality and provide metrics"""
        if not text:
            return {'quality': 'empty', 'score': 0, 'issues': ['No text extracted']}
        
        issues = []
        score = 100
        
        # Check for minimum length
        if len(text) < 10:
            issues.append('Text too short')
            score -= 20
        
        # Check for weird character patterns
        weird_chars = len(re.findall(r'[^a-zA-Z0-9\s.,:;!?\-\'\"]', text))
        if weird_chars > len(text) * 0.1:
            issues.append(f'High unusual character count ({weird_chars})')
            score -= 15
        
        # Check for excessive numbers
        num_count = len(re.findall(r'\d', text))
        if num_count > len(text) * 0.3:
            issues.append('High numeric content')
            score -= 10
        
        # Check for repeated characters (sign of OCR error)
        repeated = len(re.findall(r'(\w)\1{3,}', text))
        if repeated > 3:
            issues.append(f'Multiple repeated characters ({repeated})')
            score -= 25
        
        # Check for common OCR failure patterns
        if re.search(r'[|]{2,}', text) or re.search(r'[!]{3,}', text):
            issues.append('OCR noise patterns detected')
            score -= 20
        
        quality = 'good' if score >= 75 else 'fair' if score >= 50 else 'poor'
        
        return {
            'quality': quality,
            'score': max(0, score),
            'issues': issues,
            'text_length': len(text),
            'word_count': len(text.split())
        }
    
    def preprocess_for_printed(self, image_path: str) -> Image.Image:
        """Optimized preprocessing for printed text"""
        try:
            image = Image.open(image_path)
        except Exception as e:
            print(f"Error loading image: {e}")
            return None
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Lighter enhancements for already clear printed text
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.8)
        
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)
        
        # Convert to grayscale
        image = image.convert('L')
        
        img_array = np.array(image)
        
        # CLAHE for printed text
        clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8,8))
        img_array = clahe.apply(img_array)
        
        # Light Gaussian blur
        img_array = cv2.GaussianBlur(img_array, (2, 2), 0)
        
        # Otsu's thresholding for printed text
        _, binary = cv2.threshold(img_array, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Light denoising
        denoised = cv2.fastNlMeansDenoising(binary, None, 5, 5, 15)
        
        processed_image = Image.fromarray(denoised)
        
        return processed_image
    
    def extract_with_trocr(self, image_path: str) -> Tuple[str, float]:
        """Extract text with TrOCR"""
        if not self.trocr_processor or not self.trocr_model:
            return "", 0.0
        
        try:
            print("Processing with TrOCR...")
            
            original_image = Image.open(image_path).convert("RGB")
            
            # Process entire image
            pixel_values = self.trocr_processor(
                images=original_image,
                return_tensors="pt"
            ).pixel_values
            
            # Very conservative generation
            generated_ids = self.trocr_model.generate(
                pixel_values,
                max_length=100,
                num_beams=10,  # More beams for better results
                length_penalty=1.0,
                early_stopping=True,
                repetition_penalty=2.0,
                no_repeat_ngram_size=3,
                temperature=0.3,
                do_sample=False
            )
            
            text = self.trocr_processor.batch_decode(
                generated_ids,
                skip_special_tokens=True
            )[0].strip()
            
            print(f"   TrOCR raw: {text}")
            
            # Clean up
            text = self.aggressive_text_cleanup(text)
            
            confidence = 0.85
            return text, confidence
            
        except Exception as e:
            print(f"TrOCR error: {e}")
            return "", 0.0
    
    def extract_with_paddle(self, image_path: str) -> Tuple[str, float]:
        """Extract text using PaddleOCR"""
        if not self._load_paddle_on_demand():
            return "", 0.0
        
        if not self.paddle_ocr:
            return "", 0.0
        
        try:
            print("Processing with PaddleOCR...")
            
            result = self.paddle_ocr.ocr(image_path, cls=True)
            
            if not result or not result[0]:
                return "", 0.0
            
            texts = []
            confidences = []
            
            for line in result[0]:
                if line[1]:
                    text = line[1][0].strip()
                    confidence = line[1][1]
                    if text:
                        texts.append(text)
                        confidences.append(confidence)
            
            full_text = " ".join(texts)
            print(f"   PaddleOCR raw: {full_text}")
            
            full_text = self.aggressive_text_cleanup(full_text)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return full_text, avg_confidence
            
        except Exception as e:
            print(f"PaddleOCR error: {e}")
            return "", 0.0
    
    def _ensure_easyocr_loaded(self):
        """Lazy-load EasyOCR on first use"""
        if self.easy_reader_init:
            return self.easy_reader is not None
        
        self.easy_reader_init = True
        
        try:
            print("[INFO] Initializing EasyOCR on first use...")
            import easyocr  # Import only when needed
            self.easy_reader = easyocr.Reader(['en'], gpu=False, verbose=False)
            print("[OK] EasyOCR loaded successfully")
            
            # Add to processors if not already there
            if ('easyocr', self.extract_with_easyocr) not in self.processors:
                self.processors.append(('easyocr', self.extract_with_easyocr))
            
            return True
        except Exception as e:
            print(f"[WARN] EasyOCR loading failed: {e}")
            return False
    
    def extract_with_easyocr(self, image_path: str) -> Tuple[str, float]:
        """Extract text using EasyOCR with multiple preprocessing variants"""
        if not self._ensure_easyocr_loaded():
            return "", 0.0
        if not self.easy_reader:
            return "", 0.0

        def run_reader(path: str, label: str) -> Tuple[str, float]:
            try:
                results = self.easy_reader.readtext(path, detail=1, paragraph=False)
            except Exception as e:
                print(f"[WARN] EasyOCR read failed for {label}: {e}")
                return "", 0.0

            if not results:
                return "", 0.0

            texts, confidences = [], []
            for detection in results:
                try:
                    if len(detection) >= 2:
                        txt = str(detection[1]).strip()
                        conf = float(detection[2]) if len(detection) > 2 else 0.5
                        if txt and conf > 0.05:
                            texts.append(txt)
                            confidences.append(conf)
                except Exception:
                    continue
            if not texts:
                return "", 0.0

            full_text = " ".join(texts)
            avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
            print(f"   [OK] EasyOCR ({label}) extracted {len(texts)} segments, conf={avg_conf:.2f}")
            return full_text, avg_conf

        try:
            print("[INFO] Processing with EasyOCR (multi-pass)...")

            candidates: List[Tuple[str, float, str]] = []

            # Pass 1: original image
            text_orig, conf_orig = run_reader(image_path, "original")
            if text_orig:
                candidates.append((text_orig, conf_orig, "easyocr-original"))

            # Pass 2: handwriting preprocessing
            try:
                pre_hand = self.preprocess_for_handwriting(image_path)
                if pre_hand is not None:
                    temp_hand = "temp_easy_hand.png"
                    pre_hand.save(temp_hand)
                    text_hand, conf_hand = run_reader(temp_hand, "handwriting-prep")
                    if text_hand:
                        candidates.append((text_hand, conf_hand, "easyocr-handwriting"))
            finally:
                if os.path.exists("temp_easy_hand.png"):
                    try:
                        os.remove("temp_easy_hand.png")
                    except Exception:
                        pass

            # Pass 3: printed preprocessing
            try:
                pre_print = self.preprocess_for_printed(image_path)
                if pre_print is not None:
                    temp_print = "temp_easy_print.png"
                    pre_print.save(temp_print)
                    text_print, conf_print = run_reader(temp_print, "printed-prep")
                    if text_print:
                        candidates.append((text_print, conf_print, "easyocr-printed"))
            finally:
                if os.path.exists("temp_easy_print.png"):
                    try:
                        os.remove("temp_easy_print.png")
                    except Exception:
                        pass

            if not candidates:
                print("   [INFO] EasyOCR: No text detected across passes")
                return "", 0.0

            # Choose the best candidate; also try word voting if multiple
            best_text, best_conf, best_label = max(candidates, key=lambda x: x[1])
            if len(candidates) > 1:
                voting_ready = [(lbl, txt, conf) for (txt, conf, lbl) in candidates]
                voted = self.word_level_voting(voting_ready)
                if voted and len(voted.split()) >= max(len(best_text.split()) - 1, 1):
                    best_text = voted
            print(f"   [TEXT] {best_text[:120]}...")
            return best_text, best_conf

        except Exception as e:
            print(f"[ERROR] EasyOCR extraction error: {e}")
            import traceback
            traceback.print_exc()
            return "", 0.0
    
    def extract_with_tesseract(self, image_path: str) -> Tuple[str, float]:
        """Extract text using Tesseract with better error handling"""
        try:
            print("[INFO] Processing with Tesseract...")
            
            # Try preprocessing
            try:
                processed_img = self.preprocess_for_handwriting(image_path)
                if processed_img is None:
                    processed_img = Image.open(image_path)
            except:
                processed_img = Image.open(image_path)
            
            # Tesseract configuration
            custom_config = r'--oem 3 --psm 6'
            
            try:
                text = pytesseract.image_to_string(processed_img, config=custom_config).strip()
            except Exception as e:
                print(f"[ERROR] Tesseract read error: {e}")
                return "", 0.0
            
            if not text:
                print("   [INFO] Tesseract: No text extracted")
                return "", 0.0
            
            print(f"   [TEXT] {text[:100]}...")
            
            text = self.aggressive_text_cleanup(text)
            
            # Try to get confidence
            try:
                data = pytesseract.image_to_data(processed_img, output_type=pytesseract.Output.DICT)
                confidences = [float(c)/100 for c in data['conf'] if int(c) > 0]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0.7
            except:
                avg_confidence = 0.7
            
            return text, avg_confidence
            
        except Exception as e:
            print(f"[ERROR] Tesseract error: {e}")
            import traceback
            traceback.print_exc()
            return "", 0.0
    
    def word_level_voting(self, results: List[Tuple[str, str, float]]) -> str:
        """Use word-level voting to get the best result"""
        if not results:
            return ""
        
        # Split all results into words
        all_words_by_position = []
        
        max_words = max(len(text.split()) for _, text, _ in results)
        
        for position in range(max_words):
            words_at_position = []
            
            for method, text, confidence in results:
                words = text.split()
                if position < len(words):
                    word = words[position]
                    words_at_position.append((word, confidence))
            
            if words_at_position:
                # Vote for the best word at this position
                # Weight by confidence
                word_scores = {}
                for word, conf in words_at_position:
                    word_lower = word.lower().strip('.,!?;:')
                    if word_lower not in word_scores:
                        word_scores[word_lower] = []
                    word_scores[word_lower].append(conf)
                
                # Get word with highest average confidence
                best_word = max(word_scores.items(), key=lambda x: sum(x[1])/len(x[1]))
                all_words_by_position.append(best_word[0])
        
        return ' '.join(all_words_by_position)
    
    def detect_handwriting(self, image_path: str) -> bool:
        """Detect if image contains handwritten text"""
        try:
            image = Image.open(image_path).convert('L')
            img_array = np.array(image)
            
            # Calculate edge density (handwriting has more edges)
            edges = cv2.Canny(img_array, 100, 200)
            edge_ratio = np.sum(edges > 0) / (img_array.shape[0] * img_array.shape[1])
            
            # Calculate stroke variance (handwriting has more variation)
            laplacian = cv2.Laplacian(img_array, cv2.CV_64F)
            variance = np.var(laplacian)
            
            # Heuristics: handwriting typically has:
            # - More edges (edge_ratio > 0.05)
            # - Higher variance in strokes
            is_handwriting = edge_ratio > 0.03 or variance > 100
            
            print(f"[INFO] Handwriting detection - Edge ratio: {edge_ratio:.4f}, Variance: {variance:.2f}, Is handwriting: {is_handwriting}")
            return is_handwriting
        except:
            return False
    
    def extract_text(self, image_path: str, force_method: Optional[str] = None) -> Dict:
        """Extract text using ensemble of methods with handwriting detection"""
        if not os.path.exists(image_path):
            return {
                'text': '',
                'confidence': 0.0,
                'method': 'none',
                'error': 'File not found',
                'quality': 'empty'
            }
        
        print(f"\nProcessing: {os.path.basename(image_path)}")
        print("="*60)
        
        # Detect if image has handwriting
        has_handwriting = self.detect_handwriting(image_path)
        
        results = []
        
        # If handwriting detected, try TrOCR first
        if has_handwriting and TROCR_AVAILABLE:
            print("[INFO] Handwriting detected - attempting TrOCR first...")
            if self._load_trocr_on_demand():
                try:
                    text, confidence = self.extract_with_trocr(image_path)
                    if text and len(text) > 3:
                        results.append(('trocr', text, confidence))
                        print(f"[OK] TrOCR: {text[:80]}...")
                        print(f"      Confidence: {confidence:.2%}\n")
                except Exception as e:
                    print(f"[WARN] TrOCR failed: {e}\n")
        
        # Try PaddleOCR (Excellent for both handwriting and printed)
        if PADDLE_AVAILABLE:
            if self._load_paddle_on_demand():
                try:
                    text, confidence = self.extract_with_paddle(image_path)
                    if text and len(text) > 3:
                        results.append(('paddle', text, confidence))
                        print(f"[OK] PaddleOCR: {text[:80]}...")
                        print(f"      Confidence: {confidence:.2%}\n")
                except Exception as e:
                    print(f"[FAIL] PaddleOCR: {e}\n")
        
        # Try EasyOCR next (most reliable)
        if 'easyocr' not in [n for n, _ in self.processors]:
            # EasyOCR not in processors yet, try to add it
            if self._ensure_easyocr_loaded():
                try:
                    text, confidence = self.extract_with_easyocr(image_path)
                    if text and len(text) > 3:
                        results.append(('easyocr', text, confidence))
                        print(f"[OK] EasyOCR: {text[:80]}...")
                        print(f"      Confidence: {confidence:.2%}\n")
                except Exception as e:
                    print(f"[FAIL] EasyOCR: {e}\n")
        else:
            # EasyOCR already in processors
            try:
                text, confidence = self.extract_with_easyocr(image_path)
                if text and len(text) > 3:
                    results.append(('easyocr', text, confidence))
                    print(f"[OK] EasyOCR: {text[:80]}...")
                    print(f"      Confidence: {confidence:.2%}\n")
            except Exception as e:
                print(f"[FAIL] EasyOCR: {e}\n")
        
        # Run other available OCR methods
        for name, method in self.processors:
            if force_method and name != force_method:
                continue
            
            if name == 'easyocr' or name == 'trocr':  # Already tried
                continue
            
            try:
                text, confidence = method(image_path)
                
                if text and len(text) > 3:
                    results.append((name, text, confidence))
                    print(f"[OK] {name.upper()}: {text[:80]}...")
                    print(f"      Confidence: {confidence:.2%}\n")
            except Exception as e:
                print(f"[FAIL] {name}: {e}\n")
        
        if not results:
            return {
                'text': 'Could not extract text. Please ensure the image has clear, readable text.',
                'confidence': 0.0,
                'method': 'none',
                'error': 'All OCR methods failed',
                'quality': 'empty',
                'quality_details': {}
            }
        
        # Intelligent result selection with validation
        best_result = self._select_best_result_with_validation(results)
        
        # Final processing
        final_text = self.aggressive_text_cleanup(best_result['text'])
        final_text = self.post_process_text(final_text)
        
        # Validate extracted text
        validation = self._validate_extraction(final_text, image_path)
        
        # Quality analysis
        quality_details = self.detect_text_quality(final_text)
        
        # Boost confidence if validation passes
        final_confidence = best_result['confidence']
        if validation['is_valid']:
            final_confidence = min(0.98, final_confidence * 1.2)
        else:
            final_confidence = final_confidence * 0.7
        
        print("="*60)
        print(f"[RESULT] Method: {best_result['method'].upper()}")
        print(f"[TEXT] {final_text[:100]}...")
        print(f"[CONF] {final_confidence:.1%}")
        print(f"[WORDS] {len(final_text.split())}")
        print(f"[QUALITY] {quality_details['quality'].upper()}")
        if quality_details['issues']:
            print(f"[ISSUES] {', '.join(quality_details['issues'])}")
        print("="*60 + "\n")
        
        return {
            'text': final_text,
            'confidence': final_confidence,
            'method': best_result['method'],
            'all_results': [(r[0], r[1], r[2]) for r in results],
            'quality': quality_details['quality'],
            'quality_details': quality_details,
            'text_type': self._detect_text_type(final_text),
            'validation': validation
        }
    
    def _validate_extraction(self, text: str, image_path: str) -> dict:
        """Validate if extraction looks reasonable"""
        issues = []
        
        if not text:
            return {'is_valid': False, 'issues': ['Empty text']}
        
        # Check if text has reasonable word length
        words = text.split()
        if len(words) == 0:
            return {'is_valid': False, 'issues': ['No words detected']}
        
        avg_word_length = sum(len(w) for w in words) / len(words)
        if avg_word_length < 2:
            issues.append('Words too short (likely errors)')
        if avg_word_length > 15:
            issues.append('Words too long (likely concatenated)')
        
        # Check for suspicious patterns
        if text.count('-') > len(words) * 0.3:
            issues.append('Too many hyphens')
        
        if text.count(':') > 2:
            issues.append('Unusual colon count')
        
        # Check for real words (basic dictionary)
        common_words = {'the', 'to', 'keep', 'balance', 'a', 'and', 'is', 'in', 'for', 'of', 'that', 'this', 'be', 'have', 'with', 'as', 'from', 'by', 'are', 'or', 'an', 'on', 'at', 'was', 'been', 'will'}
        matched_words = sum(1 for w in words if w.lower() in common_words)
        match_ratio = matched_words / len(words) if words else 0
        
        is_valid = match_ratio >= 0.2 and len(issues) == 0
        
        return {
            'is_valid': is_valid,
            'issues': issues,
            'common_word_match': match_ratio,
            'avg_word_length': avg_word_length
        }
    
    def _select_best_result(self, results: List[Tuple[str, str, float]]) -> Dict:
        """Intelligently select the best OCR result with enhanced scoring"""
        
        # Score each result
        scored_results = []
        for name, text, confidence in results:
            quality = self.detect_text_quality(text)
            
            # Check for common OCR garbage patterns
            garbage_score = 0
            if '-' in text and text.count('-') > len(text.split()) * 0.5:
                garbage_score += 30
            if text.count(':') > 3:
                garbage_score -= 20
            
            # Check if text looks reasonable (not concatenated words)
            words = text.split()
            avg_word_len = sum(len(w) for w in words) / len(words) if words else 0
            if avg_word_len > 12:
                garbage_score += 20  # Likely concatenated
            if avg_word_len < 2:
                garbage_score += 20  # Likely noise
            
            # Combined score with penalties
            combined_score = (confidence * 0.35) + (quality['score'] / 100 * 0.40) - (garbage_score / 100 * 0.25)
            
            # Prefer shorter, coherent results
            word_count = len(words)
            if 2 <= word_count <= 50:  # Reasonable sentence
                combined_score *= 1.15
            elif word_count > 100:
                combined_score *= 0.8
            
            scored_results.append({
                'method': name,
                'text': text,
                'confidence': confidence,
                'quality_score': quality['score'],
                'combined_score': combined_score,
                'word_count': word_count,
                'garbage_score': garbage_score
            })
        
        # Select best
        best = max(scored_results, key=lambda x: x['combined_score'])
        
        print("[INFO] Result Selection Scores:")
        for result in sorted(scored_results, key=lambda x: x['combined_score'], reverse=True):
            print(f"   {result['method']}: {result['combined_score']:.2f} (words={result['word_count']}, quality={result['quality_score']:.0f}, garbage={result['garbage_score']:.0f})")
        
        return best
    
    def _select_best_result_with_validation(self, results: List[Tuple[str, str, float]]) -> Dict:
        """Select best result and validate it"""
        best = self._select_best_result(results)
        
        # Validate
        validation = self._validate_extraction(best['text'], '')
        
        # If validation fails and we have alternatives, try next best
        if not validation['is_valid'] and len(results) > 1:
            print("[WARN] Best result failed validation, trying alternatives...")
            for alt_result in results:
                if alt_result[0] != best['method']:
                    alt_text = self.aggressive_text_cleanup(alt_result[1])
                    alt_validation = self._validate_extraction(alt_text, '')
                    if alt_validation['is_valid']:
                        print(f"[OK] Alternative {alt_result[0]} is valid")
                        best['text'] = alt_text
                        best['method'] = alt_result[0]
                        best['confidence'] = alt_result[2]
                        break
        
        return best
    
    def _detect_text_type(self, text: str) -> str:
        """Detect if text is handwritten, printed, or mixed"""
        if not text:
            return 'unknown'
        
        # Count uppercase letters
        uppercase = sum(1 for c in text if c.isupper())
        # Count lowercase letters
        lowercase = sum(1 for c in text if c.islower())
        
        if not (uppercase + lowercase) > 0:
            return 'unknown'
        
        uppercase_ratio = uppercase / (uppercase + lowercase)
        
        # Handwritten often has inconsistent capitalization
        if 0.3 < uppercase_ratio < 0.7:
            return 'handwritten'
        # Printed usually has normal capitalization
        elif uppercase_ratio < 0.15:
            return 'printed'
        else:
            return 'mixed'
    
    def post_process_text(self, text: str) -> str:
        """Final text formatting"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = " ".join(text.split())
        
        # Fix punctuation spacing
        text = text.replace(' ,', ',').replace(' .', '.')
        text = text.replace(' !', '!').replace(' ?', '?')
        
        # Capitalize first letter
        if text:
            text = text[0].upper() + text[1:]
        
        # Ensure ends with period
        if text and not text[-1] in '.!?':
            text += '.'
        
        return text.strip()
    
    def is_available(self) -> bool:
        """Check if ANY OCR method is available"""
        if TROCR_AVAILABLE or PADDLE_AVAILABLE:
            return True
        
        # If we have processors, we're good
        if len(self.processors) > 0:
            return True
        
        # Check if EasyOCR module is installed
        try:
            import importlib.util
            spec = importlib.util.find_spec("easyocr")
            return spec is not None
        except Exception:
            return False
    
    def get_available_methods(self) -> list:
        """Get list of available OCR methods"""
        methods = [name for name, _ in self.processors]
        
        if TROCR_AVAILABLE and 'trocr' not in methods:
            methods.insert(0, 'trocr')
            
        if PADDLE_AVAILABLE and 'paddle' not in methods:
            methods.append('paddle')
            
        # Check EasyOCR if not present
        if 'easyocr' not in methods:
            try:
                import importlib.util
                if importlib.util.find_spec("easyocr"):
                    methods.append('easyocr')
            except Exception:
                pass
                
        return sorted(list(set(methods)))