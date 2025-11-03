"""
Simple RAG System - PDF to Q&A Generator
Estrae testo da un PDF e genera domande e risposte utilizzando un LLM
"""

import os
from pathlib import Path
import PyPDF2
from anthropic import Anthropic

class SimpleRAG:
    def __init__(self, api_key=None):
        """Inizializza il sistema RAG con l'API key di Anthropic"""
        self.client = Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
        self.document_text = ""
    
    def extract_text_from_pdf(self, pdf_path):
        """Estrae il testo da un file PDF"""
        print(f"📄 Estrazione testo da {pdf_path}...")
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            
            for page_num, page in enumerate(pdf_reader.pages):
                text += f"\n--- Pagina {page_num + 1} ---\n"
                text += page.extract_text()
        
        self.document_text = text
        print(f"✅ Estratto {len(text)} caratteri da {len(pdf_reader.pages)} pagine")
        return text
    
    def generate_qa_pairs(self, num_questions=5):
        """Genera coppie domanda-risposta dal documento"""
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
        
        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        qa_text = message.content[0].text
        print("✅ Q&A generate con successo!\n")
        
        return self._parse_qa_pairs(qa_text)
    
    def _parse_qa_pairs(self, qa_text):
        """Parsing delle coppie Q&A dal testo generato"""
        qa_pairs = []
        lines = qa_text.strip().split('\n')
        
        current_q = None
        current_a = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('Q') and ':' in line:
                if current_q and current_a:
                    qa_pairs.append({"question": current_q, "answer": current_a})
                current_q = line.split(':', 1)[1].strip()
                current_a = None
            elif line.startswith('A') and ':' in line:
                current_a = line.split(':', 1)[1].strip()
        
        if current_q and current_a:
            qa_pairs.append({"question": current_q, "answer": current_a})
        
        return qa_pairs
    
    def print_qa_pairs(self, qa_pairs):
        """Stampa le coppie Q&A in formato leggibile"""
        print("=" * 80)
        print("DOMANDE E RISPOSTE GENERATE")
        print("=" * 80)
        
        for i, qa in enumerate(qa_pairs, 1):
            print(f"\n{'='*80}")
            print(f"Q{i}: {qa['question']}")
            print(f"\nA{i}: {qa['answer']}")
        
        print(f"\n{'='*80}")


def create_example_pdf(pdf_path):
    """Crea un documento PDF di esempio"""
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    if os.path.exists(pdf_path):
        return

    print("📝 Creazione documento PDF di esempio...")
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.setFont("Helvetica", 12)

    text = """
    L'Intelligenza Artificiale: Una Panoramica

    L'intelligenza artificiale (IA) è un campo dell'informatica che si concentra
    sulla creazione di sistemi capaci di eseguire compiti che normalmente richiedono
    l'intelligenza umana.

    Storia dell'IA
    Il termine "intelligenza artificiale" è stato coniato nel 1956 durante la
    conferenza di Dartmouth. Da allora, il campo ha attraversato diversi periodi
    di entusiasmo e di "inverni dell'IA".

    Applicazioni Moderne
    Oggi l'IA viene utilizzata in molti settori:
    - Assistenti vocali come Siri e Alexa
    - Sistemi di raccomandazione su Netflix e Amazon
    - Veicoli autonomi
    - Diagnosi medica assistita
    - Traduzione automatica

    Machine Learning
    Il machine learning è un sottocampo dell'IA che permette ai computer di
    apprendere dai dati senza essere esplicitamente programmati. Include tecniche
    come le reti neurali e il deep learning.

    Sfide Etiche
    L'IA solleva importanti questioni etiche riguardo la privacy, i bias algoritmici
    e l'impatto sul mercato del lavoro.
    """

    y = 750
    for line in text.split('\n'):
        c.drawString(50, y, line.strip())
        y -= 15
        if y < 50:
            c.showPage()
            y = 750

    c.save()
    print(f"✅ Documento creato: {pdf_path}\n")


# Flask App Setup
from flask import Flask, jsonify, request

app = Flask(__name__)

# Global RAG instance
rag_instance = None
example_pdf = "./documento_esempio.pdf"


def init_rag():
    """Inizializza il sistema RAG"""
    global rag_instance

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("⚠️  ATTENZIONE: API key non configurata!")
        return False

    create_example_pdf(example_pdf)
    rag_instance = SimpleRAG()
    rag_instance.extract_text_from_pdf(example_pdf)
    return True


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "service": "RAG Q&A API"}), 200


@app.route('/api/generate-qa', methods=['POST'])
def generate_qa():
    """Genera coppie Q&A dal documento caricato"""
    try:
        if rag_instance is None:
            return jsonify({"error": "RAG system not initialized"}), 500

        num_questions = request.args.get('questions', 5, type=int)

        if num_questions < 1 or num_questions > 20:
            return jsonify({"error": "questions parameter must be between 1 and 20"}), 400

        qa_pairs = rag_instance.generate_qa_pairs(num_questions=num_questions)

        return jsonify({
            "success": True,
            "count": len(qa_pairs),
            "qa_pairs": qa_pairs
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/document-info', methods=['GET'])
def document_info():
    """Ritorna info sul documento caricato"""
    if rag_instance is None:
        return jsonify({"error": "RAG system not initialized"}), 500

    return jsonify({
        "document_loaded": bool(rag_instance.document_text),
        "document_length": len(rag_instance.document_text),
        "document_path": example_pdf
    }), 200


if __name__ == "__main__":
    print("🚀 Avvio del server RAG Q&A API...")
    if init_rag():
        print("✅ Sistema RAG inizializzato correttamente")
        print("📡 Server in ascolto su http://0.0.0.0:5000")
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        print("❌ Errore nell'inizializzazione del sistema RAG")
        exit(1)

