"""
Configuration and constants for the RAG Q&A system
"""

# API Configuration
DEFAULT_PORT = 5000
DEFAULT_HOST = '0.0.0.0'
REQUEST_TIMEOUT = 300  # 5 minutes

# RAG Configuration
DEFAULT_PDF_PATH = "./documento_esempio.pdf"
DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-4-20250514"
DEFAULT_MAX_TOKENS = 2000

# Client Configuration
DEFAULT_API_TIMEOUT = 60  # seconds
DEFAULT_MAX_RETRIES = 3
DEFAULT_API_CALL_DELAY = 0.5  # seconds between API calls

# Chunking Configuration
DEFAULT_CHUNK_SIZE = 8000  # characters
DEFAULT_OVERLAP = 200  # characters
DEFAULT_MAX_CHUNKS = 100
MIN_CHUNK_SIZE = 1000
MAX_CHUNK_SIZE = 16000

# Q&A Generation
DEFAULT_QUESTIONS_PER_CHUNK = 3
MIN_QUESTIONS = 1
MAX_QUESTIONS = 20

# Error Handling
DEFAULT_CHUNK_RETRIES = 2
MAX_RETRY_WAIT = 10  # seconds
