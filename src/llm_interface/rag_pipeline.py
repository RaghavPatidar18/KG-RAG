"""RAG pipeline combining Knowledge Graph with LLM reasoning."""

from typing import List, Dict, Any, Optional
import json
from src.query_engine.sparql_query import SPARQLQueryEngine
from src.utils.config import Config

class SimpleRAGPipeline:
    """Simple RAG pipeline that uses KG for retrieval and provides structured responses."""
    
    def __init__(self, kg_builder, use_llm: bool = False):
        self.kg_builder = kg_builder
        self.query_engine = SPARQLQueryEngine(kg_builder)
        self.use_llm = use_llm
        
        # Simple prompt template for LLM enhancement (if available)
        self.prompt_template = """
Based on the following information from a knowledge graph, provide a comprehensive and natural answer to the user's question.

Question: {question}

Knowledge Graph Information:
{kg_info}

Raw Data:
{raw_data}

Please provide a clear, informative answer that synthesizes this information. If the information is incomplete, acknowledge what's missing.

Answer:"""
    
    def retrieve_knowledge(self, question: str) -> Dict[str, Any]:
        """Retrieve relevant knowledge from the knowledge graph.
        
        Args:
            question: User's natural language question
            
        Returns:
            Dictionary containing retrieved knowledge
        """
        # Use SPARQL query engine to get structured answer
        kg_response = self.query_engine.answer_question(question)
        
        # Get additional context by searching for related entities
        entity = kg_response.get('entity', '')
        if entity:
            entity_info = self.kg_builder.get_entity_info(entity)
            kg_response['entity_details'] = entity_info
        
        # Get graph statistics for context
        stats = self.kg_builder.get_statistics()
        kg_response['graph_stats'] = stats
        
        return kg_response
    
    def enhance_with_llm(self, question: str, kg_info: Dict[str, Any]) -> str:
        """Enhance the KG response with LLM reasoning (placeholder for now).
        
        Args:
            question: Original question
            kg_info: Information retrieved from knowledge graph
            
        Returns:
            Enhanced response string
        """
        # For now, just return the structured KG answer
        # In a full implementation, this would call an LLM API
        
        answer = kg_info.get('answer', 'No information found.')
        raw_results = kg_info.get('raw_results', [])
        
        # Add some context if we have raw results
        if raw_results and len(raw_results) > 1:
            answer += f" (Based on {len(raw_results)} data points from the knowledge graph.)"
        
        return answer
    
    def answer_question(self, question: str) -> Dict[str, Any]:
        """Answer a question using the RAG pipeline.
        
        Args:
            question: User's natural language question
            
        Returns:
            Comprehensive response dictionary
        """
        # Step 1: Retrieve knowledge from KG
        kg_info = self.retrieve_knowledge(question)
        
        # Step 2: Enhance with LLM if available
        if self.use_llm:
            enhanced_answer = self.enhance_with_llm(question, kg_info)
        else:
            enhanced_answer = kg_info.get('answer', 'No information found.')
        
        # Step 3: Prepare comprehensive response
        response = {
            'question': question,
            'answer': enhanced_answer,
            'sources': {
                'sparql_query': kg_info.get('sparql_query', ''),
                'raw_results': kg_info.get('raw_results', []),
                'entity_details': kg_info.get('entity_details', {}),
                'question_type': kg_info.get('question_type', ''),
                'detected_entity': kg_info.get('entity', '')
            },
            'metadata': {
                'retrieval_method': 'knowledge_graph',
                'llm_enhanced': self.use_llm,
                'graph_stats': kg_info.get('graph_stats', {})
            }
        }
        
        return response
    
    def get_suggested_questions(self) -> List[str]:
        """Get a list of suggested questions based on the knowledge graph content.
        
        Returns:
            List of suggested question strings
        """
        suggestions = [
            "Who founded TechCorp?",
            "What products does TechCorp develop?",
            "Where is TechCorp located?",
            "When was TechCorp founded?",
            "How many employees does TechCorp have?",
            "What is TechCorp's revenue?",
            "Who does TechCorp partner with?",
            "What industries does TechCorp serve?",
            "List all organizations in the knowledge graph",
            "List all products in the knowledge graph",
            "List all people in the knowledge graph"
        ]
        
        return suggestions
    
    def explain_reasoning(self, question: str) -> Dict[str, Any]:
        """Explain how the system would approach answering a question.
        
        Args:
            question: User's question
            
        Returns:
            Dictionary explaining the reasoning process
        """
        from src.query_engine.sparql_query import SPARQLQueryGenerator
        
        generator = SPARQLQueryGenerator()
        question_type, entity = generator.detect_question_type(question)
        query = generator.generate_query(question)
        
        explanation = {
            'question': question,
            'reasoning_steps': [
                f"1. Detected question type: '{question_type}'",
                f"2. Identified main entity: '{entity}'",
                f"3. Generated SPARQL query to search knowledge graph",
                f"4. Would execute query and format results"
            ],
            'sparql_query': query,
            'question_type': question_type,
            'detected_entity': entity
        }
        
        return explanation

class InteractiveDemo:
    """Interactive demo interface for the RAG pipeline."""
    
    def __init__(self, rag_pipeline: SimpleRAGPipeline):
        self.rag_pipeline = rag_pipeline
    
    def run_demo(self):
        """Run an interactive demo session."""
        print("🚀 Welcome to the TechCorp Knowledge Graph RAG Demo!")
        print("=" * 60)
        print("\nThis demo showcases a Knowledge Graph-based RAG system.")
        print("The system can answer questions about TechCorp using structured knowledge.")
        print("\nType 'help' for suggested questions, 'stats' for graph statistics, or 'quit' to exit.")
        print("-" * 60)
        
        while True:
            try:
                question = input("\n❓ Ask a question: ").strip()
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Thanks for trying the demo!")
                    break
                
                elif question.lower() == 'help':
                    self._show_help()
                
                elif question.lower() == 'stats':
                    self._show_stats()
                
                elif question.lower() == 'explain':
                    explain_q = input("Enter a question to explain the reasoning: ").strip()
                    self._explain_reasoning(explain_q)
                
                elif question:
                    self._answer_question(question)
                
                else:
                    print("Please enter a question or type 'help' for suggestions.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Demo interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
    def _answer_question(self, question: str):
        """Answer a user question and display results."""
        print(f"\n🔍 Processing: '{question}'")
        print("-" * 40)
        
        response = self.rag_pipeline.answer_question(question)
        
        print(f"💡 Answer: {response['answer']}")
        
        # Show additional details
        sources = response.get('sources', {})
        if sources.get('raw_results'):
            print(f"\n📊 Found {len(sources['raw_results'])} relevant data points")
        
        if sources.get('sparql_query'):
            print(f"\n🔧 SPARQL Query Used:")
            print(f"   {sources['sparql_query'][:100]}...")
        
        print(f"\n🎯 Question Type: {sources.get('question_type', 'unknown')}")
        print(f"🏷️  Detected Entity: {sources.get('detected_entity', 'unknown')}")
    
    def _show_help(self):
        """Show suggested questions."""
        print("\n💡 Suggested Questions:")
        print("-" * 25)
        suggestions = self.rag_pipeline.get_suggested_questions()
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i:2d}. {suggestion}")
        
        print("\n🔧 Special Commands:")
        print("   - 'stats': Show knowledge graph statistics")
        print("   - 'explain': Explain reasoning for a question")
        print("   - 'help': Show this help message")
        print("   - 'quit': Exit the demo")
    
    def _show_stats(self):
        """Show knowledge graph statistics."""
        print("\n📈 Knowledge Graph Statistics:")
        print("-" * 35)
        stats = self.rag_pipeline.kg_builder.get_statistics()
        
        print(f"Total Triples: {stats.get('total_triples', 0)}")
        print(f"Total Entities: {stats.get('total_entities', 0)}")
        
        entities_by_type = stats.get('entities_by_type', {})
        if entities_by_type:
            print("\nEntities by Type:")
            for entity_type, count in entities_by_type.items():
                print(f"  - {entity_type}: {count}")
    
    def _explain_reasoning(self, question: str):
        """Explain the reasoning process for a question."""
        print(f"\n🧠 Reasoning for: '{question}'")
        print("-" * 40)
        
        explanation = self.rag_pipeline.explain_reasoning(question)
        
        for step in explanation['reasoning_steps']:
            print(f"   {step}")
        
        print(f"\n📝 Generated SPARQL Query:")
        print(f"   {explanation['sparql_query']}")