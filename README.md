# RAG Project - Legal Document Q&A System

A complete Retrieval-Augmented Generation (RAG) pipeline for answering questions about legal documents from the Court of Accounts of Minas Gerais (TCEMG).

## Table of Contents

- [Project Objective](#project-objective)
- [Project Structure and Steps](#project-structure-and-steps)
- [Tools and Techniques Utilized](#tools-and-techniques-utilized)
- [Specific Results and Outcomes](#specific-results-and-outcomes)
- [What I Have Learned from This Project](#what-i-have-learned-from-this-project)
- [How to Use This Repository](#how-to-use-this-repository)
- [Future Improvements and Enhancements](#future-improvements-and-enhancements)
- [References](#references)

---

## Project Objective

This project demonstrates how to build a production-ready Retrieval-Augmented Generation (RAG) system for legal document analysis. The primary goal is to create an interactive application that can answer questions about legal precedents (súmulas) from the Court of Accounts of Minas Gerais (TCEMG) by intelligently retrieving relevant context from PDF documents and generating accurate responses.

**Key objectives:**
- Index and semantically search legal documents stored as PDFs
- Enable natural language queries with automatic metadata filtering
- Provide a user-friendly interface for legal professionals and researchers
- Implement complete observability and traceability of each query
- Demonstrate best practices for production RAG systems

---

## Project Structure and Steps

### Repository Structure

```
rag-project/
├── app/
│   ├── graph/
│   │   ├── rag_graph.py      # Main LangGraph orchestration
│   │   └── prompt.py          # LLM prompts and templates
│   ├── ingest/
│   │   ├── embed_qdrant.py    # Embeddings and Qdrant connection
│   │   └── extract_text.py    # PDF text and metadata extraction
│   ├── retrieval/
│   │   ├── retriever.py       # SelfQueryRetriever + Qdrant
│   │   └── self_query.py      # Metadata definitions and filters
│   ├── app.py                 # Streamlit interface
│   └── settings.py            # Global application settings
├── sumulas/                   # PDF documents directory
├── requirements.txt
├── README.md
└── Dockerfile                 # (optional)
```

### Implementation Steps

1. **Document Ingestion**: Extract text and metadata from legal PDF documents using MarkItDown
2. **Vectorization**: Convert documents into embeddings and store in Qdrant vector database
3. **Retrieval Configuration**: Set up SelfQueryRetriever with metadata filtering capabilities
4. **Graph Orchestration**: Build LangGraph workflow to manage retrieve → generate flow
5. **Interface Development**: Create Streamlit UI for user interaction
6. **Observability Integration**: Implement Langfuse for complete execution tracking

---

## Tools and Techniques Utilized

### Core Technologies

- **LangChain** - Framework for LLM application development, providing integration between language models and vector databases

- **LangGraph** - State machine orchestration for controlling workflow between nodes (retrieval → generation → end)

- **Langfuse** - Observability platform for tracking spans, tokens, metrics, and complete execution traces/nodes

- **Qdrant** - Vector database for semantic and keyword search with local deployment support

- **Streamlit** - Interactive web interface framework for end-user interaction

- **OpenAI GPT** - Large language model for text generation and query understanding

- **MarkItDown (Microsoft)** - PDF text and metadata extraction tool

### Key Techniques

- **Retrieval-Augmented Generation (RAG)**: Combines semantic search with text generation, where the model retrieves real context before generating responses

- **Self-Query Retriever**: Enables the LLM to understand queries and automatically construct structured filters (e.g., filtering by `status_atual` or `data_status`)

- **Metadata Engineering**: Intelligent handling of date fields by converting string dates (DD/MM/AA) to integer years for proper numerical comparisons in Qdrant

- **State Management**: LangGraph maintains global state across nodes, ensuring proper context flow

- **Embedding-Based Search**: Semantic similarity search using vector representations of documents

---

## Specific Results and Outcomes

### Technical Achievements

**Successful Date Handling Solution**: Resolved Qdrant's limitation with string-based date comparisons by converting dates from DD/MM/AA format to integer years (e.g., "07/04/14" → 2014), enabling proper numerical filtering with operators like `<`, `>`, `<=`, `>=`

**Complete Observability Pipeline**: Every query execution is fully traced in Langfuse dashboard, including:
- Prompts and retrieved context
- Token consumption metrics
- Response latency
- Node execution chain (retrieve → generate)

**Intelligent Metadata Filtering**: The SelfQueryRetriever automatically interprets user queries and applies appropriate filters without explicit user commands

**Production-Ready Architecture**: Modular design with clear separation of concerns (ingestion, retrieval, graph orchestration, UI)

### System Capabilities

- Semantic search across legal documents with high accuracy
- Natural language query processing with automatic filter generation
- Real-time document indexing and retrieval
- Scalable vector storage with Qdrant
- Complete audit trail for compliance and debugging

---

## What I Have Learned from This Project

### Technical Insights

- **Vector Database Constraints**: Discovered that Qdrant only supports numerical comparisons on actual numeric types, not strings. String-based date formats require conversion to proper numeric or ISO 8601 formats for range queries.

- **The Importance of Metadata Design**: Proper metadata schema design is crucial for effective filtering. The data type and format of metadata fields directly impact query capabilities.

- **RAG Pipeline Complexity**: Building a production RAG system involves much more than just embeddings and retrieval - it requires careful orchestration, state management, error handling, and observability.

- **LangGraph State Management**: Understanding how to properly structure state between nodes and maintain context throughout the execution flow is essential for complex workflows.

### Best Practices

- **Observability is Non-Negotiable**: Implementing Langfuse from the start provided invaluable insights into system behavior, performance bottlenecks, and debugging capabilities.

- **Modular Architecture Pays Off**: Separating concerns into distinct modules (ingestion, retrieval, graph, UI) made the codebase maintainable and testable.

- **Test with Real Data**: Working with actual legal documents revealed edge cases that wouldn't be apparent with synthetic data, particularly around date formats and metadata extraction.

- **User Interface Matters**: Even for technical demos, a clean Streamlit interface significantly improves the ability to demonstrate and test the system effectively.

---

## How to Use This Repository

### Prerequisites

- Python 3.11+
- Docker Desktop (for Qdrant)
- API Keys:
  - OpenAI API key
  - Langfuse account (free tier available)

### Setup Instructions

#### 1. Clone the Repository

```bash
git clone https://github.com/caio-moliveira/rag-project.git
cd rag-project
```

#### 2. Start Qdrant Vector Database

```bash
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant
```

#### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxx
LANGFUSE_PUBLIC_KEY=pk-xxxxxxxxxxxxxxxxxx
LANGFUSE_SECRET_KEY=sk-xxxxxxxxxxxxxxxxxx
LANGFUSE_HOST=https://us.cloud.langfuse.com
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

#### 4. Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

#### 5. Add PDF Documents

Place your PDF files in the `sumulas/` directory. You can download official documents from:
- [TCE-MG Official Documents](https://www.tce.mg.gov.br/Noticia/Detalhe/67)

#### 6. Ingest Documents

```bash
python app/ingest/extract_text.py
```

This creates the `sumulas_jornada` collection in Qdrant, extracting text and metadata automatically.

#### 7. Launch the Application

```bash
streamlit run app/app.py
```

Open your browser at [http://localhost:8501](http://localhost:8501)

### Using the Application

1. Enter your question in natural language about the legal documents
2. The system will automatically retrieve relevant context and generate an answer
3. View execution traces in your Langfuse dashboard at [https://us.cloud.langfuse.com/](https://us.cloud.langfuse.com/)

---

## Future Improvements and Enhancements

### Short-Term Enhancements

- **Multi-Language Support**: Add support for queries in English and other languages while maintaining Portuguese document base

- **Enhanced Error Handling**: Implement more robust error handling and user feedback for edge cases

- **Query History**: Add persistent query history and bookmarking functionality

- **Export Capabilities**: Enable export of answers and sources to PDF or Word documents

### Medium-Term Features

- **Advanced Filtering UI**: Create interactive filters in the Streamlit interface for manual metadata selection

- **Document Comparison**: Add ability to compare multiple documents or precedents side-by-side

- **Citation Extraction**: Automatically extract and link citations within documents

- **Performance Optimization**: Implement caching strategies for frequently asked questions

### Long-Term Vision

- **Multi-Modal RAG**: Extend to handle tables, charts, and images within PDF documents

- **Fine-Tuned Models**: Train domain-specific embedding models for improved legal document understanding

- **Federated Search**: Enable search across multiple legal document repositories

- **Collaborative Features**: Add annotation, commenting, and sharing capabilities for teams

- **API Development**: Build REST API for integration with other legal research tools

**Real-Time Updates**: Implement automatic document monitoring and re-indexing for new publications

**Advanced Analytics**: Provide insights on most queried topics, document usage statistics, and knowledge gaps

---

## References

- [MarkItDown (Microsoft)](https://github.com/microsoft/markitdown) - Text and metadata extraction from PDFs
- [Qdrant LangChain API](https://python.lang
