from langchain.tools import tool
import logging

logger = logging.getLogger(__name__)


class ResponseAgent:
    @tool("Format response to user")
    def format_response(analysis_result: dict) -> str:
        """
        Formata a resposta para o usuário de forma amigável.

        Args:
            analysis_result: Resultado da análise

        Returns:
            Resposta formatada para o usuário
        """
        try:
            logger.info("Formatando resposta para o usuário")

            if 'error' in analysis_result:
                return f"Erro: {analysis_result['error']}"

            answer = analysis_result.get('answer', 'Não foi possível gerar uma resposta.')

            if 'analysis' in analysis_result and analysis_result['analysis']:
                analysis = "\n".join([f"- {k}: {v}" for k, v in analysis_result['analysis'].items()])
                answer += f"\n\nDetalhes:\n{analysis}"

            return answer
        except Exception as e:
            logger.error(f"Erro na formatação da resposta: {e}")
            return f"Erro ao formatar resposta: {str(e)}"