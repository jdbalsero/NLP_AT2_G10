import pdfplumber
import os
from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient
from chromadb.utils.embedding_functions import EmbeddingFunction


class MyEmbeddingFunction(EmbeddingFunction):
    def __init__(self):
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L12-v2')

    def __call__(self, input_texts):
        if isinstance(input_texts, str):
            input_texts = [input_texts]
        embeddings = self.model.encode(input_texts, convert_to_numpy=True)
        return embeddings.tolist()

class Embedding_Generation:
    def __init__(self):
        self.custom_embeddings = MyEmbeddingFunction()
        self.chroma_client = PersistentClient(path="chroma_persistent_storage")
        self.collection = self.chroma_client.get_or_create_collection(
            name="ghg_collection",
            embedding_function=self.custom_embeddings
        )

    def read_documents(self):
        current_wd = os.getcwd()
        data_path = os.path.join(current_wd, 'data')
        raw_documents = os.listdir(data_path)

        documents = []

        for file_name in raw_documents:
            with pdfplumber.open(os.path.join(data_path, file_name)) as pdf:
                text = ''
                for p in pdf.pages:
                    text += p.extract_text().replace('\n', ' ')
                documents.append({"id": file_name, "text": text})

        return documents

    def split_text(self, text, chunk_size=1000, chunk_overlap=20):
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start = end - chunk_overlap
        return chunks

    def chunk_generation(self, documents):
        chunked_documents = []
        for doc in documents:
            chunks = self.split_text(doc["text"])
            print("==== Splitting docs into chunks ====")
            for i, chunk in enumerate(chunks):
                chunked_documents.append({"id": f"{doc['id']}_chunk{i+1}", "text": chunk})
        
        return chunked_documents
        

    def generate_embeddings(self, chunked_documents):

        for chunk in chunked_documents:
            self.collection.add(
                ids=[chunk["id"]],
                embeddings = self.custom_embeddings([chunk["text"]]),
                metadatas=[{"source": chunk["id"]}],
                documents=[chunk["text"]]
            )

        print(f"Total chunks stored in ChromaDB: {self.collection.count()}")

        return True