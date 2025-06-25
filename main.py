from crewai import Agent, Task, Crew, Process
from agents import (
    ExtractionAgent, SelectionAgent,
    ProcessingAgent, AnalysisAgent, ResponseAgent
)
from utils.logging_utils import setup_logging
from config.llm_config import get_groq_llm
import streamlit as st
import os
import logging
from typing import Dict, List
import time

# Configura logging
setup_logging()
logger = logging.getLogger(__name__)


def setup_agents() -> Dict[str, Agent]:
    """Configura e retorna todos os agentes."""
    llm = get_groq_llm()

    agents = {
        'extraction': Agent(
            role='Especialista em Extração',
            goal='Extrair arquivos de documentos ZIP',
            backstory="""Você é um especialista em extração de arquivos com anos de experiência 
            em lidar com formatos compactados.""",
            tools=[ExtractionAgent().extract_zip_files],
            verbose=True,
            llm=llm,
            allow_delegation=False
        ),
        'selection': Agent(
            role='Especialista em Seleção',
            goal='Identificar o arquivo CSV mais relevante',
            backstory="""Você tem uma habilidade única para encontrar o arquivo certo baseado
            no contexto da pergunta e metadados dos arquivos.""",
            tools=[SelectionAgent().select_relevant_csv],
            verbose=True,
            llm=llm,
            allow_delegation=False
        ),
        'processing': Agent(
            role='Engenheiro de Dados',
            goal='Processar e limpar dados CSV',
            backstory="""Você transforma dados brutos em informações analisáveis, lidando com
            problemas de formatação e qualidade.""",
            tools=[ProcessingAgent().process_csv_data],
            verbose=True,
            llm=llm,
            allow_delegation=False
        ),
        'analysis': Agent(
            role='Analista de Dados',
            goal='Extrair insights dos dados processados',
            backstory="""Você encontra padrões e insights em conjuntos de dados complexos
            de notas fiscais.""",
            tools=[AnalysisAgent().analyze_and_answer],
            verbose=True,
            llm=llm,
            allow_delegation=False
        ),
        'response': Agent(
            role='Especialista em Comunicação',
            goal='Formatar respostas para o usuário',
            backstory="""Você traduz análises técnicas em respostas claras e acessíveis.""",
            tools=[ResponseAgent().format_response],
            verbose=True,
            llm=llm,
            allow_delegation=False
        )
    }
    return agents


def create_tasks(agents: Dict[str, Agent], zip_path: str, user_query: str) -> List[Task]:
    """Cria o fluxo de tarefas."""
    return [
        Task(
            description=f"Extrair arquivos de {zip_path}",
            agent=agents['extraction'],
            expected_output="Lista de caminhos dos arquivos extraídos",
            async_execution=False
        ),
        Task(
            description=f"Selecionar arquivo CSV relevante para: '{user_query}'",
            agent=agents['selection'],
            expected_output="Caminho para o arquivo CSV mais relevante",
            context=[],
            async_execution=False
        ),
        Task(
            description="Processar o arquivo CSV selecionado",
            agent=agents['processing'],
            expected_output="Dados processados em formato serializável",
            context=[],
            async_execution=False
        ),
        Task(
            description=f"Analisar dados para responder: '{user_query}'",
            agent=agents['analysis'],
            expected_output="Resposta detalhada com análise",
            context=[],
            async_execution=False
        ),
        Task(
            description="Formatar a resposta final",
            agent=agents['response'],
            expected_output="Resposta clara e formatada para o usuário",
            context=[],
            async_execution=False
        )
    ]


def update_progress(task_name: str, message: str, duration: float = None, progress_container=None):
    """Atualiza o progresso na interface do Streamlit."""
    log_message = f"[{task_name}] {message}"
    if duration is not None:
        log_message += f" (Tempo gasto: {duration:.2f} segundos)"
    st.session_state.task_logs.append(log_message)
    if progress_container:
        with progress_container:
            st.markdown("\n".join(st.session_state.task_logs))


def execute_task(task: Task, previous_result=None, progress_container=None):
    """Executa uma tarefa com monitoramento de progresso e tempo."""
    task_name = task.description.split()[0]
    start_time = time.time()

    update_progress(task_name, "Iniciado", progress_container=progress_container)

    try:
        # Tentar executar a tarefa
        result = task.execute(context=previous_result)
        end_time = time.time()
        duration = end_time - start_time

        update_progress(task_name, f"Concluído: {result}", duration, progress_container)
        return result
    except AttributeError:
        # Fallback para agent.run se execute falhar
        logger.warning(f"Método execute falhou para {task_name}. Usando agent.run.")
        result = task.agent.run(task.description, context=previous_result)
        end_time = time.time()
        duration = end_time - start_time

        update_progress(task_name, f"Concluído (via agent.run): {result}", duration, progress_container)
        return result
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        update_progress(task_name, f"Erro: {str(e)}", duration, progress_container)
        raise


def main():
    st.set_page_config(page_title="Sistema de Consulta NF-e", layout="wide")
    st.title("📄 Consulta de Notas Fiscais Eletrônicas")

    with st.sidebar:
        st.header("Configuração")
        zip_file = st.file_uploader("Carregue arquivo ZIP com CSVs", type=['zip'])
        user_query = st.text_area("Digite sua pergunta sobre os dados")
        submitted = st.button("Enviar Consulta")

    # Inicializar session_state
    if 'task_logs' not in st.session_state:
        st.session_state.task_logs = []

    progress_container = st.empty()

    if submitted and zip_file and user_query:
        with st.spinner("Processando sua solicitação..."):
            try:
                # Limpar logs anteriores
                st.session_state.task_logs = []

                # Salvar arquivo temporário
                os.makedirs('data', exist_ok=True)
                zip_path = os.path.join('data', 'temp_upload.zip')
                with open(zip_path, 'wb') as f:
                    f.write(zip_file.getvalue())

                # Configurar agentes e tarefas
                agents = setup_agents()
                tasks = create_tasks(agents, zip_path, user_query)

                # Executar tarefas sequencialmente
                previous_result = None
                for task in tasks:
                    previous_result = execute_task(task, previous_result, progress_container)
                    # Forçar re-renderização do Streamlit
                    st.write("")  # Hack para garantir atualização

                # Exibir resultados
                st.success("✅ Análise concluída!")
                st.subheader("Resposta:")
                st.markdown(previous_result)

            except Exception as e:
                st.error(f"❌ Erro durante o processamento")
                st.error(f"Detalhes: {str(e)}")
                logger.exception("Erro na execução:")


if __name__ == "__main__":
    main()