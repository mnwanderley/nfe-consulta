import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Configurações de diretório
    DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')
    TEMP_EXTRACTION_DIR = os.path.join(DATA_DIR, 'temp_extracted')

    # Configurações de logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # Configurações Groq
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    GROQ_MODEL_NAME = os.getenv('GROQ_MODEL_NAME', 'meta-llama/llama-4-scout-17b-16e-instruct')
    GROQ_TEMPERATURE = float(os.getenv('GROQ_TEMPERATURE', '0.2'))


settings = Settings()