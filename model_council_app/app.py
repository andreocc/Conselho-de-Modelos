import os
from flask import Flask, render_template, request, jsonify
import asyncio
from rag import VectorStore, DocumentProcessor
from council import ModelCouncil
import config

# Initialize Flask App
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

from history import HistoryManager

# Initialize Flask App
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global State (Simple in-memory for single user local app)
class GlobalState:
    def __init__(self):
        self.vector_store = VectorStore()
        self.doc_loaded = False
        self.filename = None

state = GlobalState()

@app.route('/')
def index():
    return render_template('index.html', app_title=config.APP_TITLE, app_icon=config.APP_ICON)

@app.route('/api/config')
def get_config():
    return jsonify({
        "models": ModelCouncil.get_available_models(),
        "personas": config.PERSONAS
    })

@app.route('/api/models')
def get_models():
    # Deprecated, keeping for backward compat if needed, but /api/config is better
    models = ModelCouncil.get_available_models()
    return jsonify({"models": models})

@app.route('/api/active_doc')
def get_active_doc():
    return jsonify({
        "loaded": state.doc_loaded,
        "filename": state.filename
    })

@app.route('/api/history')
def get_history():
    return jsonify(HistoryManager.load_history())

@app.route('/api/upload_url', methods=['POST'])
def upload_url():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    
    try:
        text = DocumentProcessor.load_url(url)
        if text:
            count = state.vector_store.add_document(text, url)
            state.doc_loaded = True
            state.filename = url
            return jsonify({"success": True, "chunks": count, "filename": url})
        else:
            return jsonify({"error": "Could not extract text from URL"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file:
        try:
            filename = file.filename
            file_bytes = file.read() # Read into memory
            
            # Determine type and process
            ext = filename.split('.')[-1].lower()
            text = ""
            
            import io
            file_stream = io.BytesIO(file_bytes)
            
            if ext == 'pdf':
                text = DocumentProcessor.load_pdf(file_stream)
            elif ext == 'docx':
                text = DocumentProcessor.load_docx(file_stream)
            elif ext == 'txt':
                text = DocumentProcessor.load_txt(file_stream)
                
            if text:
                count = state.vector_store.add_document(text, filename)
                state.doc_loaded = True
                state.filename = filename
                return jsonify({"success": True, "chunks": count, "filename": filename})
            else:
                return jsonify({"error": "Could not extract text"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/api/clear_doc', methods=['POST'])
def clear_doc():
    state.vector_store = VectorStore()
    state.doc_loaded = False
    state.filename = None
    return jsonify({"success": True})

@app.route('/api/run_council', methods=['POST'])
def run_council():
    data = request.json
    selected_models = data.get('models', [])
    judge_model = data.get('judge')
    prompt = data.get('prompt')
    persona_mode = data.get('persona', "Padrão (Neutro)")
    
    if not selected_models or not prompt:
        return jsonify({"error": "Missing parameters"}), 400

    # 1. Retrieve Context
    context_chunks = []
    if state.doc_loaded:
        context_chunks = state.vector_store.query(prompt, n_results=4)
        
    # 2. Run Council & 3. Synthesize
    
    async def process_request():
        r = await ModelCouncil.run_council(selected_models, prompt, context_chunks, persona_mode)
        s = await ModelCouncil.synthesize_answers(judge_model, prompt, r, persona_mode)
        return r, s

    try:
        results, synthesis = asyncio.run(process_request())
        
        # Save History
        HistoryManager.save_entry(prompt, persona_mode, synthesis, [r['model'] for r in results])
        
        return jsonify({
            "results": results,
            "synthesis": synthesis,
            "context": context_chunks
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8501, host='127.0.0.1')
