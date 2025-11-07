"""Generate RDF triples from extracted entities and relations."""

from typing import List, Dict, Tuple, Set
import re
from urllib.parse import quote
from src.utils.config import Config

class TripleGenerator:
    """Generate RDF triples from NLP extraction results."""
    
    def __init__(self, namespace: str = None):
        self.namespace = namespace or Config.KG_NAMESPACE
        self.entity_counter = {}  # Track entity instances for unique URIs
        
    def _clean_entity_name(self, name: str) -> str:
        """Clean entity name for use in URIs."""
        # Remove special characters and normalize
        cleaned = re.sub(r'[^\w\s-]', '', name)
        cleaned = re.sub(r'\s+', '_', cleaned.strip())
        return cleaned.lower()
    
    def _generate_uri(self, entity_name: str, entity_type: str = None) -> str:
        """Generate a unique URI for an entity."""
        cleaned_name = self._clean_entity_name(entity_name)
        
        # Add type prefix if provided
        if entity_type:
            type_prefix = entity_type.lower()
            uri_base = f"{type_prefix}_{cleaned_name}"
        else:
            uri_base = cleaned_name
        
        # Ensure uniqueness
        if uri_base in self.entity_counter:
            self.entity_counter[uri_base] += 1
            uri_base = f"{uri_base}_{self.entity_counter[uri_base]}"
        else:
            self.entity_counter[uri_base] = 0
        
        return f"{self.namespace}{uri_base}"
    
    def _get_predicate_uri(self, relation_type: str) -> str:
        """Get the predicate URI for a relation type."""
        predicate_mapping = {
            'foundedBy': 'foundedBy',
            'headquarteredIn': 'headquarteredIn', 
            'servesIndustry': 'servesIndustry',
            'develops': 'develops',
            'partnersWith': 'partnersWith',
            'ledBy': 'leadsResearch',
            'specializesIn': 'specializesIn',
            'usesProduct': 'usesProduct',
            'hasRole': 'hasRole'
        }
        
        predicate = predicate_mapping.get(relation_type, relation_type)
        return f"{self.namespace}{predicate}"
    
    def generate_entity_triples(self, entities: List[Dict]) -> List[Tuple[str, str, str]]:
        """Generate triples for entity type assertions.
        
        Args:
            entities: List of entity dictionaries from NER
            
        Returns:
            List of (subject, predicate, object) triples
        """
        triples = []
        entity_uris = {}  # Map entity text to URI
        
        for entity in entities:
            entity_text = entity['text']
            entity_type = entity['label']
            
            # Generate URI for the entity
            if entity_text not in entity_uris:
                entity_uri = self._generate_uri(entity_text, entity_type)
                entity_uris[entity_text] = entity_uri
            else:
                entity_uri = entity_uris[entity_text]
            
            # Add type assertion triple
            type_uri = f"{self.namespace}{entity_type}"
            triples.append((entity_uri, "rdf:type", type_uri))
            
            # Add name property
            triples.append((entity_uri, f"{self.namespace}hasName", f'"{entity_text}"'))
        
        return triples, entity_uris
    
    def generate_relation_triples(self, relations: List[Dict], entity_uris: Dict[str, str]) -> List[Tuple[str, str, str]]:
        """Generate triples for relations between entities.
        
        Args:
            relations: List of relation dictionaries
            entity_uris: Mapping of entity text to URIs
            
        Returns:
            List of (subject, predicate, object) triples
        """
        triples = []
        
        for relation in relations:
            subject_text = relation['subject']
            object_text = relation['object']
            predicate = relation['predicate']
            
            # Get or create URIs for subject and object
            if subject_text not in entity_uris:
                subject_uri = self._generate_uri(subject_text)
                entity_uris[subject_text] = subject_uri
            else:
                subject_uri = entity_uris[subject_text]
            
            if object_text not in entity_uris:
                object_uri = self._generate_uri(object_text)
                entity_uris[object_text] = object_uri
            else:
                object_uri = entity_uris[object_text]
            
            # Generate predicate URI
            predicate_uri = self._get_predicate_uri(predicate)
            
            # Add relation triple
            triples.append((subject_uri, predicate_uri, object_uri))
        
        return triples
    
    def generate_document_triples(self, doc_id: str, nlp_results: Dict) -> List[Tuple[str, str, str]]:
        """Generate all triples for a document's NLP results.
        
        Args:
            doc_id: Document identifier
            nlp_results: Results from NLP processing containing entities and relations
            
        Returns:
            List of all generated triples
        """
        all_triples = []
        
        # Generate entity triples
        entity_triples, entity_uris = self.generate_entity_triples(nlp_results['entities'])
        all_triples.extend(entity_triples)
        
        # Generate relation triples
        relation_triples = self.generate_relation_triples(nlp_results['relations'], entity_uris)
        all_triples.extend(relation_triples)
        
        # Add document metadata triples
        doc_uri = self._generate_uri(doc_id, "document")
        all_triples.append((doc_uri, "rdf:type", f"{self.namespace}Document"))
        all_triples.append((doc_uri, f"{self.namespace}hasName", f'"{doc_id}"'))
        
        # Link entities to document
        for entity_text, entity_uri in entity_uris.items():
            all_triples.append((entity_uri, f"{self.namespace}mentionedIn", doc_uri))
        
        return all_triples
    
    def add_hardcoded_facts(self) -> List[Tuple[str, str, str]]:
        """Add some hardcoded facts about TechCorp for demo purposes."""
        triples = []
        
        # TechCorp basic info
        techcorp_uri = f"{self.namespace}organization_techcorp"
        sarah_uri = f"{self.namespace}person_sarah_johnson"
        michael_uri = f"{self.namespace}person_michael_chen"
        sf_uri = f"{self.namespace}location_san_francisco"
        ai_platform_uri = f"{self.namespace}product_ai_platform"
        cloud_services_uri = f"{self.namespace}product_cloud_services"
        
        # Organization facts
        triples.extend([
            (techcorp_uri, "rdf:type", f"{self.namespace}Organization"),
            (techcorp_uri, f"{self.namespace}hasName", '"TechCorp"'),
            (techcorp_uri, f"{self.namespace}foundedYear", '"2010"^^xsd:gYear'),
            (techcorp_uri, f"{self.namespace}hasEmployeeCount", '"5000"^^xsd:integer'),
            (techcorp_uri, f"{self.namespace}hasRevenue", '"500000000"^^xsd:decimal'),
            
            # People
            (sarah_uri, "rdf:type", f"{self.namespace}Person"),
            (sarah_uri, f"{self.namespace}hasName", '"Sarah Johnson"'),
            (sarah_uri, f"{self.namespace}hasRole", '"CEO"'),
            
            (michael_uri, "rdf:type", f"{self.namespace}Person"),
            (michael_uri, f"{self.namespace}hasName", '"Michael Chen"'),
            (michael_uri, f"{self.namespace}hasRole", '"CTO"'),
            
            # Location
            (sf_uri, "rdf:type", f"{self.namespace}Location"),
            (sf_uri, f"{self.namespace}hasName", '"San Francisco"'),
            
            # Products
            (ai_platform_uri, "rdf:type", f"{self.namespace}Product"),
            (ai_platform_uri, f"{self.namespace}hasName", '"TechCorp AI Platform"'),
            (ai_platform_uri, f"{self.namespace}launchedYear", '"2018"^^xsd:gYear'),
            
            (cloud_services_uri, "rdf:type", f"{self.namespace}Product"),
            (cloud_services_uri, f"{self.namespace}hasName", '"TechCorp Cloud Services"'),
            (cloud_services_uri, f"{self.namespace}launchedYear", '"2020"^^xsd:gYear'),
            
            # Relations
            (techcorp_uri, f"{self.namespace}foundedBy", sarah_uri),
            (techcorp_uri, f"{self.namespace}foundedBy", michael_uri),
            (techcorp_uri, f"{self.namespace}headquarteredIn", sf_uri),
            (techcorp_uri, f"{self.namespace}develops", ai_platform_uri),
            (techcorp_uri, f"{self.namespace}develops", cloud_services_uri),
        ])
        
        return triples