from langchain.tools import tool
from utils.logging_utils import log_agent
import zipfile
import os

class ExtractionAgent:
    def __init__(self, monitor=None):
        self.monitor = monitor  # Recebe o monitor

    @tool
    @log_agent("Extração de ZIP")
    def extract_zip_files(self, zip_path: str):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            files = zip_ref.namelist()
            zip_ref.extractall('data/temp')
            return {
                'success': True,
                'files': files,
                'extracted_to': 'data/temp'
            }