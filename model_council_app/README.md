# 🧠 Conselho de Modelos Local (Local Model Council)

> **Orquestre múltiplos LLMs locais para debater, analisar e sintetizar soluções complexas.**

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Flask](https://img.shields.io/badge/Flask-Waitress-orange)
![Ollama](https://img.shields.io/badge/Ollama-Local%20AI-white)
![RAG](https://img.shields.io/badge/RAG-Local-green)

O **Conselho de Modelos Local** é uma aplicação web que permite consultar vários Modelos de Linguagem (LLMs) rodando localmente via **Ollama** de forma paralela. Diferente de um chat comum, ele introduz um "Juiz" (Sintetizador) que analisa todas as respostas e entrega um veredito consolidado, eliminando alucinações e enriquecendo a resposta final.

A aplicação foi desenhada para privacidade total (100% offline), performance em hardware consumidor (Apple Silicon/Windows ARM64/x64) e usabilidade premium.

---

## ✨ Principais Funcionalidades

### 🤖 Orquestração de Múltiplos Modelos
- Selecione livremente quais modelos instalados no seu Ollama (Llama 3, Mistral, Gemma, Phi-3, etc.) farão parte do conselho.
- Execução paralela para minimizar o tempo de espera.

### ⚖️ Sistema de Juiz e Síntese
- Um modelo dedicado atua como "Presidente do Conselho".
- Ele lê todas as opiniões individuais e gera um relatório final contendo: **Consensos**, **Divergências** e uma **Conclusão Unificada**.

### 🎭 Personas do Conselho (Novo!)
Altere a dinâmica do debate com modos predefinidos:
- **Debate (Opostos)**: Força os modelos a assumirem papéis de *Cético*, *Visionário* e *Pragmático*.
- **Consultoria**: Foco em análise técnica e estruturada.
- **Criativo**: Brainstorming sem filtros.

### 📚 RAG (Retrieval-Augmented Generation) Local
- **Docs**: Upload de PDFs, DOCX e TXT para dar contexto ao conselho.
- **Web**: Cole uma URL e o sistema lerá o conteúdo da página para embasar a discussão.
- Tudo processado na memória localmente (Embeddings via Ollama), sem envio de dados para nuvem.

### 🎨 Interface Premium
- UI moderna e responsiva (Dark Mode).
- Feedback em tempo real ("O Juiz está deliberando...").
- Histórico de sessões salvo localmente.

---

## 🛠️ Stack Tecnológica

- **Backend**: Python + Flask (transição de Streamlit para maior compatibilidade).
- **IA/LLM**: [Ollama](https://ollama.com/) (Biblioteca Python oficial).
- **Vetorização**: NumPy + Ollama Embeddings (sem dependências pesadas como ChromaDB/Torch, ideal para ARM64).
- **Frontend**: HTML5, Vanilla CSS (Inter Font), JavaScript puro.

---

## 🚀 Como Executar

### Pré-requisitos
1.  Tenha o **[Ollama](https://ollama.com/)** instalado e rodando.
2.  Baixe alguns modelos (ex: `ollama pull llama3`, `ollama pull mistral`).
3.  Python 3 instalado.

### Instalação Rápida (Windows)

Basta executar o script automático:

```powershell
.\run_council.bat
```

O script irá:
1.  Criar um ambiente virtual (`venv`).
2.  Instalar as dependências (`flask`, `requests`, `beautifulsoup4`, etc.).
3.  Iniciar o servidor e abrir seu navegador em `http://127.0.0.1:8501`.

---

## 📖 Como Usar

1.  **Selecione os Conselheiros**: Marque as caixas dos modelos que deseja consultar na barra lateral.
2.  **Escolha o Juiz**: Defina qual modelo fará a síntese final (recomendado um modelo mais capaz, como Llama 3 ou Mistral).
3.  **Defina o Contexto (Opcional)**:
    *   Faça upload de um arquivo PDF/DOCX.
    *   Ou cole uma URL para leitura.
4.  **Escolha a Persona**: Defina se quer um debate acalorado ou uma consultoria técnica.
5.  **Pergunte**: Digite seu dilema e clique em "Convocar Conselho".

---

## 📄 Licença

Este projeto é open-source sob a licença [MIT](LICENSE). Sinta-se livre para modificar e distribuir.

---

Desenvolvido com foco em **Simplicidade**, **Privacidade** e **Poder Local**.
