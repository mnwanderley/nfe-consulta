from typing import Optional
from langchain.tools import tool
from utils.file_utils import find_csv_files, load_csv
import pandas as pd
import logging
from sentence_transformers import SentenceTransformer, util
import numpy as np

logger = logging.getLogger(__name__)

class SelectionAgent:
    def __init__(self):
        """Inicializa o modelo de embeddings."""
        try:
            self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        except Exception as e:
            logger.error(f"Erro ao carregar o modelo de embeddings: {e}")
            raise

    @tool("Select relevant CSV file")
    def select_relevant_csv(self, extracted_files: list, query: str) -> Optional[str]:
        """
        Seleciona o arquivo CSV mais relevante baseado na pergunta do usuário usando embeddings.

        Args:
            extracted_files: Lista de arquivos extraídos
            query: Pergunta do usuário

        Returns:
            Caminho para o arquivo CSV mais relevante ou None
        """
        try:
            logger.info(f"Selecionando CSV relevante para a query: {query}")

            # Encontrar todos os CSVs
            csv_files = []
            for file in extracted_files:
                if file.lower().endswith('.csv'):
                    csv_files.append(file)
                else:
                    csv_files.extend(find_csv_files(file))

            if not csv_files:
                logger.warning("Nenhum arquivo CSV encontrado")
                return None

            # Gerar embedding da query
            query_embedding = self.model.encode(query.lower(), convert_to_tensor=True)

            # Avaliar cada CSV
            similarities = []
            for csv_file in csv_files:
                df = load_csv(csv_file)
                df.columns = df.columns.str.lower()

                # Criar contexto: nome das colunas + amostra de dados
                context_parts = [f"Coluna: {col}" for col in df.columns]
                for col in df.columns[:3]:  # Limitar a 3 colunas pra desempenho
                    sample = df[col].astype(str).head(5).to_list()
                    context_parts.append(f"Amostra de {col}: {', '.join(sample)}")
                context = " ".join(context_parts)

                # Gerar embedding do contexto
                context_embedding = self.model.encode(context, convert_to_tensor=True)
                similarity = util.cos_sim(query_embedding, context_embedding)[0][0].item()
                similarities.append((csv_file, similarity))

            # Selecionar o CSV com maior similaridade
            if similarities:
                best_csv, best_score = max(similarities, key=lambda x: x[1])
                logger.info(f"Arquivo selecionado: {best_csv} (Similaridade: {best_score:.2f})")
                return best_csv

            logger.warning("Nenhum arquivo CSV relevante encontrado")
            return None
        except Exception as e:
            logger.error(f"Erro na seleção de CSV: {e}")
            raise