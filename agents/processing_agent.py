from langchain.tools import tool
#import pandas as pd
import logging
from typing import Dict
from utils.file_utils import load_csv

logger = logging.getLogger(__name__)

class ProcessingAgent:
    @tool("Process CSV data")
    def process_csv_data(csv_path: str) -> Dict:
        """
        Carrega e pré-processa os dados do CSV, retornando um formato serializável.

        Args:
            csv_path: Caminho para o arquivo CSV

        Returns:
            Dicionário com os dados processados e metadados
        """
        try:
            logger.info(f"Processando arquivo CSV: {csv_path}")

            # Carrega o CSV usando a função corrigida
            df = load_csv(csv_path)

            # Pré-processamento básico
            df = df.dropna(how='all')
            df = df.fillna('')

            # Converte para formato serializável
            processed_data = {
                'data': df.to_dict(orient='records'),
                'metadata': {
                    'columns': list(df.columns),
                    'num_rows': len(df),
                    'sample': df.head(1).to_dict(orient='records')[0] if not df.empty else {}
                }
            }

            logger.info("Processamento concluído com sucesso")
            return processed_data
        except Exception as e:
            logger.error(f"Erro no processamento: {e}")
            return {'error': str(e)}