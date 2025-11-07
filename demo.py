#!/usr/bin/env python3
"""
TechCorp Knowledge Graph RAG Demo

This script demonstrates a complete Knowledge Graph-based RAG system.
It builds a knowledge graph from sample documents and provides an interactive
query interface.

Usage:
    python demo.py [--rebuild] [--interactive]
    
Options:
    --rebuild: Force rebuild of the knowledge graph
    --interactive: Run interactive demo (default)
"""

import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.utils.config import Config
from src.kg_construction.kg_builder import KnowledgeGraphBuilder
from src.llm_interface.rag_pipeline import SimpleRAGPipeline, InteractiveDemo

def setup_demo():
    """Set up the demo environment."""
    print("🔧 Setting up TechCorp KG-RAG Demo...")
    
    # Ensure directories exist
    Config.ensure_directories()
    
    # Initialize knowledge graph builder
    kg_builder = KnowledgeGraphBuilder()
    
    return kg_builder

def build_knowledge_graph(kg_builder: KnowledgeGraphBuilder, force_rebuild: bool = False):
    """Build the knowledge graph from sample data."""
    
    kg_file = Config.RDF_DATA_DIR / "techcorp_kg.ttl"
    
    # Check if KG already exists and we don't want to rebuild
    if kg_file.exists() and not force_rebuild:
        print(f"📚 Loading existing knowledge graph from {kg_file}")
        kg_builder.load_graph(kg_file)
        return kg_builder.get_statistics()
    
    print("🏗️  Building knowledge graph from sample documents...")
    
    # Load sample documents
    sample_docs_file = Config.RAW_DATA_DIR / "sample_documents.json"
    
    if not sample_docs_file.exists():
        print(f"❌ Sample documents not found at {sample_docs_file}")
        print("Please ensure the sample data files are in place.")
        return None
    
    # Build KG from documents
    stats = kg_builder.build_from_json(sample_docs_file)
    
    # Save the built knowledge graph
    kg_builder.save_graph(kg_file)
    
    print("✅ Knowledge graph built successfully!")
    print(f"   📊 Statistics: {stats}")
    
    return stats

def run_sample_queries(rag_pipeline: SimpleRAGPipeline):
    """Run some sample queries to demonstrate the system."""
    print("\n🎯 Running Sample Queries:")
    print("=" * 50)
    
    sample_questions = [
        "Who founded TechCorp?",
        "What products does TechCorp develop?",
        "Where is TechCorp located?",
        "How many employees does TechCorp have?",
        "What is TechCorp's revenue?"
    ]
    
    for i, question in enumerate(sample_questions, 1):
        print(f"\n{i}. Question: {question}")
        print("-" * 30)
        
        response = rag_pipeline.answer_question(question)
        print(f"   Answer: {response['answer']}")
        
        # Show some technical details
        sources = response.get('sources', {})
        print(f"   Type: {sources.get('question_type', 'unknown')}")
        print(f"   Results: {len(sources.get('raw_results', []))} data points")

def show_graph_info(kg_builder: KnowledgeGraphBuilder):
    """Display information about the knowledge graph."""
    print("\n📊 Knowledge Graph Information:")
    print("=" * 40)
    
    stats = kg_builder.get_statistics()
    print(f"Total Triples: {stats.get('total_triples', 0)}")
    print(f"Total Entities: {stats.get('total_entities', 0)}")
    
    entities_by_type = stats.get('entities_by_type', {})
    if entities_by_type:
        print("\nEntities by Type:")
        for entity_type, count in entities_by_type.items():
            print(f"  - {entity_type}: {count}")
    
    # Show some sample entities
    print("\n🔍 Sample Entity Information:")
    entity_info = kg_builder.get_entity_info("TechCorp")
    if entity_info:
        for entity_uri, info in list(entity_info.items())[:1]:  # Show first entity
            print(f"\nEntity: {entity_uri}")
            for prop in info.get('properties', [])[:5]:  # Show first 5 properties
                prop_name = prop['property'].split('#')[-1] if '#' in prop['property'] else prop['property']
                print(f"  - {prop_name}: {prop['value']}")

def main():
    """Main demo function."""
    parser = argparse.ArgumentParser(description="TechCorp Knowledge Graph RAG Demo")
    parser.add_argument("--rebuild", action="store_true", 
                       help="Force rebuild of the knowledge graph")
    parser.add_argument("--no-interactive", action="store_true",
                       help="Skip interactive demo")
    parser.add_argument("--sample-only", action="store_true",
                       help="Run sample queries only")
    
    args = parser.parse_args()
    
    print("🚀 TechCorp Knowledge Graph RAG Demo")
    print("=" * 60)
    print("This demo showcases a complete KG-RAG pipeline including:")
    print("  • Document ingestion and NLP processing")
    print("  • Knowledge graph construction with RDF")
    print("  • SPARQL query generation from natural language")
    print("  • Interactive question-answering interface")
    print("=" * 60)
    
    try:
        # Setup
        kg_builder = setup_demo()
        
        # Build knowledge graph
        stats = build_knowledge_graph(kg_builder, args.rebuild)
        if stats is None:
            return 1
        
        # Show graph information
        show_graph_info(kg_builder)
        
        # Initialize RAG pipeline
        rag_pipeline = SimpleRAGPipeline(kg_builder)
        
        # Run sample queries
        if not args.no_interactive or args.sample_only:
            run_sample_queries(rag_pipeline)
        
        # Interactive demo
        if not args.no_interactive and not args.sample_only:
            print("\n" + "=" * 60)
            demo = InteractiveDemo(rag_pipeline)
            demo.run_demo()
        
        print("\n✅ Demo completed successfully!")
        return 0
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user.")
        return 0
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
