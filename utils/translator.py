import groq
from groq import Groq
import requests
import json

class Translator:
    def __init__(self, api_key):
        self.groq_client = None
        self.translation_method = None
        self.libretranslate_endpoints = [
            'https://libretranslate.de',
            'https://translate.argosopentech.com',
            'https://libretranslate.com',
        ]
        
        # Try Groq first
        if api_key:
            try:
                self.groq_client = Groq(api_key=api_key)
                self.translation_method = 'groq'
                print("✅ Groq translator initialized")
            except Exception as e:
                print(f"⚠️ Failed to initialize Groq: {e}")
        
        # If Groq fails, try LibreTranslate API (free, no key needed)
        if not self.groq_client:
            for endpoint in self.libretranslate_endpoints:
                try:
                    response = requests.get(f'{endpoint}/detect', timeout=3)
                    if response.status_code == 200:
                        self.libretranslate_endpoint = endpoint
                        self.translation_method = 'libretranslate'
                        print(f"✅ LibreTranslate translator initialized ({endpoint})")
                        break
                except:
                    pass
        
        # If LibreTranslate fails, try mymemory API (free, no auth needed)
        if not self.translation_method:
            try:
                response = requests.get('https://mymemory.translated.net/api/get?q=test&langpair=en|es', timeout=3)
                if response.status_code == 200:
                    self.translation_method = 'mymemory'
                    print("✅ MyMemory translator initialized (free alternative)")
            except:
                pass
        
        # If both fail, try Google Translate (unofficial)
        if not self.translation_method:
            try:
                from google_trans_new import google_translator
                self.google_translator = google_translator()
                self.translation_method = 'google'
                print("✅ Google Translate initialized (free alternative)")
            except:
                print("⚠️ All translation services unavailable. Installing fallback...")
                self.translation_method = 'text_only'
    
    def translate_text(self, text, source_lang, target_lang):
        """Translate text using available service"""
        if not text or not text.strip():
            return ""
        
        # Try each available method
        if self.translation_method == 'groq':
            result = self._translate_groq(text, source_lang, target_lang)
            if result and not result.startswith("Translation failed"):
                return result
            print("⚠️ Groq failed, trying fallback methods...")
        
        # Try LibreTranslate
        result = self._translate_libretranslate(text, source_lang, target_lang)
        if result:
            return result
        
        # Try MyMemory
        result = self._translate_mymemory(text, source_lang, target_lang)
        if result:
            return result
        
        # Try Google Translate as last resort
        result = self._translate_google(text, source_lang, target_lang)
        if result:
            return result
        
        # If all fail, return original text with note
        return text  # Return original text if all services fail
    
    def _translate_groq(self, text, source_lang, target_lang):
        """Translate using Groq API"""
        if not self.groq_client:
            return None
        
        try:
            lang_names = {
                'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German',
                'it': 'Italian', 'pt': 'Portuguese', 'hi': 'Hindi', 'mr': 'Marathi',
                'zh': 'Chinese (Simplified)', 'ja': 'Japanese', 'ko': 'Korean',
                'ar': 'Arabic', 'ru': 'Russian', 'auto': 'Auto-detect'
            }
            
            source_name = lang_names.get(source_lang, source_lang)
            target_name = lang_names.get(target_lang, target_lang)
            
            if source_lang == 'auto':
                prompt = f"""You are a professional translator. 
First, detect the language of the following text, then translate it to {target_name}.
Maintain the original meaning, tone, and formatting.

Text to translate:
{text}

Please provide ONLY the translated text in {target_name}, nothing else."""
            else:
                prompt = f"""You are a professional translator.
Translate the following text from {source_name} to {target_name}.
Maintain the original meaning, tone, and formatting.

Text to translate:
{text}

Please provide ONLY the translated text in {target_name}, nothing else."""
            
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": f"You are a professional translator. Translate text accurately to {target_name}."},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.3,
                max_tokens=2048,
                top_p=1,
                stream=False
            )
            
            translated = chat_completion.choices[0].message.content.strip()
            print(f"✅ Translation successful (Groq): {source_lang} → {target_lang}")
            return translated
        except Exception as e:
            print(f"❌ Groq translation error: {str(e)}")
            return None
    
    def _translate_libretranslate(self, text, source_lang, target_lang):
        """Translate using LibreTranslate (free alternative)"""
        try:
            lang_map = {
                'auto': 'auto', 'en': 'en', 'es': 'es', 'fr': 'fr', 'de': 'de',
                'it': 'it', 'pt': 'pt', 'hi': 'hi', 'zh': 'zh', 'ja': 'ja',
                'ko': 'ko', 'ar': 'ar', 'ru': 'ru', 'mr': 'mr'
            }
            
            src = lang_map.get(source_lang, source_lang)
            tgt = lang_map.get(target_lang, target_lang)
            
            # Try all available endpoints
            for endpoint in self.libretranslate_endpoints:
                try:
                    payload = {
                        "q": text,
                        "source": src if src != 'auto' else 'auto',
                        "target": tgt,
                        "format": "text"
                    }
                    
                    response = requests.post(f'{endpoint}/translate', json=payload, timeout=5)
                    if response.status_code == 200:
                        result = response.json().get('translatedText', '')
                        if result:
                            print(f"✅ Translation successful (LibreTranslate): {source_lang} → {target_lang}")
                            return result
                except:
                    continue
        except Exception as e:
            print(f"⚠️ LibreTranslate failed: {str(e)}")
        
        return None
    
    def _translate_mymemory(self, text, source_lang, target_lang):
        """Translate using MyMemory API (free, no API key needed)"""
        try:
            lang_map = {
                'auto': 'en', 'en': 'en', 'es': 'es', 'fr': 'fr', 'de': 'de',
                'it': 'it', 'pt': 'pt', 'hi': 'hi', 'zh': 'zh-CN', 'ja': 'ja',
                'ko': 'ko', 'ar': 'ar', 'ru': 'ru', 'mr': 'hi'  # Marathi not supported, use Hindi
            }
            
            src = lang_map.get(source_lang, 'en')
            tgt = lang_map.get(target_lang, 'en')
            
            # Limit text length for MyMemory (max 500 chars per request)
            if len(text) > 500:
                # Split text and translate in chunks
                chunks = [text[i:i+500] for i in range(0, len(text), 500)]
                translated_chunks = []
                for chunk in chunks:
                    try:
                        response = requests.get(
                            f'https://mymemory.translated.net/api/get?q={requests.utils.quote(chunk)}&langpair={src}|{tgt}',
                            timeout=5
                        )
                        if response.status_code == 200:
                            data = response.json()
                            if data.get('responseStatus') == 200:
                                translated_chunks.append(data['responseData']['translatedText'])
                    except:
                        pass
                
                if translated_chunks:
                    result = ''.join(translated_chunks)
                    print(f"✅ Translation successful (MyMemory): {source_lang} → {target_lang}")
                    return result
            else:
                response = requests.get(
                    f'https://mymemory.translated.net/api/get?q={requests.utils.quote(text)}&langpair={src}|{tgt}',
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get('responseStatus') == 200:
                        result = data['responseData']['translatedText']
                        if result and result != text:  # Ensure translation is different
                            print(f"✅ Translation successful (MyMemory): {source_lang} → {target_lang}")
                            return result
        except Exception as e:
            print(f"⚠️ MyMemory failed: {str(e)}")
        
        return None
    
    def _translate_google(self, text, source_lang, target_lang):
        """Translate using Google Translate (free alternative)"""
        try:
            from google_trans_new import google_translator
            translator = google_translator()
            
            lang_map = {
                'auto': 'auto', 'en': 'en', 'es': 'es', 'fr': 'fr', 'de': 'de',
                'it': 'it', 'pt': 'pt', 'hi': 'hi', 'zh': 'zh', 'ja': 'ja',
                'ko': 'ko', 'ar': 'ar', 'ru': 'ru', 'mr': 'mr'
            }
            
            src = lang_map.get(source_lang, source_lang)
            tgt = lang_map.get(target_lang, target_lang)
            
            result = translator.translate(text, lang_tgt=tgt, lang_src=src)
            if result:
                print(f"✅ Translation successful (Google): {source_lang} → {target_lang}")
                return result
        except Exception as e:
            print(f"⚠️ Google Translate failed: {str(e)}")
        
        return None