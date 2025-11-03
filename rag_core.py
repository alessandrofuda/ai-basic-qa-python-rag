"""
Core RAG (Retrieval-Augmented Generation) system for Q&A pair generation
"""

import os
import time
import PyPDF2
from anthropic import Anthropic
from config import (
    DEFAULT_ANTHROPIC_MODEL,
    DEFAULT_MAX_TOKENS,
    DEFAULT_API_TIMEOUT,
    DEFAULT_MAX_RETRIES,
    DEFAULT_API_CALL_DELAY,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_OVERLAP,
    DEFAULT_MAX_CHUNKS,
    DEFAULT_CHUNK_RETRIES,
    MAX_RETRY_WAIT,
)


class SimpleRAG:
    """Simple Retrieval-Augmented Generation system for PDF Q&A generation"""

    def __init__(self, api_key=None, timeout=DEFAULT_API_TIMEOUT, max_retries=DEFAULT_MAX_RETRIES):
        """Initialize RAG system with Anthropic API credentials

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            timeout: API request timeout in seconds
            max_retries: Number of retries for API calls
        """
        self.client = Anthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"),
            timeout=timeout,
            max_retries=max_retries,
        )
        self.document_text = ""
        self.api_call_delay = DEFAULT_API_CALL_DELAY

    def extract_text_from_pdf(self, pdf_path):
        """Extract text from a PDF file

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Extracted text from all pages
        """
        print(f"📄 Estrazione testo da {pdf_path}...")

        with open(pdf_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""

            for page_num, page in enumerate(pdf_reader.pages):
                text += f"\n--- Pagina {page_num + 1} ---\n"
                text += page.extract_text()

        self.document_text = text
        print(f"✅ Estratto {len(text)} caratteri da {len(pdf_reader.pages)} pagine")
        return text

    def generate_qa_pairs(self, num_questions=5):
        """Generate Q&A pairs from the loaded document

        Args:
            num_questions: Number of Q&A pairs to generate

        Returns:
            List of dictionaries with 'question' and 'answer' keys

        Raises:
            ValueError: If no document is loaded
        """
        if not self.document_text:
            raise ValueError("Nessun documento caricato. Usa extract_text_from_pdf() prima.")

        print(f"\n🤖 Generazione di {num_questions} coppie Q&A...")

        prompt = f"""Analizza il seguente documento e genera {num_questions} coppie di domande e risposte.

            Le domande devono essere pertinenti e coprire i concetti chiave del documento.
            Le risposte devono essere accurate e basate esclusivamente sul contenuto del documento.

            Formatta l'output come:

            Q1: [domanda]
            A1: [risposta]

            Q2: [domanda]
            A2: [risposta]

            Documento:
            {self.document_text[:8000]}
        """

        try:
            message = self.client.messages.create(
                model=DEFAULT_ANTHROPIC_MODEL,
                max_tokens=DEFAULT_MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}],
            )

            qa_text = message.content[0].text
            print("✅ Q&A generate con successo!\n")

            return self._parse_qa_pairs(qa_text)
        finally:
            # Add delay between API calls to prevent rate limiting
            time.sleep(self.api_call_delay)

    def _parse_qa_pairs(self, qa_text):
        """Parse Q&A pairs from generated text

        Args:
            qa_text: Raw text containing Q&A pairs in Q:..., A:... format

        Returns:
            List of dictionaries with 'question' and 'answer' keys
        """
        qa_pairs = []
        lines = qa_text.strip().split("\n")

        current_q = None
        current_a = None

        for line in lines:
            line = line.strip()
            if line.startswith("Q") and ":" in line:
                if current_q and current_a:
                    qa_pairs.append({"question": current_q, "answer": current_a})
                current_q = line.split(":", 1)[1].strip()
                current_a = None
            elif line.startswith("A") and ":" in line:
                current_a = line.split(":", 1)[1].strip()

        if current_q and current_a:
            qa_pairs.append({"question": current_q, "answer": current_a})

        return qa_pairs

    def chunk_text(self, text, max_chars=DEFAULT_CHUNK_SIZE, overlap=DEFAULT_OVERLAP, max_chunks=DEFAULT_MAX_CHUNKS):
        """Split text into intelligent chunks respecting sentence boundaries

        Args:
            text: Text to chunk
            max_chars: Maximum characters per chunk
            overlap: Overlap characters between chunks
            max_chunks: Maximum number of chunks (prevents runaway processing)

        Returns:
            List of text chunks
        """
        chunks = []
        start = 0

        while start < len(text) and len(chunks) < max_chunks:
            # Calculate chunk end
            end = min(start + max_chars, len(text))

            # If not at document end, find last period for natural break
            if end < len(text):
                last_period = text.rfind(".", start, end)
                if last_period > start:
                    end = last_period + 1

            # Extract and add chunk
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # Exit if we've reached the end
            if end >= len(text):
                break

            # Move to next chunk with overlap
            # Ensure we always advance (at least 1 character)
            start = max(end - overlap, start + 1)

        if len(chunks) >= max_chunks:
            print(f"⚠️  Raggiunto il limite massimo di {max_chunks} chunk")

        return chunks

    def generate_qa_pairs_chunked(self, num_questions=3, chunk_size=DEFAULT_CHUNK_SIZE, overlap=DEFAULT_OVERLAP):
        """Generate Q&A pairs for long documents by processing in chunks

        Args:
            num_questions: Number of Q&A pairs per chunk
            chunk_size: Characters per chunk
            overlap: Overlap between chunks

        Returns:
            List of Q&A pairs from all chunks
        """
        if not self.document_text:
            raise ValueError("Nessun documento caricato. Usa extract_text_from_pdf() prima.")

        # Split document into chunks
        chunks = self.chunk_text(self.document_text, max_chars=chunk_size, overlap=overlap)
        print(
            f"\n📚 Documento diviso in {len(chunks)} chunk "
            f"(dimensione chunk: {chunk_size} caratteri, overlap: {overlap})"
        )

        all_qa = []
        errors = []

        # Process each chunk
        for i, chunk in enumerate(chunks):
            print(f"\n🔄 Processamento chunk {i+1}/{len(chunks)}... ({len(chunk)} caratteri)")

            # Save original text and replace with current chunk
            original_text = self.document_text
            self.document_text = chunk

            max_retries = DEFAULT_CHUNK_RETRIES
            retry_count = 0

            while retry_count <= max_retries:
                try:
                    qa = self.generate_qa_pairs(num_questions=num_questions)
                    all_qa.extend(qa)
                    print(f"   ✓ Generati {len(qa)} Q&A dal chunk {i+1}")
                    break  # Success, exit retry loop

                except Exception as e:
                    retry_count += 1
                    error_msg = f"Errore nel chunk {i+1} (tentativo {retry_count}/{max_retries + 1}): {str(e)}"
                    print(f"⚠️  {error_msg}")

                    if retry_count > max_retries:
                        errors.append(error_msg)
                    else:
                        # Wait before retrying with exponential backoff
                        wait_time = min(2**retry_count, MAX_RETRY_WAIT)
                        print(f"   ⏳ Attesa {wait_time}s prima di ritentare...")
                        time.sleep(wait_time)
                finally:
                    # Restore original text
                    self.document_text = original_text

        if errors:
            print(f"\n⚠️  Alcuni chunk hanno prodotto errori ({len(errors)}/{len(chunks)})")

        print(f"\n✅ Generato un totale di {len(all_qa)} coppie Q&A da {len(chunks)} chunk")
        return all_qa

    def print_qa_pairs(self, qa_pairs):
        """Print Q&A pairs in readable format

        Args:
            qa_pairs: List of Q&A pair dictionaries
        """
        print("=" * 80)
        print("DOMANDE E RISPOSTE GENERATE")
        print("=" * 80)

        for i, qa in enumerate(qa_pairs, 1):
            print(f"\n{'='*80}")
            print(f"Q{i}: {qa['question']}")
            print(f"\nA{i}: {qa['answer']}")

        print(f"\n{'='*80}")
