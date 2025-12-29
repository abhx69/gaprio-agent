# Gaprio Agent

## Setup Instructions

1. Copy `.env.example` to `.env` and fill in your values
2. Install dependencies: `pip install -r requirements.txt`
3. Setup database: `python setup_database.py`
4. Run server: `python main.py`

graph TB
    A[User Interface] --> B[FastAPI Server]
    B --> C[Agent Brain]
    C --> D{Ollama LLM}
    C --> E[Database]
    C --> F[Asana API]
    C --> G[Gmail API]
    
    E --> H[MySQL Database]
    D --> I[Local LLM]
    
    style A fill:#4CAF50
    style C fill:#2196F3
    style H fill:#FF9800