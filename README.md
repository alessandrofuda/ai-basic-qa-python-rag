# Simple RAG: PDF to Q&A Generator

Un semplice esempio di sistema RAG (Retrieval-Augmented Generation) che:
1. Riceve in input un file PDF
2. Estrae il testo dal documento
3. Genera automaticamente una lista di domande e risposte

## Installazione

```bash
pip install -r requirements.txt
```

## Configurazione

Imposta la tua API key di Anthropic:

```bash
export ANTHROPIC_API_KEY="la-tua-api-key"
```

Con **docker compose**: passa la variabile d'ambiente nel container via `env_file`

## Utilizzo

### 1. Come Web API (Consigliato per Docker)

Avvia il servizio con Docker Compose:

```bash
docker compose up
```

L'API sarà disponibile su `http://localhost:5000`

#### Endpoint Disponibili

**Health Check**
```bash
curl http://localhost:5000/health
```
Risposta:
```json
{"status":"ok","service":"RAG Q&A API"}
```

**Informazioni Documento**
```bash
curl http://localhost:5000/api/document-info
```
Risposta:
```json
{
  "document_loaded": true,
  "document_length": 1007,
  "document_path": "./documento_esempio.pdf"
}
```

**Generare Coppie Q&A**
```bash
curl -X POST "http://localhost:5000/api/generate-qa?questions=5"
```

Parametri:
- `questions`: Numero di coppie Q&A da generare (1-20, default: 5)

Risposta:
```json
{
  "success": true,
  "count": 2,
  "qa_pairs": [
    {
      "question": "Quando è stato coniato il termine \"intelligenza artificiale\"?",
      "answer": "Il termine è stato coniato nel 1956 durante la conferenza di Dartmouth..."
    },
    {
      "question": "Che cos'è il machine learning?",
      "answer": "Il machine learning è un sottocampo dell'IA che permette ai computer di apprendere..."
    }
  ]
}
```

### 2. Utilizzo da Linea di Comando

```bash
python simple_rag_qa.py
```

Questo comando:
- Crea un PDF di esempio sull'Intelligenza Artificiale
- Estrae il testo dal PDF
- Genera 5 coppie di domande e risposte

### 3. Utilizzo Personalizzato (Programmazione)

```python
from simple_rag_qa import SimpleRAG

# Inizializza il RAG
rag = SimpleRAG(api_key="la-tua-api-key")

# Carica il tuo PDF
rag.extract_text_from_pdf("percorso/al/tuo/documento.pdf")

# Genera Q&A (puoi specificare il numero di domande)
qa_pairs = rag.generate_qa_pairs(num_questions=10)

# Stampa i risultati
rag.print_qa_pairs(qa_pairs)
```

## Struttura del Codice

- **`SimpleRAG`**: Classe principale che gestisce il sistema RAG
  - `extract_text_from_pdf()`: Estrae testo da un PDF usando PyPDF2
  - `generate_qa_pairs()`: Usa Claude per generare domande e risposte
  - `print_qa_pairs()`: Formatta e stampa i risultati

## Output

Il sistema genera coppie Q&A in questo formato:

```
Q1: Cos'è l'intelligenza artificiale?
A1: L'intelligenza artificiale è un campo dell'informatica che si concentra 
sulla creazione di sistemi capaci di eseguire compiti che normalmente 
richiedono l'intelligenza umana.

Q2: Quando è stato coniato il termine "intelligenza artificiale"?
A2: Il termine è stato coniato nel 1956 durante la conferenza di Dartmouth.
```

## Docker

### Avviare il Servizio

**Modo interattivo** (vedi i log):
```bash
docker compose up
```

**Modo detached** (esegui in background):
```bash
docker compose up -d
```

### Visualizzare i Log

```bash
docker compose logs -f
```

### Fermare il Servizio

```bash
docker compose down
```

## Note

- Il sistema utilizza Claude Sonnet 4 per la generazione di Q&A
- Il testo estratto viene limitato a ~8000 caratteri per rispettare i limiti del contesto
- Per PDF più lunghi, considera di implementare la chunking del testo
- La Web API rimane in ascolto e pronta a servire richieste indefinitamente

