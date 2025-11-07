"""Named Entity Recognition using spaCy with custom patterns."""

import spacy
from spacy.matcher import Matcher
from typing import List, Dict, Tuple, Set
import re

class CustomNER:
    """Custom Named Entity Recognition for the TechCorp domain."""
    
    def __init__(self):
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Please install spaCy English model: python -m spacy download en_core_web_sm")
            raise
        
        # Initialize matcher for custom patterns
        self.matcher = Matcher(self.nlp.vocab)
        self._add_custom_patterns()
        
        # Define entity type mappings
        self.entity_type_mapping = {
            'PERSON': 'Person',
            'ORG': 'Organization', 
            'GPE': 'Location',
            'MONEY': 'FinancialAmount',
            'DATE': 'Date',
            'CARDINAL': 'Number',
            'PRODUCT': 'Product',
            'TECHNOLOGY': 'Technology',
            'INDUSTRY': 'Industry'
        }
    
    def _add_custom_patterns(self):
        """Add custom patterns for domain-specific entities."""
        
        # Technology patterns
        tech_patterns = [
            [{"LOWER": "artificial"}, {"LOWER": "intelligence"}],
            [{"LOWER": "machine"}, {"LOWER": "learning"}],
            [{"LOWER": "natural"}, {"LOWER": "language"}, {"LOWER": "processing"}],
            [{"LOWER": "computer"}, {"LOWER": "vision"}],
            [{"LOWER": "cloud"}, {"LOWER": "computing"}],
            [{"LOWER": "quantum"}, {"LOWER": "machine"}, {"LOWER": "learning"}],
            [{"LOWER": "federated"}, {"LOWER": "learning"}],
            [{"LOWER": "explainable"}, {"LOWER": "ai"}]
        ]
        self.matcher.add("TECHNOLOGY", tech_patterns)
        
        # Product patterns
        product_patterns = [
            [{"LOWER": "ai"}, {"LOWER": "platform"}],
            [{"LOWER": "cloud"}, {"LOWER": "services"}],
            [{"LOWER": "techcorp"}, {"LOWER": "ai"}, {"LOWER": "platform"}],
            [{"LOWER": "techcorp"}, {"LOWER": "cloud"}, {"LOWER": "services"}]
        ]
        self.matcher.add("PRODUCT", product_patterns)
        
        # Industry patterns
        industry_patterns = [
            [{"LOWER": "healthcare"}],
            [{"LOWER": "finance"}],
            [{"LOWER": "retail"}],
            [{"LOWER": "technology"}]
        ]
        self.matcher.add("INDUSTRY", industry_patterns)
    
    def extract_entities(self, text: str) -> List[Dict[str, any]]:
        """Extract entities from text using spaCy NER and custom patterns.
        
        Args:
            text: Input text to process
            
        Returns:
            List of entity dictionaries with text, label, start, end positions
        """
        doc = self.nlp(text)
        entities = []
        
        # Extract standard spaCy entities
        for ent in doc.ents:
            entity_type = self.entity_type_mapping.get(ent.label_, ent.label_)
            entities.append({
                'text': ent.text,
                'label': entity_type,
                'start': ent.start_char,
                'end': ent.end_char,
                'confidence': 0.8  # Default confidence for spaCy entities
            })
        
        # Extract custom pattern matches
        matches = self.matcher(doc)
        for match_id, start, end in matches:
            span = doc[start:end]
            label = self.nlp.vocab.strings[match_id]
            
            # Check if this span overlaps with existing entities
            overlaps = any(
                (span.start_char < ent['end'] and span.end_char > ent['start'])
                for ent in entities
            )
            
            if not overlaps:
                entities.append({
                    'text': span.text,
                    'label': label.title(),
                    'start': span.start_char,
                    'end': span.end_char,
                    'confidence': 0.9  # Higher confidence for custom patterns
                })
        
        return entities
    
    def extract_relations(self, text: str, entities: List[Dict]) -> List[Dict[str, any]]:
        """Extract simple relations between entities based on patterns.
        
        Args:
            text: Input text
            entities: List of extracted entities
            
        Returns:
            List of relation dictionaries
        """
        doc = self.nlp(text)
        relations = []
        
        # Simple pattern-based relation extraction
        relation_patterns = [
            (r'(\w+(?:\s+\w+)*)\s+(?:founded|established|created)\s+(\w+(?:\s+\w+)*)', 'foundedBy'),
            (r'(\w+(?:\s+\w+)*)\s+(?:headquartered|located|based)\s+in\s+(\w+(?:\s+\w+)*)', 'headquarteredIn'),
            (r'(\w+(?:\s+\w+)*)\s+(?:serves|works with|targets)\s+(\w+(?:\s+\w+)*)', 'servesIndustry'),
            (r'(\w+(?:\s+\w+)*)\s+(?:develops|creates|builds)\s+(\w+(?:\s+\w+)*)', 'develops'),
            (r'(\w+(?:\s+\w+)*)\s+(?:partners with|collaborates with)\s+(\w+(?:\s+\w+)*)', 'partnersWith'),
            (r'(\w+(?:\s+\w+)*)\s+(?:led by|headed by)\s+(\w+(?:\s+\w+)*)', 'ledBy'),
            (r'(\w+(?:\s+\w+)*)\s+(?:specializes in|focuses on)\s+(\w+(?:\s+\w+)*)', 'specializesIn')
        ]
        
        for pattern, relation_type in relation_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                subject = match.group(1).strip()
                object_entity = match.group(2).strip()
                
                relations.append({
                    'subject': subject,
                    'predicate': relation_type,
                    'object': object_entity,
                    'confidence': 0.7,
                    'start': match.start(),
                    'end': match.end()
                })
        
        return relations
    
    def process_document(self, text: str) -> Dict[str, any]:
        """Process a document to extract entities and relations.
        
        Args:
            text: Document text to process
            
        Returns:
            Dictionary containing entities and relations
        """
        entities = self.extract_entities(text)
        relations = self.extract_relations(text, entities)
        
        return {
            'entities': entities,
            'relations': relations,
            'text': text
        }