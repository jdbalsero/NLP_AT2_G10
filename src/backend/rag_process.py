import os
from dotenv import load_dotenv
from groq import Groq
from backend.embedding_generation import Embedding_Generation


class rag_process:
    def __init__(self):
        load_dotenv()
        self.embedding_class = Embedding_Generation()

    def run_embedding_process(self):

        documents = self.embedding_class.read_documents()
        chunks = self.embedding_class.chunk_generation(documents)
        generation = self.embedding_class.generate_embeddings(chunked_documents=chunks)

        if generation:
            return "Process Complete"
        else:
            return "Error in embedding generation"

    def query_documents(self, question, n_results=2):
        query_embedding = self.embedding_class.custom_embeddings([question])

        results = self.embedding_class.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            include=["documents", "metadatas"]
        )

        relevant_chunks = results["documents"][0]
        metadatas = results["metadatas"][0]
        
        # print("==== Returning relevant chunks ====")
        # print("\nDEBUG - Full metadata structure:")
        # for i, metadata in enumerate(metadatas):
        #     print(f"\nMetadata {i + 1}:")
        #     print("Keys:", metadata.keys())
        #     print("Full metadata:", metadata)
            

        return relevant_chunks, metadatas

    def generate_response(self, question, relevant_chunks, results_metadata):
        # Format context with source information
        formatted_chunks = []
        
        for i, (chunk, metadata) in enumerate(zip(relevant_chunks, results_metadata)):
            # Format with page information if available
            source_info = f"Source: {metadata.get('source', 'Unknown')}"
            if metadata.get('chunk_number'):
                source_info += f" (Chunk {metadata['chunk_number']})"
            
            formatted_chunk = f"{source_info}\n{chunk}"
            formatted_chunks.append(formatted_chunk)
            
        context = "\n\n---\n\n".join(formatted_chunks)  # Added separator for better readability
        
        prompt = (
            "You are a digital consultant specializing in Australia's evolving greenhouse gas (GHG) emission regulations. "
            "Your task is to help companies navigate the complexities of compliance, accurate emission calculations, and industry-specific scope definitions. "
            "Use the following context to provide tailored, concise, and accurate guidance. Ensure the response is practical, actionable, and aligned with the most recent regulatory updates. "
            "If the answer is not available or unclear, state that you do not know. "
            "\n\nContext:\n" + context + "\n\nQuestion:\n" + question
        )

        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt},
            ],
        )

        answer = response.choices[0].message.content
        return answer
