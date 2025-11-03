"""
Flask API routes for the RAG Q&A system
"""

from flask import jsonify, request
from config import (
    DEFAULT_QUESTIONS_PER_CHUNK,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_OVERLAP,
    MIN_QUESTIONS,
    MAX_QUESTIONS,
    MIN_CHUNK_SIZE,
    MAX_CHUNK_SIZE,
    DEFAULT_PDF_PATH,
)


# Global RAG instance (set by app.py during initialization)
rag_instance = None


def set_rag_instance(instance):
    """Set the global RAG instance

    Args:
        instance: SimpleRAG instance
    """
    global rag_instance
    rag_instance = instance


def create_routes(app):
    """Create and register API routes on the Flask app

    Args:
        app: Flask application instance
    """

    @app.route("/health", methods=["GET"])
    def health():
        """Health check endpoint

        Returns:
            JSON response with service status
        """
        return jsonify({"status": "ok", "service": "RAG Q&A API"}), 200

    @app.route("/api/generate-qa", methods=["POST"])
    def generate_qa():
        """Generate Q&A pairs from the loaded document

        Query Parameters:
            questions (int): Number of Q&A pairs (1-20, default: 5)

        Returns:
            JSON response with generated Q&A pairs or error
        """
        try:
            if rag_instance is None:
                return jsonify({"error": "RAG system not initialized"}), 500

            num_questions = request.args.get("questions", 5, type=int)

            if num_questions < MIN_QUESTIONS or num_questions > MAX_QUESTIONS:
                return (
                    jsonify(
                        {
                            "error": f"questions parameter must be between {MIN_QUESTIONS} and {MAX_QUESTIONS}"
                        }
                    ),
                    400,
                )

            qa_pairs = rag_instance.generate_qa_pairs(num_questions=num_questions)

            return (
                jsonify({"success": True, "count": len(qa_pairs), "qa_pairs": qa_pairs}),
                200,
            )

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/generate-qa-chunked", methods=["POST"])
    def generate_qa_chunked():
        """Generate Q&A pairs for long documents by processing in chunks

        Query Parameters:
            questions_per_chunk (int): Q&A pairs per chunk (1-20, default: 3)
            chunk_size (int): Characters per chunk (1000-16000, default: 8000)
            overlap (int): Overlap between chunks (default: 200)

        Returns:
            JSON response with generated Q&A pairs or error
        """
        try:
            if rag_instance is None:
                return jsonify({"error": "RAG system not initialized"}), 500

            num_questions = request.args.get("questions_per_chunk", DEFAULT_QUESTIONS_PER_CHUNK, type=int)
            chunk_size = request.args.get("chunk_size", DEFAULT_CHUNK_SIZE, type=int)
            overlap = request.args.get("overlap", DEFAULT_OVERLAP, type=int)

            # Validate parameters
            if num_questions < MIN_QUESTIONS or num_questions > MAX_QUESTIONS:
                return (
                    jsonify(
                        {
                            "error": f"questions_per_chunk must be between {MIN_QUESTIONS} and {MAX_QUESTIONS}"
                        }
                    ),
                    400,
                )

            if chunk_size < MIN_CHUNK_SIZE or chunk_size > MAX_CHUNK_SIZE:
                return (
                    jsonify(
                        {
                            "error": f"chunk_size must be between {MIN_CHUNK_SIZE} and {MAX_CHUNK_SIZE}"
                        }
                    ),
                    400,
                )

            if overlap < 0 or overlap >= chunk_size:
                return (
                    jsonify({"error": "overlap must be between 0 and chunk_size-1"}),
                    400,
                )

            print(
                f"\n📊 Inizio elaborazione chunked: "
                f"questions={num_questions}, chunk_size={chunk_size}, overlap={overlap}"
            )

            qa_pairs = rag_instance.generate_qa_pairs_chunked(
                num_questions=num_questions, chunk_size=chunk_size, overlap=overlap
            )

            print(f"✅ Elaborazione completata: {len(qa_pairs)} Q&A generate")

            return (
                jsonify({"success": True, "count": len(qa_pairs), "qa_pairs": qa_pairs}),
                200,
            )

        except TimeoutError as e:
            print(f"⏱️  TimeoutError: {str(e)}")
            return jsonify({"error": f"Request timeout: {str(e)}"}), 504
        except Exception as e:
            print(f"❌ Exception in generate_qa_chunked: {type(e).__name__}: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/document-info", methods=["GET"])
    def document_info():
        """Get information about the loaded document

        Returns:
            JSON response with document metadata
        """
        if rag_instance is None:
            return jsonify({"error": "RAG system not initialized"}), 500

        return (
            jsonify(
                {
                    "document_loaded": bool(rag_instance.document_text),
                    "document_length": len(rag_instance.document_text),
                    "document_path": DEFAULT_PDF_PATH,
                }
            ),
            200,
        )
