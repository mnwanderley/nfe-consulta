from langchain_groq import ChatGroq
from config.settings import settings
import logging

logger = logging.getLogger(__name__)


def get_groq_llm():
    """Configura e retorna a instância do LLM Groq com tratamento de erros"""
    try:
        if not settings.GROQ_API_KEY:
            raise ValueError("Chave API Groq não configurada. Defina GROQ_API_KEY no .env")

        return ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name=settings.GROQ_MODEL_NAME,
            temperature=settings.GROQ_TEMPERATURE,
            request_timeout=60
        )
    except Exception as e:
        logger.error(f"Erro ao configurar o LLM Groq: {str(e)}")
        raise