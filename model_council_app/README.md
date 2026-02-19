# Local Model Council 🧠

Uma aplicação web Python que implementa um "Conselho de Modelos" usando Ollama. A aplicação permite consultar múltiplos LLMs locais em paralelo e obter uma síntese consolidada, com suporte a RAG (Retrieval-Augmented Generation) para documentos.

Inspiração: [Perplexity Model Council](https://www.perplexity.ai/hub/blog/introducing-model-council)

## Funcionalidades
- **Múltiplos Modelos**: Selecione e consulte vários modelos Ollama simultaneamente.
- **RAG Local**: Upload de PDF, DOCX ou TXT para usar como contexto.
- **Síntese Inteligente**: Um modelo "Juiz" consolida as respostas, destacando consensos e divergências.
- **Execução Paralela**: Respostas rápidas usando `asyncio`.
- **Interface Amigável**: Construída com Streamlit.

## Pré-requisitos
1. **Python 3.9+** instalado.
2. **Ollama** instalado e rodando.
   - Baixe em: [ollama.com](https://ollama.com)
   - Certifique-se de ter baixado alguns modelos (ex: `ollama pull llama3`, `ollama pull mistral`, `ollama pull gemma`).

## Instalação

1. Clone o repositório ou navegue até a pasta:
   ```bash
   cd model_council_app
   ```

2. Crie um ambiente virtual (recomendado):
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Como Usar

1. Inicie a aplicação:
   ```bash
   streamlit run app.py
   ```

2. O navegador abrirá automaticamente (geralmente em `http://localhost:8501`).

3. **Na barra lateral**:
   - Verifique se os modelos foram carregados corretamente.
   - Selecione os modelos que farão parte do conselho.
   - Selecione o modelo "Juiz".
   - (Opcional) Faça upload de um documento para contexto.

4. **Na área principal**:
   - Digite sua pergunta/prompt.
   - Clique em "Convening Council".

5. Aguarde as respostas individuais e a síntese final.

## Estrutura do Projeto

- `app.py`: Interface do usuário (Streamlit).
- `council.py`: Lógica de orquestração e chamada aos modelos (Ollama).
- `rag.py`: Processamento de documentos e banco vetorial (ChromaDB + SentenceTransformers).
- `config.py`: Configurações globais.

## Troubleshooting

- **Erro de conexão Ollama**: Certifique-se de que o aplicativo Ollama está rodando em background (`ollama serve` ou via aplicativo desktop).
- **Modelos não aparecem**: Rode `ollama list` no terminal para garantir que você tem modelos baixados.
- **Erro no ChromaDB**: Se houver problemas com sqlite3, tente atualizar o pip ou instalar as build tools do C++.
