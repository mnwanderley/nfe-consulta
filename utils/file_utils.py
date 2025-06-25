import os
import zipfile
import pandas as pd
from typing import List, Optional
from config.settings import settings
import logging
import csv

logger = logging.getLogger(__name__)

def extract_zip(zip_path: str, extract_to: Optional[str] = None) -> List[str]:
    """Extrai arquivos ZIP para o diretório especificado."""
    extract_to = extract_to or settings.TEMP_EXTRACTION_DIR
    os.makedirs(extract_to, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
            extracted_files = zip_ref.namelist()
        logger.info(f"Arquivos extraídos: {extracted_files}")
        return [os.path.join(extract_to, f) for f in extracted_files]
    except Exception as e:
        logger.error(f"Erro ao extrair arquivo ZIP: {e}")
        raise

def load_csv(file_path: str) -> pd.DataFrame:
    """Carrega um arquivo CSV como DataFrame com suporte a múltiplas codificações."""
    encodings = ['utf-8', 'latin1', 'iso-8859-1']
    separator = None

    try:
        # Detectar o separador
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    try:
                        dialect = csv.Sniffer().sniff(file.read(1024))
                        separator = dialect.delimiter
                        break
                    except:
                        separator = ';'  # Fallback para ponto-e-vírgula
                break
            except UnicodeDecodeError:
                continue

        if not separator:
            separator = ';'  # Último fallback

        # Tentar carregar o CSV
        for encoding in encodings:
            try:
                return pd.read_csv(file_path, encoding=encoding, sep=separator, decimal=',')
            except Exception as e:
                logger.warning(f"Tentativa com codificação {encoding} falhou: {e}")
                continue

        raise ValueError("Não foi possível carregar o CSV com nenhuma codificação suportada.")
    except Exception as e:
        logger.error(f"Erro ao carregar CSV: {e}")
        raise

def find_csv_files(directory: str) -> List[str]:
    """Encontra todos os arquivos CSV em um diretório."""
    csv_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.csv'):
                csv_files.append(os.path.join(root, file))
    return csv_files