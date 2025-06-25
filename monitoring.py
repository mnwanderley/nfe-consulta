import streamlit as st
import pandas as pd
import time
from datetime import datetime


class AgentMonitor:
    def __init__(self):
        if 'agent_logs' not in st.session_state:
            st.session_state.agent_logs = []

        self.placeholder = st.empty()

    def update(self, agent_name, task_description, status, execution_time=None):
        now = datetime.now().strftime("%H:%M:%S")
        log_entry = {
            'timestamp': now,
            'agent': agent_name,
            'task': task_description,
            'status': status,
            'time': execution_time or 'Em andamento'
        }
        st.session_state.agent_logs.append(log_entry)

        with self.placeholder.container():
            st.subheader("Monitoramento dos Agentes")
            logs_df = pd.DataFrame(st.session_state.agent_logs)
            st.dataframe(
                logs_df,
                column_config={
                    "timestamp": "Horário",
                    "agent": "Agente",
                    "task": "Tarefa",
                    "status": "Status",
                    "time": "Tempo"
                },
                use_container_width=True,
                hide_index=True
            )