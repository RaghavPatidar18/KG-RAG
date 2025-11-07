"""Text loading and document processing utilities."""

import json
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class Document:
    """Represents a document with metadata."""
    id: str
    title: str
    content: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class TextLoader:
    """Load and process text documents from various sources."""
    
    def __init__(self):
        pass
    
    def load_json_documents(self, file_path: Path) -> List[Document]:
        """Load documents from a JSON file.
        
        Args:
            file_path: Path to the JSON file containing documents
            
        Returns:
            List of Document objects
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        documents = []
        for item in data:
            doc = Document(
                id=item.get('id', ''),
                title=item.get('title', ''),
                content=item.get('content', ''),
                metadata=item.get('metadata', {})
            )
            documents.append(doc)
        
        return documents
    
    def load_text_file(self, file_path: Path, doc_id: str = None) -> Document:
        """Load a single text file as a document.
        
        Args:
            file_path: Path to the text file
            doc_id: Optional document ID
            
        Returns:
            Document object
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        doc_id = doc_id or file_path.stem
        title = file_path.stem.replace('_', ' ').title()
        
        return Document(
            id=doc_id,
            title=title,
            content=content,
            metadata={'source_file': str(file_path)}
        )
    
    def chunk_document(self, document: Document, chunk_size: int = 500, overlap: int = 50) -> List[Document]:
        """Split a document into smaller chunks.
        
        Args:
            document: Document to chunk
            chunk_size: Maximum size of each chunk in characters
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of chunked documents
        """
        content = document.content
        chunks = []
        
        start = 0
        chunk_id = 0
        
        while start < len(content):
            end = start + chunk_size
            chunk_content = content[start:end]
            
            # Try to break at sentence boundaries
            if end < len(content):
                last_period = chunk_content.rfind('.')
                last_newline = chunk_content.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > start + chunk_size // 2:  # Only break if it's not too early
                    end = start + break_point + 1
                    chunk_content = content[start:end]
            
            chunk_doc = Document(
                id=f"{document.id}_chunk_{chunk_id}",
                title=f"{document.title} (Part {chunk_id + 1})",
                content=chunk_content.strip(),
                metadata={
                    **document.metadata,
                    'parent_doc_id': document.id,
                    'chunk_id': chunk_id,
                    'start_pos': start,
                    'end_pos': end
                }
            )
            
            chunks.append(chunk_doc)
            chunk_id += 1
            start = end - overlap
        
        return chunks