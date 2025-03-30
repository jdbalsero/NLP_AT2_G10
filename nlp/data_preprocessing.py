"""
Data preprocessing module for handling PDF documents and text processing.
"""
import os
from typing import List, Dict, Union
import pdfplumber
from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient
from chromadb.utils.embedding_functions import EmbeddingFunction

class DataPreprocessor:
    def __init__(self, data_dir: str = 'nlp/data', storage_path: str = "chroma_persistent_storage"):
        print("Initializing DataPreprocessor...")
        """
        Initialize the data preprocessor.
        
        Args:
            data_dir: Directory containing PDF files
            storage_path: Path for ChromaDB storage
        """
        self.data_dir = data_dir
        self.storage_path = storage_path
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L12-v2')
        self.chroma_client = PersistentClient(path=storage_path)
        # Just get the collection if it exists
        self.collection = self._get_collection()

    def _get_collection(self):
        """Get existing ChromaDB collection."""
        print("Getting existing collection...")
        class CustomEmbeddingFunction(EmbeddingFunction):
            def __init__(self, model):
                self.model = model

            def __call__(self, input_texts: Union[str, List[str]]) -> List[List[float]]:
                if isinstance(input_texts, str):
                    input_texts = [input_texts]
                embeddings = self.model.encode(input_texts, convert_to_numpy=True)
                return embeddings.tolist()

        return self.chroma_client.get_or_create_collection(
            name="ghg_collection",
            embedding_function=CustomEmbeddingFunction(self.embedding_model)
        )

    def index_documents(self):
        """Alias for create_database for backward compatibility"""
        print("The function index_documents is running (alias for create_database)")
        return self.create_database()

    def create_database(self):
        """
        One-time process to create and populate the vector database.
        This should be run separately from the main application.
        """
        print("Creating and populating database...")
        documents = self._read_pdf_files()
        chunked_documents = []
        
        for doc in documents:
            chunks = self._split_text(doc["text"])
            chunked_documents.extend([
                {"id": f"{doc['id']}_chunk{i+1}", "text": chunk}
                for i, chunk in enumerate(chunks)
            ])
        
        # Prepare data for batch processing
        ids = [doc["id"] for doc in chunked_documents]
        texts = [doc["text"] for doc in chunked_documents]
        
        # Batch upsert to ChromaDB
        self.collection.upsert(
            ids=ids,
            documents=texts
        )
        print("Database creation completed!")

    def get_similar_chunks(self, query: str, n_results: int = 3) -> List[str]:
        """Alias for query_database for backward compatibility"""
        print("The function get_similar_chunks is running (alias for query_database)")
        return self.query_database(query, n_results)

    def query_database(self, query: str, n_results: int = 3) -> List[str]:
        """
        Query the existing database for similar chunks.
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of relevant document chunks
        """
        print("Querying database...")
        # Generate embedding for the query
        query_embedding = self.embedding_model.encode([query], convert_to_numpy=True)
        
        # Query the collection with embeddings
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=n_results
        )
        
        return [doc for sublist in results["documents"] for doc in sublist]

    # Keep these methods private as they're only used for database creation
    def _read_pdf_files(self) -> List[Dict[str, str]]:
        """Read and extract text from PDF files."""
        documents = []
        pdf_files = [f for f in os.listdir(self.data_dir) if f.endswith('.pdf')]
        
        for file_name in pdf_files:
            file_path = os.path.join(self.data_dir, file_name)
            try:
                with pdfplumber.open(file_path) as pdf:
                    text = ' '.join(page.extract_text().replace('\n', ' ') 
                                  for page in pdf.pages)
                    documents.append({"id": file_name, "text": text})
            except Exception as e:
                print(f"Error processing {file_name}: {str(e)}")
                continue
                
        return documents

    def _split_text(self, text: str, chunk_size: int = 1000, chunk_overlap: int = 20) -> List[str]:
        """Split text into overlapping chunks."""
        if not text:
            return []
            
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = min(start + chunk_size, text_length)
            chunks.append(text[start:end])
            start = end - chunk_overlap
            
        return chunks

# Example usage
if __name__ == "__main__":
    # This script is for creating the database
    print("Starting database creation process...")
    preprocessor = DataPreprocessor()
    preprocessor.create_database()