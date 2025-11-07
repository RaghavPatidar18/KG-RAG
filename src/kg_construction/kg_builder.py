"""Knowledge Graph builder using RDFLib."""

import rdflib
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD
from typing import List, Tuple, Dict, Any
from pathlib import Path
import json

from src.utils.config import Config
from src.ingestion.text_loader import TextLoader, Document
from src.nlp_pipeline.spacy_ner import CustomNER
from src.nlp_pipeline.triple_generator import TripleGenerator

class KnowledgeGraphBuilder:
    """Build and manage a knowledge graph using RDFLib."""
    
    def __init__(self, namespace: str = None):
        self.namespace_str = namespace or Config.KG_NAMESPACE
        self.namespace = Namespace(self.namespace_str)
        
        # Initialize RDF graph
        self.graph = Graph()
        self.graph.bind("", self.namespace)
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("owl", OWL)
        self.graph.bind("xsd", XSD)
        
        # Initialize components
        self.text_loader = TextLoader()
        self.ner = CustomNER()
        self.triple_generator = TripleGenerator(self.namespace_str)
        
        # Load ontology if available
        self._load_ontology()
    
    def _load_ontology(self):
        """Load the domain ontology into the graph."""
        ontology_path = Config.ONTOLOGY_FILE
        if ontology_path.exists():
            try:
                self.graph.parse(ontology_path, format="turtle")
                print(f"✅ Loaded ontology from {ontology_path}")
            except Exception as e:
                print(f"⚠️ Failed to load ontology: {e}")
        else:
            print(f"⚠️ Ontology file not found: {ontology_path}")
    
    def _parse_triple(self, triple_tuple: Tuple[str, str, str]) -> Tuple[URIRef, URIRef, Any]:
        """Parse a string triple into RDFLib objects.
        
        Args:
            triple_tuple: (subject, predicate, object) as strings
            
        Returns:
            Tuple of RDFLib objects
        """
        subject_str, predicate_str, object_str = triple_tuple
        
        # Parse subject (always a URI)
        if subject_str.startswith('http'):
            subject = URIRef(subject_str)
        else:
            subject = URIRef(self.namespace_str + subject_str)
        
        # Parse predicate
        if predicate_str.startswith('http'):
            predicate = URIRef(predicate_str)
        elif predicate_str.startswith('rdf:'):
            predicate = RDF[predicate_str[4:]]
        elif predicate_str.startswith('rdfs:'):
            predicate = RDFS[predicate_str[5:]]
        elif predicate_str.startswith('owl:'):
            predicate = OWL[predicate_str[4:]]
        else:
            predicate = URIRef(self.namespace_str + predicate_str)
        
        # Parse object (can be URI or literal)
        if object_str.startswith('"') and object_str.endswith('"'):
            # It's a literal
            literal_value = object_str[1:-1]  # Remove quotes
            
            # Check for datatype
            if '^^' in object_str:
                value_part, datatype_part = object_str.rsplit('^^', 1)
                literal_value = value_part[1:-1]  # Remove quotes
                
                if datatype_part.startswith('xsd:'):
                    datatype = XSD[datatype_part[4:]]
                else:
                    datatype = URIRef(datatype_part)
                
                obj = Literal(literal_value, datatype=datatype)
            else:
                obj = Literal(literal_value)
        elif object_str.startswith('http'):
            obj = URIRef(object_str)
        else:
            obj = URIRef(self.namespace_str + object_str)
        
        return subject, predicate, obj
    
    def add_triples(self, triples: List[Tuple[str, str, str]]):
        """Add triples to the knowledge graph.
        
        Args:
            triples: List of (subject, predicate, object) string tuples
        """
        for triple in triples:
            try:
                s, p, o = self._parse_triple(triple)
                self.graph.add((s, p, o))
            except Exception as e:
                print(f"⚠️ Failed to add triple {triple}: {e}")
    
    def process_documents(self, documents: List[Document]) -> Dict[str, Any]:
        """Process documents and add extracted knowledge to the graph.
        
        Args:
            documents: List of documents to process
            
        Returns:
            Processing statistics
        """
        stats = {
            'documents_processed': 0,
            'entities_extracted': 0,
            'relations_extracted': 0,
            'triples_added': 0
        }
        
        all_triples = []
        
        for doc in documents:
            print(f"Processing document: {doc.id}")
            
            # Extract entities and relations
            nlp_results = self.ner.process_document(doc.content)
            
            # Generate triples
            doc_triples = self.triple_generator.generate_document_triples(doc.id, nlp_results)
            all_triples.extend(doc_triples)
            
            # Update stats
            stats['documents_processed'] += 1
            stats['entities_extracted'] += len(nlp_results['entities'])
            stats['relations_extracted'] += len(nlp_results['relations'])
        
        # Add hardcoded facts
        hardcoded_triples = self.triple_generator.add_hardcoded_facts()
        all_triples.extend(hardcoded_triples)
        
        # Add all triples to graph
        self.add_triples(all_triples)
        stats['triples_added'] = len(all_triples)
        
        return stats
    
    def build_from_json(self, json_file_path: Path) -> Dict[str, Any]:
        """Build knowledge graph from a JSON file of documents.
        
        Args:
            json_file_path: Path to JSON file containing documents
            
        Returns:
            Processing statistics
        """
        print(f"Loading documents from {json_file_path}")
        documents = self.text_loader.load_json_documents(json_file_path)
        
        print(f"Loaded {len(documents)} documents")
        return self.process_documents(documents)
    
    def query_sparql(self, query: str) -> List[Dict[str, Any]]:
        """Execute a SPARQL query on the knowledge graph.
        
        Args:
            query: SPARQL query string
            
        Returns:
            Query results as list of dictionaries
        """
        try:
            results = self.graph.query(query)
            
            # Convert results to list of dictionaries
            result_list = []
            for row in results:
                row_dict = {}
                for i, var in enumerate(results.vars):
                    value = row[i]
                    if isinstance(value, URIRef):
                        row_dict[str(var)] = str(value)
                    elif isinstance(value, Literal):
                        row_dict[str(var)] = str(value)
                    else:
                        row_dict[str(var)] = str(value) if value else None
                result_list.append(row_dict)
            
            return result_list
        except Exception as e:
            print(f"Query error: {e}")
            return []
    
    def get_entity_info(self, entity_name: str) -> Dict[str, Any]:
        """Get information about a specific entity.
        
        Args:
            entity_name: Name of the entity to look up
            
        Returns:
            Dictionary containing entity information
        """
        query = f"""
        PREFIX : <{self.namespace_str}>
        SELECT ?entity ?property ?value WHERE {{
            ?entity :hasName ?name .
            FILTER(CONTAINS(LCASE(?name), LCASE("{entity_name}")))
            ?entity ?property ?value .
        }}
        """
        
        results = self.query_sparql(query)
        
        # Group results by entity
        entity_info = {}
        for result in results:
            entity_uri = result['entity']
            if entity_uri not in entity_info:
                entity_info[entity_uri] = {'properties': []}
            
            entity_info[entity_uri]['properties'].append({
                'property': result['property'],
                'value': result['value']
            })
        
        return entity_info
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the knowledge graph.
        
        Returns:
            Dictionary containing graph statistics
        """
        stats = {
            'total_triples': len(self.graph),
            'total_entities': 0,
            'entities_by_type': {}
        }
        
        # Count entities by type
        type_query = f"""
        PREFIX : <{self.namespace_str}>
        SELECT ?type (COUNT(?entity) as ?count) WHERE {{
            ?entity rdf:type ?type .
            FILTER(STRSTARTS(STR(?type), "{self.namespace_str}"))
        }}
        GROUP BY ?type
        """
        
        type_results = self.query_sparql(type_query)
        for result in type_results:
            entity_type = result['type'].replace(self.namespace_str, '')
            count = int(result['count'])
            stats['entities_by_type'][entity_type] = count
            stats['total_entities'] += count
        
        return stats
    
    def save_graph(self, output_path: Path, format: str = "turtle"):
        """Save the knowledge graph to a file.
        
        Args:
            output_path: Path to save the graph
            format: RDF serialization format (turtle, xml, n3, etc.)
        """
        try:
            self.graph.serialize(destination=output_path, format=format)
            print(f"✅ Saved knowledge graph to {output_path}")
        except Exception as e:
            print(f"❌ Failed to save graph: {e}")
    
    def load_graph(self, input_path: Path, format: str = "turtle"):
        """Load a knowledge graph from a file.
        
        Args:
            input_path: Path to load the graph from
            format: RDF serialization format
        """
        try:
            self.graph.parse(input_path, format=format)
            print(f"✅ Loaded knowledge graph from {input_path}")
        except Exception as e:
            print(f"❌ Failed to load graph: {e}")