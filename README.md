# Agentic Personal RAG

Sistema RAG (Retrieval-Augmented Generation) con agenti LangGraph, **Regolo AI** e Qdrant.

Carica i tuoi documenti e chiedi informazioni in totale privacy. L'agente decide autonomamente quando cercare nei documenti.

## 🔒 Privacy e Sicurezza Dati - Powered by Regolo AI

Questo sistema è costruito sulla piattaforma **Regolo AI** di Seeweb, garantendo la massima protezione dei tuoi dati personali:

- **Zero Data Retention**: Regolo non salva i tuoi dati. I tuoi documenti e le tue conversazioni non vengono mai trattenuti o usati per il training dei modelli
- **GDPR Compliance**: Infrastruttura 100% europea con server in Italia, conforme al Regolamento Generale sulla Protezione dei Dati
- **Data Sovereignty**: I tuoi dati non lasciano mai l'Unione Europea
- **Green AI**: Regolo utilizza energia 100% rinnovabile per le operazioni di inferenza, riducendo l'impatto ambientale
- **OpenAI Compatible**: API compatibile OpenAI, facile integrazione senza lock-in

### Perché Regolo AI?

Regolo AI è la piattaforma AI di Seeweb, provider cloud italiano leader. Scopri di più:
- 🌐 [Regolo AI - Sito Ufficiale](https://regolo.ai)
- 📚 [Documentazione e Guide](https://regolo.ai/labs/)
- 🚀 [Guida: Regolo + LangGraph per Agentic RAG](https://regolo.ai/chat-with-all-your-documents-with-regolo-elysia/)
- 🔐 [Green AI & Privacy](https://regolo.ai/what-is-cloud-llm-hosting-a-european-take-on-scalable-private-and-green-ai-infrastructure/)

## Caratteristiche

- **Agente RAG**: Agente LangGraph che decide autonomamente quando cercare nei documenti
- **Powered by Regolo AI**: LLM e embeddings 100% open-source su infrastruttura europea
- **Privacy Assoluta**: Zero retention dei dati, nessun training su documenti personali
- **Supporto Documenti**: Upload PDF, DOCX, TXT
- **Vector Database**: Qdrant per ricerca semantica (opzionale self-hosted)
- **Frontend Semplice**: Single-page HTML con Tailwind CSS
- **GDPR Ready**: Infrastruttura italiana, conforme alle normative europee sulla privacy
- **Green AI**: Funzionamento su energia 100% rinnovabile
- **Codebase Semplice**: Facile da personalizzare ed estendere

## Stack Tecnologico

- **AI Engine**: **Regolo AI** (Seeweb) - LLM e Embeddings open-source su infrastruttura europea
  - gpt-oss-120b per il reasoning
  - Qwen3-Embedding-8B per la ricerca semantica
- **AI Agent**: LangGraph + LangChain
- **Backend**: FastAPI, Python 3.12+
- **Vector DB**: Qdrant (Docker)
- **Frontend**: HTML + Tailwind CSS
- **Document Processing**: PyPDF, python-docx, pdfplumber

## Quick Start

### Prerequisiti

- Python 3.12+
- Docker e Docker Compose
- **Regolo AI Account**: Registrati su [regolo.ai](https://regolo.ai) (gratuito, senza carta di credito per sandbox) per ottenere la tua API key dalla dashboard

### 1. Clone e Setup

```bash
cd "Agentic personal RAG"
```

### 2. Configura Environment

```bash
cd backend
cp .env.example .env
```

Modifica `.env`:
```bash
REGOLO_API_KEY=your_actual_api_key_here
```

### 3. Avvia Qdrant

```bash
cd ../docker/qdrant
docker-compose up -d
```

**Nota**: Se hai già un container Qdrant, modifica `docker-compose.yml`:
```yaml
ports:
  - "7333:6333"
  - "7334:6334"
```

### 4. Installa Dipendenze

```bash
cd ../backend
pip install -r requirements.txt
```

### 5. Avvia Backend

```bash
python -m app.main
# o
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 6. Apri Frontend

Visita : http://localhost:8000/static/index.html

## Come Funziona

### L'Agente RAG

Il sistema usa un agente LangGraph con tre nodi:

1. **Agent**: Il LLM decide se chiamare il tool `search_documents` o rispondere direttamente
2. **Tool**: Esegue la ricerca nei documenti caricati
3. **Response**: Formatta la risposta con i risultati

L'agente opera in un ciclo:
- Input utente → Agent → (se necessario) Tool → Agent → Output

### Upload Documenti

1. Clicca tab "Upload"
2. Drag & drop PDF, DOCX, TXT
3. Automaticamente processati e embedded

### Chat con Documenti

1. Clicca tab "Chat"
2. Fai domande sui tuoi documenti
3. L'agente cerca informazioni se necessario e risponde con fonti

### Gestione Documenti

1. Clicca tab "Documents"
2. Vedi tutti i documenti caricati
3. Cancella singoli o tutti

## 🔐 Privacy & Security

Questo sistema è progettato per garantire la massima privacy dei tuoi dati:

### Flusso Dati

1. **Upload Documenti**: I tuoi file vengono processati localmente e convertiti in embeddings
2. **Archiviazione**: Gli embeddings sono salvati nel tuo database Qdrant (può essere self-hosted)
3. **Inference**: Solo i chunks rilevanti vengono inviati a Regolo AI per generare risposte
4. **Zero Retention**: Regolo non salva i tuoi dati. Niente training sui tuoi documenti.

### Regolo AI: European Privacy First

- **Data Residency**: Tutta l'inferenza avviene in Italia (EU)
- **Zero Retention Policy**: I dati non vengono trattenuti, né usati per migliorare i modelli
- **GDPR Compliant**: Conforme alle normative europee sulla protezione dei dati
- **Transparent Pricing**: Paghi solo per i token consumati, nessun costo nascosto
- **OpenAI Compatible**: API drop-in, facile integrazione e nessun vendor lock-in

### Perché la Privacy è Importante

Con i provider AI statunitensi, i tuoi dati potrebbero:
- Essere conservati indefinitamente
- Essere usati per il training dei modelli
- Essere soggetti a leggi non europee (es. CLOUD Act)
- Essere processati fuori dall'UE

Con **Regolo AI** sei protetto dalla normativa europea e hai il controllo completo dei tuoi dati.

## API Documentation

Una volta avviato il backend, visita:
- **Interactive docs**: http://localhost:8000/docs
- **API Spec**: http://localhost:8000/openapi.json

### Endpoint principali

```
POST   /api/documents/upload      # Carica documento
GET    /api/documents             # Lista documenti
DELETE /api/documents/{id}        # Cancella documento
POST   /api/rag/chat              # Chat con documenti
GET    /api/health                 # Health check
```

## Struttura Progetto

```
Agentic personal RAG/
├── backend/
│   ├── app/
│   │   ├── agents/              # Agente LangGraph
│   │   │   └── __init__.py      # Implementazione agente RAG
│   │   ├── api/routes/          # API endpoints
│   │   ├── core/               # Config e servizi base
│   │   ├── models/             # Pydantic schemas
│   │   ├── services/           # Business logic
│   │   │   ├── rag_service.py  # Facade per agente
│   │   │   ├── embedding_service.py
│   │   │   └── document_processor.py
│   │   └── main.py             # FastAPI app
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── index.html
│   ├── css/custom.css
│   └── js/                     # Frontend logic
├── docker/
│   └── qdrant/
│       └── docker-compose.yml
└── README.md
```

## Configurazione

### Backend (.env)

```bash
# Regolo AI (Seeweb)
REGOLO_API_KEY=your_key
REGOLO_BASE_URL=https://api.regolo.ai/v1
REGOLO_MODEL=gpt-oss-120b                    # Modello reasoning 120B parametri
REGOLO_EMBEDDING_MODEL=qwen3-embedding-8b     # Embedding multilingua 8B

# Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_NAME=documents

# RAG
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=5
```

### Modelli Regolo AI Disponibili

Vedi tutti i modelli su [regolo.ai/models](https://regolo.ai/models):

- **gpt-oss-120b**: Modello reasoning con 120B parametri, ideale per complessi ragionamenti
- **llama-3.3**: Modello Meta Llama 3.3, bilanciato tra velocità e qualità
- **qwen3-embedding-8b**: Embeddings multilingua ottimizzati per RAG
- **Qwen3-Reranker-4B**: Reranker per migliorare la precisione del retrieval (opzionale)

### Frontend (js/api.js)

```javascript
const API_BASE_URL = 'http://localhost:8000';
```

## Personalizzazione

### Aggiungere Tools all'Agente

Modifica `backend/app/agents/__init__.py`:

```python
@tool
def your_custom_tool(param: str) -> str:
    """Your tool description."""
    # Your logic
    return "result"

# Aggiungi alla lista tools
tools = [search_documents, your_custom_tool]
```

### Modificare System Prompt

Cambia la variabile `system_prompt` in `backend/app/agents/__init__.py`.

### Aggiungere Tipi di Documenti

Modifica `backend/app/services/document_processor.py`.

## Troubleshooting

### Qdrant Connection Fails

```bash
# Verifica che Qdrant sia in esecuzione
docker ps | grep qdrant

# Vedi i log
docker logs agentic-rag-qdrant
```

### Regolo API Errors

- Verifica API key in `.env`
- Controlla quota su dashboard Regolo

### Frontend Can't Connect

- Assicurati che il backend sia su porta 8000
- Controlla CORS in `backend/app/core/config.py`

## Performance

- **Upload**: ~1-2 MB/s (dipende da API Regolo)
- **Query**: ~500ms - 2s (dipende da numero documenti)
- **Memory**: ~2GB per 100 documenti

## License

MIT License - sentiti libero di usare e modificare.

## Contributing

Contributi benvenuti! Apri una issue o pull request.

## 🌍 Made with Regolo AI

Questo sistema è powered by **Regolo AI** di Seeweb, la piattaforma AI italiana che combina:

- 🇪🇺 **Sovranità Digitale**: Infrastruttura europea con data center in Italia
- 🔒 **Privacy by Design**: Zero retention, conformità GDPR nativa
- 🌱 **Green AI**: 100% energia rinnovabile, metriche Token/Watt disponibili
- 🚀 **Open First**: Modelli open-source (Llama, Qwen, Mistral) senza lock-in
- ⚡ **Performance**: Scalabilità serverless, API OpenAI-compatible

Scopri di più su [regolo.ai](https://regolo.ai)

## Support & Risorse

### Regolo AI (Seeweb)
- 🌐 **Sito Ufficiale**: [regolo.ai](https://regolo.ai)
- 📚 **Documentazione & Guide**: [Regolo Labs](https://regolo.ai/labs/)
- 🤖 **Agentic RAG con Regolo**: [Guida Completa](https://regolo.ai/chat-with-all-your-documents-with-regolo-elysia/)
- 🔒 **Privacy & Green AI**: [Sicurezza e Sostenibilità](https://regolo.ai/what-is-cloud-llm-hosting-a-european-take-on-scalable-private-and-green-ai-infrastructure/)
- ⚡ **RAG con Qwen3**: [Quickstart Guide](https://regolo.ai/supercharging-retrieval-with-qwen-and-llamaindex-a-hands-on-guide/)

### Altri Tools
- **Qdrant Docs**: https://qdrant.tech/documentation/
- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/

### Hai bisogno di aiuto?
- Apri una issue su GitHub
- Contatta il supporto Regolo AI dalla dashboard
- Leggi le guide su [Regolo Labs](https://regolo.ai/labs/)
