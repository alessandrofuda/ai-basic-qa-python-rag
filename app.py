"""
Main application entry point for the RAG Q&A System
"""

import os
from flask import Flask
from rag_core import SimpleRAG
from utils import create_example_pdf
from api import create_routes, set_rag_instance
from config import (
    DEFAULT_PORT,
    DEFAULT_HOST,
    REQUEST_TIMEOUT,
    DEFAULT_PDF_PATH,
)


def create_app():
    """Create and configure the Flask application

    Returns:
        Configured Flask app instance
    """
    app = Flask(__name__)

    # Configure request timeouts
    app.config["REQUEST_TIMEOUT"] = REQUEST_TIMEOUT

    # Register API routes
    create_routes(app)

    return app


def init_rag():
    """Initialize the RAG system

    Returns:
        True if initialization successful, False otherwise
    """
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("⚠️  ATTENZIONE: API key non configurata!")
        return False

    create_example_pdf(DEFAULT_PDF_PATH)
    rag = SimpleRAG()
    rag.extract_text_from_pdf(DEFAULT_PDF_PATH)
    set_rag_instance(rag)
    return True


def main():
    """Main entry point for the application"""
    print("🚀 Avvio del server RAG Q&A API...")

    if init_rag():
        print("✅ Sistema RAG inizializzato correttamente")
        print(f"📡 Server in ascolto su http://{DEFAULT_HOST}:{DEFAULT_PORT}")

        app = create_app()
        app.run(
            host=DEFAULT_HOST,
            port=DEFAULT_PORT,
            debug=False,
            threaded=True,
        )
    else:
        print("❌ Errore nell'inizializzazione del sistema RAG")
        exit(1)


if __name__ == "__main__":
    main()
