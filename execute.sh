echo -e "Running Web Scraper..."
python3 -m src.tools.web_crawler
echo -e "Web Scraper Completed.\n"

echo -e "Running Pdf Scraper..."
python3 -m src.tools.pdf_scraper
echo -e "Pdf Scraper Completed.\n"

echo -e "Initializing ChromaDB..."
python3 -m src.config
python3 -m src.utils
python3 -m src.chroma_service
echo -e "ChromaDB Initialization Completed.\n"

echo -e "Initializing Groq LLM..."
python3 -m src.groq_llm
echo -e "Groq LLM Initialization Completed.\n"

echo -e "Running Embedding Store Creation..."
python3 -m src.embed_store
echo -e "Embedding Store Creation Completed.\n"

echo -e "Running RAG Pipeline..."
python3 -m src.rag_pipeline
