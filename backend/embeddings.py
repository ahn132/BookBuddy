from pinecone import Pinecone
import config
from typing import List, Dict
import re

class TextEmbedder:
    def __init__(self):
        # Initialize Pinecone
        self.pc = Pinecone(api_key=config.PINECONE_API_KEY)
        self.index = self.pc.Index(config.PINECONE_INDEX_NAME)

    def chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        """Split text into chunks of approximately chunk_size words."""
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = []
        current_size = 0

        for para in paragraphs:
            words = para.split()
            if current_size + len(words) > chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_size = 0
            current_chunk.extend(words)
            current_size += len(words)

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks

    def create_embeddings(self, text: str, chapter_name: str) -> List[Dict]:
        """Create embeddings for text chunks and prepare for Pinecone storage."""
        # Split text into chunks
        chunks = self.chunk_text(text)
        print(chunks)
        
        # Prepare vectors for Pinecone
        vectors = []
        for i, chunk in enumerate(chunks):
            vector = {
                'id': f"{chapter_name}_{i}",
                'values': chunk,  # Pinecone will handle the embedding
                'metadata': {
                    'text': chunk,
                    'chapter': chapter_name,
                    'chunk_index': i
                }
            }
            vectors.append(vector)
        
        print(vectors)
        return vectors

    def store_in_pinecone(self, vectors: List[Dict]):
        """Store vectors in Pinecone index."""
        # Upsert vectors in batches of 100
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.index.upsert(vectors=batch)

    def process_book_chapter(self, chapter_text: str, chapter_name: str):
        """Process a single chapter and store it in Pinecone."""
        vectors = self.create_embeddings(chapter_text, chapter_name)
        #self.store_in_pinecone(vectors)
        return len(vectors)  # Return number of chunks processed 