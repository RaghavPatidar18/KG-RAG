"""SPARQL query generation and execution utilities."""

from typing import List, Dict, Any, Optional
import re
from src.utils.config import Config

class SPARQLQueryGenerator:
    """Generate SPARQL queries for common question patterns."""
    
    def __init__(self, namespace: str = None):
        self.namespace = namespace or Config.KG_NAMESPACE
        
        # Define query templates for common question patterns
        self.query_templates = {
            'who_founded': """
                PREFIX : <{namespace}>
                SELECT ?founder ?founderName WHERE {{
                    ?org :hasName ?orgName .
                    FILTER(CONTAINS(LCASE(?orgName), LCASE("{entity}")))
                    ?org :foundedBy ?founder .
                    ?founder :hasName ?founderName .
                }}
            """,
            
            'what_products': """
                PREFIX : <{namespace}>
                SELECT ?product ?productName WHERE {{
                    ?org :hasName ?orgName .
                    FILTER(CONTAINS(LCASE(?orgName), LCASE("{entity}")))
                    ?org :develops ?product .
                    ?product :hasName ?productName .
                }}
            """,
            
            'where_located': """
                PREFIX : <{namespace}>
                SELECT ?location ?locationName WHERE {{
                    ?org :hasName ?orgName .
                    FILTER(CONTAINS(LCASE(?orgName), LCASE("{entity}")))
                    ?org :headquarteredIn ?location .
                    ?location :hasName ?locationName .
                }}
            """,
            
            'when_founded': """
                PREFIX : <{namespace}>
                SELECT ?year WHERE {{
                    ?org :hasName ?orgName .
                    FILTER(CONTAINS(LCASE(?orgName), LCASE("{entity}")))
                    ?org :foundedYear ?year .
                }}
            """,
            
            'how_many_employees': """
                PREFIX : <{namespace}>
                SELECT ?count WHERE {{
                    ?org :hasName ?orgName .
                    FILTER(CONTAINS(LCASE(?orgName), LCASE("{entity}")))
                    ?org :hasEmployeeCount ?count .
                }}
            """,
            
            'what_revenue': """
                PREFIX : <{namespace}>
                SELECT ?revenue WHERE {{
                    ?org :hasName ?orgName .
                    FILTER(CONTAINS(LCASE(?orgName), LCASE("{entity}")))
                    ?org :hasRevenue ?revenue .
                }}
            """,
            
            'who_partners': """
                PREFIX : <{namespace}>
                SELECT ?partner ?partnerName WHERE {{
                    ?org :hasName ?orgName .
                    FILTER(CONTAINS(LCASE(?orgName), LCASE("{entity}")))
                    ?org :partnersWith ?partner .
                    ?partner :hasName ?partnerName .
                }}
            """,
            
            'what_industries': """
                PREFIX : <{namespace}>
                SELECT ?industry ?industryName WHERE {{
                    ?org :hasName ?orgName .
                    FILTER(CONTAINS(LCASE(?orgName), LCASE("{entity}")))
                    ?org :servesIndustry ?industry .
                    ?industry :hasName ?industryName .
                }}
            """,
            
            'entity_info': """
                PREFIX : <{namespace}>
                SELECT ?property ?value WHERE {{
                    ?entity :hasName ?name .
                    FILTER(CONTAINS(LCASE(?name), LCASE("{entity}")))
                    ?entity ?property ?value .
                }}
            """,
            
            'all_organizations': """
                PREFIX : <{namespace}>
                SELECT ?org ?name WHERE {{
                    ?org rdf:type :Organization .
                    ?org :hasName ?name .
                }}
            """,
            
            'all_products': """
                PREFIX : <{namespace}>
                SELECT ?product ?name WHERE {{
                    ?product rdf:type :Product .
                    ?product :hasName ?name .
                }}
            """,
            
            'all_people': """
                PREFIX : <{namespace}>
                SELECT ?person ?name ?role WHERE {{
                    ?person rdf:type :Person .
                    ?person :hasName ?name .
                    OPTIONAL {{ ?person :hasRole ?role }}
                }}
            """
        }
    
    def detect_question_type(self, question: str) -> tuple:
        """Detect the type of question and extract the main entity.
        
        Args:
            question: Natural language question
            
        Returns:
            Tuple of (question_type, entity)
        """
        question_lower = question.lower()
        
        # Extract potential entity names (capitalize words that might be proper nouns)
        entity_patterns = [
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',  # Capitalized words
            r'\b(techcorp|ai platform|cloud services)\b'  # Known entities
        ]
        
        entities = []
        for pattern in entity_patterns:
            matches = re.findall(pattern, question, re.IGNORECASE)
            entities.extend(matches)
        
        # Use the first found entity or default to "TechCorp"
        entity = entities[0] if entities else "TechCorp"
        
        # Question type detection patterns
        if any(word in question_lower for word in ['who founded', 'who created', 'who established']):
            return 'who_founded', entity
        elif any(word in question_lower for word in ['what products', 'what does', 'products']):
            return 'what_products', entity
        elif any(word in question_lower for word in ['where located', 'where is', 'headquarters']):
            return 'where_located', entity
        elif any(word in question_lower for word in ['when founded', 'when established', 'founded']):
            return 'when_founded', entity
        elif any(word in question_lower for word in ['how many employees', 'employee count', 'employees']):
            return 'how_many_employees', entity
        elif any(word in question_lower for word in ['revenue', 'income', 'earnings']):
            return 'what_revenue', entity
        elif any(word in question_lower for word in ['partners', 'partnerships', 'collaborates']):
            return 'who_partners', entity
        elif any(word in question_lower for word in ['industries', 'sectors', 'serves']):
            return 'what_industries', entity
        elif any(word in question_lower for word in ['list organizations', 'all companies']):
            return 'all_organizations', entity
        elif any(word in question_lower for word in ['list products', 'all products']):
            return 'all_products', entity
        elif any(word in question_lower for word in ['list people', 'all people', 'employees']):
            return 'all_people', entity
        else:
            return 'entity_info', entity
    
    def generate_query(self, question: str) -> str:
        """Generate a SPARQL query for a natural language question.
        
        Args:
            question: Natural language question
            
        Returns:
            SPARQL query string
        """
        question_type, entity = self.detect_question_type(question)
        
        if question_type in self.query_templates:
            query = self.query_templates[question_type].format(
                namespace=self.namespace,
                entity=entity
            )
            return query.strip()
        else:
            # Fallback to entity info query
            return self.query_templates['entity_info'].format(
                namespace=self.namespace,
                entity=entity
            ).strip()
    
    def format_results(self, results: List[Dict[str, Any]], question_type: str) -> str:
        """Format SPARQL query results into natural language.
        
        Args:
            results: Query results from SPARQL execution
            question_type: Type of question that was asked
            
        Returns:
            Formatted natural language response
        """
        if not results:
            return "I couldn't find any information about that in the knowledge graph."
        
        if question_type == 'who_founded':
            founders = [result.get('founderName', 'Unknown') for result in results]
            if len(founders) == 1:
                return f"The company was founded by {founders[0]}."
            else:
                return f"The company was founded by {', '.join(founders[:-1])} and {founders[-1]}."
        
        elif question_type == 'what_products':
            products = [result.get('productName', 'Unknown') for result in results]
            if len(products) == 1:
                return f"The main product is {products[0]}."
            else:
                return f"The products include: {', '.join(products)}."
        
        elif question_type == 'where_located':
            location = results[0].get('locationName', 'Unknown')
            return f"The company is located in {location}."
        
        elif question_type == 'when_founded':
            year = results[0].get('year', 'Unknown')
            return f"The company was founded in {year}."
        
        elif question_type == 'how_many_employees':
            count = results[0].get('count', 'Unknown')
            return f"The company has {count} employees."
        
        elif question_type == 'what_revenue':
            revenue = results[0].get('revenue', 'Unknown')
            if revenue != 'Unknown':
                revenue_millions = int(revenue) / 1000000
                return f"The company's revenue is ${revenue_millions:.0f} million."
            return f"The company's revenue is {revenue}."
        
        elif question_type == 'who_partners':
            partners = [result.get('partnerName', 'Unknown') for result in results]
            if partners:
                return f"The company partners with: {', '.join(partners)}."
            return "No partnership information found."
        
        elif question_type == 'what_industries':
            industries = [result.get('industryName', 'Unknown') for result in results]
            if industries:
                return f"The company serves these industries: {', '.join(industries)}."
            return "No industry information found."
        
        elif question_type == 'all_organizations':
            orgs = [result.get('name', 'Unknown') for result in results]
            return f"Organizations in the knowledge graph: {', '.join(orgs)}."
        
        elif question_type == 'all_products':
            products = [result.get('name', 'Unknown') for result in results]
            return f"Products in the knowledge graph: {', '.join(products)}."
        
        elif question_type == 'all_people':
            people = []
            for result in results:
                name = result.get('name', 'Unknown')
                role = result.get('role', '')
                if role:
                    people.append(f"{name} ({role})")
                else:
                    people.append(name)
            return f"People in the knowledge graph: {', '.join(people)}."
        
        else:  # entity_info
            info_parts = []
            for result in results:
                prop = result.get('property', '').replace(self.namespace, '')
                value = result.get('value', '')
                if prop and value and prop not in ['hasName']:
                    info_parts.append(f"{prop}: {value}")
            
            if info_parts:
                return f"Information found: {'; '.join(info_parts[:5])}."  # Limit to 5 items
            return "No specific information found."

class SPARQLQueryEngine:
    """Execute SPARQL queries and provide natural language responses."""
    
    def __init__(self, kg_builder):
        self.kg_builder = kg_builder
        self.query_generator = SPARQLQueryGenerator()
    
    def answer_question(self, question: str) -> Dict[str, Any]:
        """Answer a natural language question using the knowledge graph.
        
        Args:
            question: Natural language question
            
        Returns:
            Dictionary containing the answer and metadata
        """
        # Generate SPARQL query
        query = self.query_generator.generate_query(question)
        question_type, entity = self.query_generator.detect_question_type(question)
        
        # Execute query
        results = self.kg_builder.query_sparql(query)
        
        # Format response
        answer = self.query_generator.format_results(results, question_type)
        
        return {
            'question': question,
            'answer': answer,
            'sparql_query': query,
            'raw_results': results,
            'question_type': question_type,
            'entity': entity
        }