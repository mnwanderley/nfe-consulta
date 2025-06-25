from langchain.tools import tool
import pandas as pd
import logging
from typing import Dict
from sentence_transformers import SentenceTransformer, util
import numpy as np

logger = logging.getLogger(__name__)


class AnalysisAgent:
    def __init__(self):
        """Inicializa o modelo de embeddings."""
        try:
            self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        except Exception as e:
            logger.error(f"Erro ao carregar o modelo de embeddings: {e}")
            raise

    @tool("Analyze data and answer query")
    def analyze_and_answer(self, processed_data: Dict, query: str) -> Dict:
        """
        Analisa os dados e responde à pergunta do usuário usando embeddings para queries complexas.

        Args:
            processed_data: Dados processados no formato serializável
            query: Pergunta do usuário

        Returns:
            Dicionário com a resposta e metadados
        """
        try:
            logger.info(f"Analisando dados para a query: {query}")

            # Converte de volta para DataFrame
            df = pd.DataFrame(processed_data['data'])
            df.columns = df.columns.str.lower()

            # Gerar embedding da query
            query_embedding = self.model.encode(query.lower(), convert_to_tensor=True)

            # Extrair contexto das colunas e amostra de dados
            contexts = []
            for col in df.columns:
                # Usar nome da coluna e uma amostra de valores únicos
                sample_values = df[col].astype(str).unique()[:5]  # Até 5 valores únicos
                context = f"Coluna: {col}. Valores: {', '.join(sample_values)}"
                contexts.append(context)

            # Gerar embeddings dos contextos
            context_embeddings = self.model.encode(contexts, convert_to_tensor=True)

            # Calcular similaridade de cosseno
            similarities = util.cos_sim(query_embedding, context_embeddings)[0]
            most_relevant_idx = np.argmax(similarities)
            most_relevant_col = df.columns[most_relevant_idx]

            # Análises básicas com base na coluna mais relevante
            result = {
                'query': query,
                'answer': None,
                'analysis': None,
                'data_sample': processed_data['metadata']['sample']
            }

            # Lógica de análise aprimorada
            if 'total' in query.lower() and most_relevant_col in df.columns:
                if df[most_relevant_col].dtype in ['float64', 'int64']:
                    total = df[most_relevant_col].sum()
                    result['answer'] = f"O total de {most_relevant_col} é {total:,.2f}"
                    result['analysis'] = {f'total_{most_relevant_col}': total}
                else:
                    result['answer'] = f"A coluna {most_relevant_col} não é numérica."

            elif 'quantidade' in query.lower() and most_relevant_col in df.columns:
                if df[most_relevant_col].dtype in ['float64', 'int64']:
                    count = df[most_relevant_col].sum()
                    result['answer'] = f"A quantidade total de {most_relevant_col} é {count:,.0f}"
                    result['analysis'] = {f'total_{most_relevant_col}': count}
                else:
                    result['answer'] = f"A coluna {most_relevant_col} não é numérica."

            else:
                # Resposta genérica baseada na coluna mais relevante
                sample = df[most_relevant_col].head(5).to_list()
                result['answer'] = f"Dados relevantes em '{most_relevant_col}': {', '.join(map(str, sample))}"
                result['analysis'] = {f'sample_{most_relevant_col}': sample}

            logger.info(f"Análise concluída. Resposta: {result['answer']}")
            return result
        except Exception as e:
            logger.error(f"Erro na análise: {e}")
            return {'error': str(e)}