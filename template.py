import os

# Define base project structure
structure = {
    "kg-rag-app": {
        "data": {
            "raw": {},
            "processed": {},
            "rdf": {},
            "ontology": {},
            "graphdb": {}
        },
        "src": {
            "ingestion": {
                "__init__.py": "",
                "text_loader.py": "# Load documents, webpages, and PDFs\n",
                "clean_data.py": "# Cleaning and normalization\n",
                "rdf_converter.py": "# Convert text → RDF triples\n"
            },
            "nlp_pipeline": {
                "__init__.py": "",
                "spacy_ner.py": "# Named Entity Recognition (custom)\n",
                "relation_extractor.py": "# Extract relations guided by ontology\n",
                "ontology_mapper.py": "# Map extracted entities to OWL classes\n",
                "triple_generator.py": "# Build RDF triples (subject, predicate, object)\n"
            },
            "kg_construction": {
                "__init__.py": "",
                "rdf_serializer.py": "# Serialize RDF data\n",
                "kg_builder.py": "# Build KG in rdflib or GraphDB\n",
                "ontology_loader.py": "# Load ontology (OWL)\n",
                "reasoning_engine.py": "# Apply OWL reasoning/inference\n"
            },
            "query_engine": {
                "__init__.py": "",
                "sparql_query.py": "# SPARQL query generator\n",
                "vector_retriever.py": "# Hybrid retriever (FAISS/AstraDB)\n",
                "schema_aligner.py": "# Align user query to ontology schema\n",
                "retriever.py": "# Combine KG + semantic retrieval\n"
            },
            "llm_interface": {
                "__init__.py": "",
                "prompt_template.py": "# Dynamic prompt construction\n",
                "groq_client.py": "# Call Groq/OpenAI API\n",
                "rag_pipeline.py": "# Full KG-RAG chain\n"
            },
            "api": {
                "__init__.py": "",
                "main.py": "# FastAPI app entry point\n",
                "routes": {
                    "__init__.py": "",
                    "query_routes.py": "# Endpoint for user queries\n",
                    "kg_routes.py": "# Endpoint for KG inspection/debug\n"
                },
                "utils.py": "# Helper functions for API\n"
            },
            "frontend": {
                "app.py": "# Streamlit-based UI\n",
                "components": {}
            },
            "utils": {
                "config.py": "# Environment variables loader\n",
                "logger.py": "# Custom logger setup\n",
                "helpers.py": "# Common helper functions\n"
            },
            "pipelines": {
                "build_kg_pipeline.py": "# Ingest → Extract → Build KG\n",
                "rag_pipeline.py": "# Retrieval + LLM reasoning\n",
                "eval_pipeline.py": "# Evaluate KG-RAG performance\n"
            }
        },
        "tests": {
            "test_kg_build.py": "",
            "test_rdf_serialization.py": "",
            "test_retrieval.py": "",
            "test_rag_pipeline.py": ""
        },
        "notebooks": {
            "01_data_exploration.ipynb": "",
            "02_entity_relation_extraction.ipynb": "",
            "03_kg_visualization.ipynb": "",
            "04_rag_demo.ipynb": ""
        },
        "README.md": "# Knowledge Graph-based RAG Application\n",
        "requirements.txt": "",
        ".env": "",
        "setup.py": "# Setup configuration for KG-RAG application\n"
    }
}


def create_structure(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)

        # If the content is a dictionary, it's a folder
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            # Create a file with optional initial content
            with open(path, "w") as f:
                f.write(content)


if __name__ == "__main__":
    base_dir = os.getcwd()  # Current directory
    create_structure(base_dir, structure)
    print("✅ Knowledge Graph-based RAG project structure created successfully!")
