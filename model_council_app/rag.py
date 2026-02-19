import os
import PyPDF2
import docx
import numpy as np
import ollama
import requests
from bs4 import BeautifulSoup
import config

class DocumentProcessor:
    @staticmethod
    def load_pdf(file_bytes):
        pdf_reader = PyPDF2.PdfReader(file_bytes)
        text = ""
        for page in pdf_reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
        return text

    @staticmethod
    def load_docx(file_bytes):
        doc = docx.Document(file_bytes)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text

    @staticmethod
    def load_txt(file_bytes):
        return file_bytes.read().decode('utf-8')

    @staticmethod
    def load_url(url):
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
                
            text = soup.get_text()
            
            # Break into lines and remove leading/trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # Drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            print(f"Error scraping URL: {e}")
            return None

    @staticmethod
    def split_text(text, chunk_size=config.CHUNK_SIZE, overlap=config.CHUNK_OVERLAP):
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = start + chunk_size
            chunks.append(text[start:end])
            start += chunk_size - overlap
        return chunks

class VectorStore:
    def __init__(self):
        # Using Ollama for embeddings to avoid heavy python dependencies (torch, etc.)
        self.chunks = []
        self.embeddings = None
        self.embedding_model = "all-minilm" # Default lightweight model for ollama

    def _get_embedding_model_name(self):
        # Check if the preferred embedding model exists, else try to find one or fallback
        try:
            models_info = ollama.list()
            
            model_names = []
            # Robust parsing (same as council.py)
            source_list = []
            if hasattr(models_info, 'models'):
                source_list = models_info.models
            elif isinstance(models_info, dict) and 'models' in models_info:
                source_list = models_info['models']
            else:
                source_list = models_info
                
            for m in source_list:
                if hasattr(m, 'model'):
                    model_names.append(m.model)
                elif isinstance(m, dict):
                    model_names.append(m.get('model') or m.get('name'))
            
            # If our default is there, good.
            if any(self.embedding_model in m for m in model_names):
                return self.embedding_model
            
            # If not, look for common embedding models
            for known in ["nomic-embed-text", "mxbai-embed-large", "snowflake-arctic-embed"]:
                if any(known in m for m in model_names):
                    return known
            
            # Fallback to the first available model (not ideal but better than crash)
            if model_names:
                return model_names[0]
            
            return None
        except Exception as e:
            print(f"Error finding embedding model: {e}")
            return None

    def add_document(self, text, source_name="upload"):
        self.chunks = []
        self.embeddings = None

        new_chunks = DocumentProcessor.split_text(text)
        if not new_chunks:
            return 0
            
        self.chunks = new_chunks
        
        target_model = self._get_embedding_model_name()
        if not target_model:
            # If no model found, we can't embed. Return 0 to indicate failure or handle upstream.
            # For now let's just proceed and fail at embedding step with error log if needed, 
            # or try to pull?
            # Let's try to pull 'all-minilm' if we can't find it? 
            # Pulling is blocking and slow. Let's assume user has models or the app will warn.
            print("No models found for embedding.")
            return 0

        # Generate embeddings in batch if possible or loop
        embeddings = []
        for chunk in new_chunks:
            try:
                resp = ollama.embeddings(model=target_model, prompt=chunk)
                embeddings.append(resp['embedding'])
            except Exception as e:
                print(f"Embedding error: {e}")
                
        if not embeddings:
            return 0
            
        # Convert to numpy
        emb_matrix = np.array(embeddings)
        
        # Normalize
        norms = np.linalg.norm(emb_matrix, axis=1, keepdims=True)
        # Avoid divide by zero
        norms[norms == 0] = 1e-10
        self.embeddings = emb_matrix / norms
        
        return len(new_chunks)

    def query(self, prompt, n_results=3):
        if not self.chunks or self.embeddings is None:
            return []
            
        target_model = self._get_embedding_model_name()
        if not target_model:
            return []

        try:
            resp = ollama.embeddings(model=target_model, prompt=prompt)
            query_embedding = np.array(resp['embedding'])
        except:
            return []
        
        # Normalize query
        query_norm = np.linalg.norm(query_embedding)
        if query_norm == 0:
            return []
            
        query_embedding = query_embedding / query_norm
        
        # Cosine similarity
        scores = np.dot(query_embedding, self.embeddings.T)
        
        if len(scores) < n_results:
            n_results = len(scores)
            
        top_indices = np.argsort(scores)[-n_results:][::-1]
        
        results = [self.chunks[i] for i in top_indices]
        return results
