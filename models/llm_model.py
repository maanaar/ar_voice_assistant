"""Gemini LLM wrapper (lazy)."""
import asyncio
import traceback
import google.generativeai as genai
import config

_llm_instance = None

class GeminiLLM:
    """Wrapper for Google Gemini LLM with lazy loading."""

    def __init__(self):
        self.model = None

    def _load_model(self):
        if self.model is None:
            print("🤖 Initializing Gemini LLM...")
            genai.configure(api_key=config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(config.GEMINI_MODEL)
            print("✅ Gemini LLM ready")

    async def generate_response(self, user_text: str) -> str:
        try:
            self._load_model()
            prompt = (
                f"{config.GEMINI_SYSTEM_PROMPT}\n\n"
                f"العميل قال: {user_text}\n\n"
                f"رد الموظف:"
            )

            # run blocking call in thread pool
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"❌ Gemini Error: {e}")
            traceback.print_exc()
            return "عذرًا يا فندم، حصل خطأ بسيط في النظام. ممكن تعيد سؤالك؟"

def get_llm_model() -> GeminiLLM:
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = GeminiLLM()
    return _llm_instance
