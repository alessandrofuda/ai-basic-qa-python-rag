"""
Utility functions for PDF handling and document management
"""

import os
from config import DEFAULT_PDF_PATH


def create_example_pdf(pdf_path=DEFAULT_PDF_PATH):
    """Create an example PDF document if it doesn't exist

    Args:
        pdf_path: Path where to create the PDF file
    """
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
    for line in text.split("\n"):
        c.drawString(50, y, line.strip())
        y -= 15
        if y < 50:
            c.showPage()
            y = 750

    c.save()
    print(f"✅ Documento creato: {pdf_path}\n")
