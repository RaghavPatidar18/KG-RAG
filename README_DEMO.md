# TechCorp Knowledge Graph RAG Demo

This demo showcases a complete Knowledge Graph-based Retrieval-Augmented Generation (RAG) system. The system ingests documents, builds a knowledge graph, and provides intelligent question-answering capabilities.

## 🎯 Demo Overview

The demo includes:

- **Document Ingestion**: Load and process sample documents about TechCorp
- **NLP Pipeline**: Extract entities and relations using spaCy and custom patterns
- **Knowledge Graph Construction**: Build RDF knowledge graph using RDFLib
- **SPARQL Query Generation**: Convert natural language questions to SPARQL queries
- **Interactive Q&A**: Answer questions using the knowledge graph
- **RAG Pipeline**: Combine structured knowledge retrieval with response generation

## 🏗️ Architecture

```
Documents → NLP Processing → Triple Generation → Knowledge Graph → SPARQL Queries → Answers
```

### Components

1. **Text Loader** (`src/ingestion/text_loader.py`): Load documents from JSON files
2. **Custom NER** (`src/nlp_pipeline/spacy_ner.py`): Extract entities and relations
3. **Triple Generator** (`src/nlp_pipeline/triple_generator.py`): Convert NLP results to RDF triples
4. **KG Builder** (`src/kg_construction/kg_builder.py`): Build and manage the knowledge graph
5. **SPARQL Query Engine** (`src/query_engine/sparql_query.py`): Generate and execute queries
6. **RAG Pipeline** (`src/llm_interface/rag_pipeline.py`): Orchestrate the complete pipeline

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Install dependencies and setup
python setup_demo.py
```

### 2. Run the Demo

```bash
# Run interactive demo
python demo.py

# Force rebuild knowledge graph
python demo.py --rebuild

# Run sample queries only
python demo.py --sample-only
```

### 3. Manual Setup (if needed)

```bash
# Install requirements
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

## 📊 Sample Data

The demo uses custom sample data about TechCorp:

### Documents (`data/raw/sample_documents.json`)
- Company overview
- Product information (AI Platform, Cloud Services)
- Research division details
- Partnership information
- Financial performance

### Ontology (`data/ontology/techcorp_ontology.ttl`)
- Organization, Person, Product, Location classes
- Properties like foundedBy, develops, headquarteredIn
- Data properties for revenue, employee count, etc.

## 💡 Example Questions

Try asking these questions in the interactive demo:

- "Who founded TechCorp?"
- "What products does TechCorp develop?"
- "Where is TechCorp located?"
- "When was TechCorp founded?"
- "How many employees does TechCorp have?"
- "What is TechCorp's revenue?"
- "Who does TechCorp partner with?"
- "What industries does TechCorp serve?"
- "List all organizations in the knowledge graph"
- "List all products in the knowledge graph"

## 🔧 Demo Commands

In the interactive demo, you can use these commands:

- `help` - Show suggested questions
- `stats` - Display knowledge graph statistics
- `explain <question>` - Explain how the system processes a question
- `quit` - Exit the demo

## 📈 Knowledge Graph Statistics

The demo knowledge graph typically contains:

- **~100-200 triples** from document processing and hardcoded facts
- **Organizations**: TechCorp and partner companies
- **People**: Founders, executives, researchers
- **Products**: AI Platform, Cloud Services
- **Locations**: San Francisco, data center locations
- **Technologies**: AI, ML, cloud computing concepts

## 🎨 Technical Features

### NLP Processing
- **Named Entity Recognition**: Custom spaCy patterns for domain entities
- **Relation Extraction**: Pattern-based extraction of relationships
- **Entity Linking**: Map extracted entities to ontology classes

### Knowledge Graph
- **RDF Format**: Standard semantic web format using RDFLib
- **Ontology Integration**: Domain-specific ontology with classes and properties
- **SPARQL Queries**: Structured queries for precise information retrieval

### Query Processing
- **Question Classification**: Detect question types (who, what, where, when, how)
- **Entity Detection**: Identify main entities in questions
- **Query Generation**: Convert natural language to SPARQL
- **Result Formatting**: Present answers in natural language

## 🔍 Example Interaction

```
❓ Ask a question: Who founded TechCorp?

🔍 Processing: 'Who founded TechCorp?'
----------------------------------------
💡 Answer: The company was founded by Sarah Johnson and Michael Chen.

📊 Found 2 relevant data points
🔧 SPARQL Query Used:
   PREFIX : <http://example.org/techcorp#> SELECT ?founder ?founderName WHERE { ?org :hasName ?orgName...

🎯 Question Type: who_founded
🏷️  Detected Entity: TechCorp
```

## 📁 Project Structure

```
kg-rag-app/
├── demo.py                 # Main demo script
├── setup_demo.py          # Setup and installation script
├── requirements.txt       # Python dependencies
├── data/
│   ├── raw/               # Sample documents
│   ├── ontology/          # Domain ontology
│   └── rdf/               # Generated knowledge graph
└── src/
    ├── ingestion/         # Document loading
    ├── nlp_pipeline/      # NLP processing
    ├── kg_construction/   # Knowledge graph building
    ├── query_engine/      # SPARQL query processing
    ├── llm_interface/     # RAG pipeline
    └── utils/             # Configuration and utilities
```

## 🛠️ Extending the Demo

### Adding New Documents
1. Add documents to `data/raw/sample_documents.json`
2. Run `python demo.py --rebuild`

### Adding New Entity Types
1. Update the ontology in `data/ontology/techcorp_ontology.ttl`
2. Add patterns to `src/nlp_pipeline/spacy_ner.py`
3. Update query templates in `src/query_engine/sparql_query.py`

### Adding LLM Integration
1. Set up API keys in environment variables
2. Implement LLM calls in `src/llm_interface/rag_pipeline.py`
3. Enhance prompt templates for better responses

## 🐛 Troubleshooting

### Common Issues

1. **spaCy model not found**
   ```bash
   python -m spacy download en_core_web_sm
   ```

2. **Import errors**
   ```bash
   pip install -r requirements.txt
   ```

3. **No sample data**
   - Ensure `data/raw/sample_documents.json` exists
   - Run the demo from the project root directory

4. **Empty knowledge graph**
   - Check that sample documents are valid JSON
   - Run with `--rebuild` flag to force regeneration

### Debug Mode

For debugging, you can:
- Check SPARQL queries in the demo output
- Examine raw results from knowledge graph queries
- Use the `explain` command to understand question processing

## 📚 Learning Resources

This demo demonstrates concepts from:
- **Knowledge Graphs**: RDF, SPARQL, semantic web technologies
- **Information Extraction**: NER, relation extraction, entity linking
- **Retrieval-Augmented Generation**: Combining structured and unstructured data
- **Natural Language Processing**: Question understanding, answer generation

## 🤝 Contributing

To extend this demo:
1. Fork the repository
2. Add new features or improvements
3. Test with the existing demo data
4. Submit a pull request

## 📄 License

This demo is provided for educational and demonstration purposes.
