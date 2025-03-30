"""
Chatbot application using Flask and the DataPreprocessor for document Q&A.
"""
from flask import Flask, request, jsonify, render_template
from nlp.data_preprocessing import DataPreprocessor
import os
import atexit
import signal
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()
groq_key = os.getenv("GROQ_API_KEY")

# Initialize Flask app
app = Flask(__name__)

# Initialize DataPreprocessor and Groq client
preprocessor = None
groq_client = None

def initialize_resources():
    """Initialize global resources"""
    global preprocessor, groq_client
    preprocessor = DataPreprocessor()
    groq_client = Groq(api_key=groq_key)

def cleanup_resources():
    """Cleanup resources before shutdown"""
    global preprocessor
    if preprocessor:
        if hasattr(preprocessor, 'embedding_model'):
            del preprocessor.embedding_model
        if hasattr(preprocessor, 'chroma_client'):
            preprocessor.chroma_client.reset()
        del preprocessor

# Register cleanup function
atexit.register(cleanup_resources)

# Handle signals
def signal_handler(sig, frame):
    print("Cleaning up resources...")
    cleanup_resources()
    os._exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Initialize resources
initialize_resources()

def prompt_maker(question: str, n_results: int = 2) -> tuple[str, str]:
    print("The function prompt_maker is running")
    """
    Create prompts by querying the database for relevant context.
    
    Args:
        question: User's question
        n_results: Number of relevant chunks to retrieve
    
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    # Query the database for relevant chunks
    relevant_chunks = preprocessor.query_database(question, n_results=n_results)
    print(f"Found {len(relevant_chunks)} relevant chunks")
    
    # Format the context
    context = "\n\n---\n\n".join(relevant_chunks)
    
    # Create system prompt
    system_prompt = """
    You are a digital consultant specializing in Australia's evolving greenhouse gas (GHG) emission regulations. 
    Your task is to help companies navigate the complexities of compliance, accurate emission calculations, and industry-specific scope definitions. 
    Use the following context to provide tailored, concise, and accurate guidance. Ensure the response is practical, actionable, and aligned with the most recent regulatory updates.
    If the answer is not available or unclear, state that you do not know.
    Use five sentences maximum and keep the answer concise.
    """
    
    # Create user prompt with context and question
    user_prompt = f"""
    Based on the following context, please answer the question.
    
    Context:
    {context}

    Question: {question}
    """
    
    return system_prompt, user_prompt

def generate_response(question: str) -> str:
    print("The function generate_response is running")
    """
    Generate a response using Groq's model with context from documents.
    
    Args:
        question: User's question
    
    Returns:
        Generated answer
    """
    try:
        # Get prompts with relevant context
        system_prompt, user_prompt = prompt_maker(question)
        
        # Generate response using Groq
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        return "I apologize, but I encountered an error while processing your question."

@app.route('/')
def home():
    print("The function home is running")
    """Render the chat interface."""
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    print("The function ask is running")
    """
    Handle chat requests and generate responses.
    
    Expected JSON input: {"question": "user question here"}
    Returns JSON: {"answer": "generated response"}
    """
    try:
        # Get question from request
        data = request.get_json()
        question = data.get('question')
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400

        # Generate response
        answer = generate_response(question)
        
        return jsonify({'answer': answer})
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({'error': 'An error occurred processing your request'}), 500

# @app.route('/refresh-docs', methods=['POST'])
# def refresh_documents():
#     print("The function refresh_documents is running")
#     """
#     Endpoint to refresh the document index.
#     Returns JSON: {"status": "success/failure", "message": "status message"}
#     """
#     try:
#         preprocessor.index_documents()
#         return jsonify({
#             'status': 'success',
#             'message': 'Documents reindexed successfully'
#         })
#     except Exception as e:
#         return jsonify({
#             'status': 'failure',
#             'message': f'Error refreshing documents: {str(e)}'
#         }), 500

def initialize_chatbot():
    print("The function initialize_chatbot is running")
    """
    Initialize the chatbot by indexing documents if not already done.
    """
    try:
        # Check if documents are already indexed
        test_query = preprocessor.get_similar_chunks("test", n_results=1)
        if not test_query:
            preprocessor.index_documents()
    except Exception:
        preprocessor.index_documents()

if __name__ == "__main__":
    print("Starting chatbot application...")
    try:
        app.run(debug=False, port=5000)  # Set debug=False to avoid duplicate resource initialization
    except Exception as e:
        print(f"Error running application: {str(e)}")
    finally:
        cleanup_resources() 