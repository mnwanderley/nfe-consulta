import logging
import time
from datetime import datetime
from functools import wraps


class AgentMonitor:
    def __init__(self):
        self.history = []
        self.current_agent = None
        self.start_time = None

    def start_process(self):
        self.start_time = time.time()
        self.history = []
        logging.info("Processo iniciado")

    def log_agent_start(self, agent_name):
        self.current_agent = agent_name
        entry = {
            'agent': agent_name,
            'status': 'executando',
            'start': datetime.now().strftime("%H:%M:%S"),
            'duration': None
        }
        self.history.append(entry)

    def log_agent_end(self):
        if self.current_agent:
            duration = time.time() - self.start_time
            for entry in reversed(self.history):
                if entry['agent'] == self.current_agent:
                    entry['status'] = 'concluído'
                    entry['duration'] = f"{duration:.2f}s"
                    break


def log_agent(agent_name):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if hasattr(self, 'monitor'):
                self.monitor.log_agent_start(agent_name)

            start_time = time.time()
            try:
                result = func(self, *args, **kwargs)
                duration = time.time() - start_time

                if hasattr(self, 'monitor'):
                    self.monitor.log_agent_end()

                logging.info(f"{agent_name} concluído em {duration:.2f}s")
                return result
            except Exception as e:
                logging.error(f"Erro em {agent_name}: {str(e)}")
                raise

        return wrapper

    return decorator


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )