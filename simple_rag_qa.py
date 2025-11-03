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


def main():
    """Esempio di utilizzo"""
    
    # Verifica se l'API key è configurata
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("⚠️  ATTENZIONE: API key non configurata!")
        print("Per usare questo sistema RAG, imposta la variabile d'ambiente:")
        print("export ANTHROPIC_API_KEY='la-tua-api-key'\n")
        print("Puoi ottenere una API key su: https://console.anthropic.com/\n")
        return
    
    # Crea un documento PDF di esempio se non esiste
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    
    example_pdf = "/home/claude/documento_esempio.pdf"
    
    if not os.path.exists(example_pdf):
        print("📝 Creazione documento PDF di esempio...")
        c = canvas.Canvas(example_pdf, pagesize=letter)
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
        print(f"✅ Documento creato: {example_pdf}\n")
    
    # Inizializza il RAG
    rag = SimpleRAG()
    
    # Estrai il testo dal PDF
    rag.extract_text_from_pdf(example_pdf)
    
    # Genera le coppie Q&A
    qa_pairs = rag.generate_qa_pairs(num_questions=5)
    
    # Stampa i risultati
    rag.print_qa_pairs(qa_pairs)


if __name__ == "__main__":
    main()

