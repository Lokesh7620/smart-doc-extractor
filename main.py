from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, Document
from utils.translator import Translator
from utils.pdf_generator import PDFGenerator
from config import Config
import os
import uuid

# Import appropriate OCR processor based on environment
try:
    from utils.advanced_ocr_processor import AdvancedOCRProcessor
    ocr_processor = AdvancedOCRProcessor()
    print("[INFO] Using Advanced OCR Processor (full features)")
except ImportError as e:
    print(f"[INFO] Advanced OCR not available, using lightweight version: {e}")
    from utils.lightweight_ocr_processor import LightweightOCRProcessor
    ocr_processor = LightweightOCRProcessor()
    print("[INFO] Using Lightweight OCR Processor (Tesseract only)")

main = Blueprint('main', __name__)

# Initialize processors
pdf_generator = PDFGenerator()
translator = Translator(Config.GROQ_API_KEY) if Config.GROQ_API_KEY else None

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    documents = Document.query.filter_by(user_id=current_user.id).order_by(
        Document.created_at.desc()
    ).all()
    return render_template('dashboard.html', documents=documents)

@main.route('/extract')
@login_required
def extract():
    return render_template('extract.html', languages=Config.SUPPORTED_LANGUAGES)

@main.route('/upload', methods=['POST'])
@login_required
def upload_file():
    try:
        # Check OCR availability first
        if not ocr_processor.is_available():
            return jsonify({
                'error': 'No OCR service is available. Please check the installation.',
                'available_methods': ocr_processor.get_available_methods(),
                'installation_help': 'Run: pip install -r requirements.txt'
            }), 500
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            try:
                # Generate unique filename
                filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
                filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
                
                # Create upload directory if it doesn't exist
                os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
                
                file.save(filepath)
                print(f"[INFO] File saved: {filepath}")
                
                # Show available OCR methods
                print(f"[INFO] Available OCR methods: {ocr_processor.get_available_methods()}")
                
                # Extract text using advanced OCR processor
                extraction_result = ocr_processor.extract_text(filepath)
                
                # Check if extraction was successful
                if extraction_result['confidence'] < 0.2 or not extraction_result['text']:
                    # Try different methods if first attempt failed
                    all_methods = ocr_processor.get_available_methods()
                    for method in all_methods:
                        if method != extraction_result.get('method'):
                            print(f"[INFO] Retrying with {method}...")
                            try:
                                retry_result = ocr_processor.extract_text(filepath, force_method=method)
                                if retry_result['confidence'] > extraction_result['confidence']:
                                    extraction_result = retry_result
                            except Exception as retry_err:
                                print(f"[WARN] Retry with {method} failed: {retry_err}")
                    
                    if extraction_result['confidence'] < 0.2 or not extraction_result['text']:
                        return jsonify({
                            'error': 'Could not extract meaningful text from the image.',
                            'extracted_text': extraction_result.get('text', ''),
                            'confidence': extraction_result.get('confidence', 0),
                            'method_used': extraction_result.get('method', 'none'),
                            'text_type': extraction_result.get('text_type', 'unknown'),
                            'all_methods_tried': extraction_result.get('all_results', []),
                            'suggestions': [
                                'For handwritten text: Write clearly with dark ink on white paper',
                                'For printed text: Ensure good lighting and clear image',
                                'Take photo from directly above the document',
                                'Avoid shadows and ensure even lighting',
                                'Make sure text is in focus and not blurry',
                                'Try writing in print letters rather than cursive'
                            ]
                        }), 400
                
                # Save to database
                document = Document(
                    filename=filename,
                    original_filename=file.filename,
                    file_path=filepath,
                    extracted_text=extraction_result.get('text', ''),
                    user_id=current_user.id
                )
                db.session.add(document)
                db.session.commit()
                
                extracted_text = extraction_result.get('text', '')
                print(f"[OK] Successfully extracted {len(extracted_text)} characters")
                print(f"[INFO] Method: {extraction_result.get('method', 'unknown')}")
                print(f"[INFO] Confidence: {extraction_result.get('confidence', 0):.2%}")
                print(f"[INFO] Quality: {extraction_result.get('quality', 'unknown')}")
                
                return jsonify({
                    'success': True,
                    'document_id': document.id,
                    'extracted_text': extracted_text,
                    'word_count': len(extracted_text.split()) if extracted_text else 0,
                    'confidence': extraction_result.get('confidence', 0),
                    'method_used': extraction_result.get('method', 'unknown'),
                    'quality': extraction_result.get('quality', 'unknown'),
                    'quality_score': extraction_result.get('quality_details', {}).get('score', 0),
                    'text_type': extraction_result.get('text_type', 'unknown'),
                    'available_methods': ocr_processor.get_available_methods()
                })
                
            except Exception as e:
                print(f"[ERROR] Upload error: {str(e)}")
                import traceback
                traceback.print_exc()
                return jsonify({
                    'error': f'File processing failed: {str(e)}',
                    'help': 'Please try with a different image or check if the file is corrupted.'
                }), 500
        
        return jsonify({'error': 'Invalid file type. Please select PNG, JPG, JPEG, or PDF files.'}), 400
    
    except Exception as e:
        print(f"❌ Unexpected error in upload_file: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'An unexpected error occurred: {str(e)}'
        }), 500

@main.route('/translate', methods=['POST'])
@login_required
def translate():
    data = request.get_json()
    document_id = data.get('document_id')
    target_lang = data.get('target_language')
    source_lang = data.get('source_language', 'en')
    
    if not translator:
        return jsonify({'error': 'Translation service not available. Please configure GROQ_API_KEY.'}), 500
    
    if not document_id:
        return jsonify({'error': 'No document ID provided'}), 400
    
    if source_lang == target_lang and source_lang != 'auto':
        return jsonify({
            'error': 'Source and target languages must be different',
            'suggestion': 'Please select different languages or use auto-detect for source'
        }), 400
    
    try:
        document = Document.query.get_or_404(document_id)
        
        if document.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        # Translate text
        translated_text = translator.translate_text(
            document.extracted_text, 
            source_lang, 
            target_lang
        )
        
        # Update document
        document.translated_text = translated_text
        document.source_language = source_lang
        document.target_language = target_lang
        db.session.commit()
        
        return jsonify({
            'success': True,
            'translated_text': translated_text
        })
        
    except Exception as e:
        print(f"Translation error: {str(e)}")
        return jsonify({'error': f'Translation failed: {str(e)}'}), 500

@main.route('/generate_pdf/<int:document_id>')
@login_required
def generate_pdf(document_id):
    try:
        document = Document.query.get_or_404(document_id)
        
        if document.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        text_content = document.translated_text or document.extracted_text
        
        if not text_content:
            return jsonify({'error': 'No text content available for PDF generation'}), 400
        
        pdf_filename = f"document_{document_id}_{uuid.uuid4().hex[:8]}.pdf"
        pdf_path = os.path.join(Config.UPLOAD_FOLDER, pdf_filename)
        
        if pdf_generator.create_pdf(text_content, pdf_path, f"Document - {document.original_filename}"):
            document.pdf_path = pdf_path
            db.session.commit()
            
            return send_file(pdf_path, as_attachment=True, download_name=f"{document.original_filename}.pdf")
        else:
            return jsonify({'error': 'Failed to generate PDF'}), 500
            
    except Exception as e:
        print(f"PDF generation error: {str(e)}")
        return jsonify({'error': f'PDF generation failed: {str(e)}'}), 500

@main.route('/delete_document/<int:document_id>', methods=['POST'])
@login_required
def delete_document(document_id):
    try:
        document = Document.query.get_or_404(document_id)
        
        if document.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        if document.pdf_path and os.path.exists(document.pdf_path):
            os.remove(document.pdf_path)
        
        db.session.delete(document)
        db.session.commit()
        
        flash('Document deleted successfully!', 'success')
        return redirect(url_for('main.dashboard'))
        
    except Exception as e:
        print(f"Delete error: {str(e)}")
        flash(f'Failed to delete document: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))

@main.route('/reprocess/<int:document_id>', methods=['POST'])
@login_required
def reprocess_document(document_id):
    """Reprocess document with different OCR method"""
    try:
        document = Document.query.get_or_404(document_id)
        
        if document.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        method = request.json.get('method', None)
        
        # Re-extract text with specified method
        extraction_result = ocr_processor.extract_text(document.file_path, force_method=method)
        
        # Update document
        document.extracted_text = extraction_result['text']
        db.session.commit()
        
        return jsonify({
            'success': True,
            'extracted_text': extraction_result['text'],
            'confidence': extraction_result['confidence'],
            'method_used': extraction_result['method']
        })
        
    except Exception as e:
        print(f"Reprocess error: {str(e)}")
        return jsonify({'error': f'Reprocessing failed: {str(e)}'}), 500