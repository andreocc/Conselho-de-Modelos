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
        self.full_text = None

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
        text = DocumentProcessor.load_url(url)
        if text:
            # Store full text fallback
            state.full_text = text
            state.filename = url
            state.doc_loaded = True # Assume loaded even if embeddings fail, so we can use fallback
            
            count = state.vector_store.add_document(text, url)
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
                # Store full text fallback
                state.full_text = text
                state.filename = filename
                state.doc_loaded = True # Assume loaded even if embeddings fail
                
                count = state.vector_store.add_document(text, filename)
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
        # Try vector search first
        context_chunks = state.vector_store.query(prompt, n_results=4)
        
        # Fallback: If no chunks found (e.g. no embedding model) but we have text, use full text
        if not context_chunks and state.full_text:
            print("Using full text fallback for context.")
            # Limit text length to avoid context window overflow (e.g. 50k chars is usually safe for modern models)
            # This is a simple safety cap.
            safe_text = state.full_text[:50000]
            if len(state.full_text) > 50000:
                safe_text += "\n...(truncated)..."
            context_chunks = [safe_text]
        
    # 2. Run Council & 3. Synthesize via Streaming
    import queue
    import threading
    import json
    from flask import Response

    def generate():
        q = queue.Queue()
        
        def worker():
            async def async_process():
                results = []
                try:
                    # Stream Model Execution
                    async for event in ModelCouncil.run_council(selected_models, prompt, context_chunks, persona_mode):
                        q.put(json.dumps(event))
                        if event['type'] == 'model_done':
                            results.append(event['result'])
                    
                    # Stream Synthesis
                    q.put(json.dumps({"type": "synthesis_start"}))
                    
                    # Filter out failed results for synthesis
                    valid_results = [r for r in results if r['status'] == 'Success']
                    
                    synthesis = await ModelCouncil.synthesize_answers(judge_model, prompt, valid_results, persona_mode)
                    q.put(json.dumps({"type": "synthesis_done", "result": synthesis}))
                    
                    # Save History
                    # We save the history here, but we don't return it in the stream necessarily, 
                    # or we can send a "complete" event.
                    # The UI reloads history separately anyway.
                    HistoryManager.save_entry(prompt, persona_mode, synthesis, [r['model'] for r in valid_results])
                    
                    # Send context separately if needed by UI
                    q.put(json.dumps({"type": "context", "data": context_chunks}))

                except Exception as e:
                    q.put(json.dumps({"type": "error", "error": str(e)}))
                finally:
                    q.put(None) # Sentinel

            asyncio.run(async_process())

        # Start the background worker
        threading.Thread(target=worker).start()

        # Yield from queue
        while True:
            item = q.get()
            if item is None:
                break
            yield f"data: {item}\n\n"

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, port=8501, host='127.0.0.1')
