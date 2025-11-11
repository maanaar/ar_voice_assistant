"""Gemini LLM wrapper."""
import asyncio
import traceback
import google.generativeai as genai
import config


class GeminiLLM:
    """Wrapper for Google Gemini LLM."""
    
    def __init__(self):
        """Initialize Gemini model."""
        print("🤖 Configuring Gemini LLM...")
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(config.GEMINI_MODEL)
        print("✅ Gemini LLM configured")
    
    async def generate_response(self, user_text: str) -> str:
        """
        Generate response from user input.
        
        Args:
            user_text: User's input text
            
        Returns:
            Generated response text
        """
        try:
            prompt = f"{config.GEMINI_SYSTEM_PROMPT}\n\nالعميل قال: {user_text}\n\nرد الموظف:"
            
            # Run blocking API call in thread pool
            response = await asyncio.to_thread(
                self.model.generate_content, 
                prompt
            )
            
            return response.text.strip()
            
        except Exception as e:
            print(f"❌ Gemini Error: {e}")
            traceback.print_exc()
            return "عذرًا يا فندم، حصل خطأ بسيط في النظام. ممكن تعيد سؤالك؟"


# Global LLM instance
_llm_instance = None


def get_llm_model() -> GeminiLLM:
    """Get or create global LLM model instance."""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = GeminiLLM()
    return _llm_instance