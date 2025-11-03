# Immagine base Python
FROM python:3.9

# Imposta la directory di lavoro
WORKDIR /app

# Copia il file delle dipendenze e installale
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice dell'applicazione nella directory di lavoro
COPY . .

# Comando per eseguire l'applicazione (es. avviare un'app Flask)
# CMD ["python", "app.py"]
CMD ["python", "simple_rag_qa.py"]
