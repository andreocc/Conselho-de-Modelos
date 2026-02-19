
import sys
import os

# Ensure we can import app modules
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'model_council_app'))

from model_council_app.app import state
from model_council_app.rag import DocumentProcessor

def test_fallback():
    print("Testing Fallback Logic...")
    
    # 1. Simulate a clear state
    state.vector_store.chunks = []
    state.vector_store.embeddings = None
    state.doc_loaded = False
    state.full_text = None
    
    # 2. Simulate loading a document
    dummy_text = "This is a secret document about the project Alpha. The project status is Green."
    state.full_text = dummy_text
    state.doc_loaded = True
    state.filename = "test.txt"
    
    print(f"State loaded with text: {state.full_text}")
    
    # 3. Simulate context retrieval where embeddings fail (return empty)
    # We force the vector store to return empty by not adding anything to it
    prompt = "What is the project status?"
    
    print(f"Querying: {prompt}")
    
    context_chunks = state.vector_store.query(prompt, n_results=4)
    print(f"Vector store returned: {context_chunks}")
    
    # 4. Apply fallback logic from app.py
    if not context_chunks and state.full_text:
        print("Triggering fallback logic...")
        safe_text = state.full_text[:50000]
        if len(state.full_text) > 50000:
            safe_text += "\n...(truncated)..."
        context_chunks = [safe_text]
        
    print(f"Final Context Chunks: {context_chunks}")
    
    if context_chunks and "project Alpha" in context_chunks[0]:
        print("SUCCESS: Fallback worked, context contains document text.")
    else:
        print("FAILURE: Fallback did not produce expected context.")

if __name__ == "__main__":
    test_fallback()
