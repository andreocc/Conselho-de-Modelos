import os

# App Config
APP_TITLE = "Conselho de Modelos 🧠"
APP_ICON = "⚖️"

# RAG Config
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
EMBEDDING_MODEL = 'all-minilm' # Lightweight model for ollama
VECTOR_DB_PATH = os.path.join(os.getcwd(), "chroma_db")

# Ollama Config
DEFAULT_TIMEOUT = 120  # seconds
DEFAULT_TEMPERATURE = 0.7

# Personas / Modes
PERSONAS = {
    "Padrão (Neutro)": {
        "description": "Assistentes úteis e diretos.",
        "system_prompt": "Você é um assistente útil e objetivo."
    },
    "Debate (Opostos)": {
        "description": "Modelos assumem posições distintas para gerar debate.",
        "roles": [
            "O Cético: Você deve questionar premissas, apontar riscos e falhas na ideia.",
            "O Visionário: Você deve focar no potencial futuro, inovação e ideias ousadas.",
            "O Pragmático: Você deve focar na viabilidade técnica, custos e execução realista.",
            "O Historiador: Você deve buscar paralelos históricos e lições do passado."
        ]
    },
    "Consultoria (Especialistas)": {
        "description": "Foco em análise profissional e técnica.",
        "system_prompt": "Você é um consultor sênior de alto nível. Sua resposta deve ser técnica, estruturada e focada em gerar valor de negócio."
    },
    "Criativo (Brainstorm)": {
        "description": "Foco em ideias fora da caixa.",
        "system_prompt": "Você é um especialista em criatividade. Gere ideias não convencionais, metaforas e abordagens laterais. Não se preocupe com restrições agora."
    }
}

# Prompt Templates
SYNTHESIS_PROMPT_TEMPLATE = """
Você atua como o Presidente do Conselho de Inteligência Artificial.
Sua missão é analisar as respostas fornecidas por outros modelos (os Conselheiros) e entregar um veredito final de alta qualidade ao usuário.

Modo do Conselho: {council_mode}
Contexto da Solicitação: {user_prompt}

Delebrações dos Conselheiros:
{model_responses}

Instruções para o Veredito:
1. **Consenso**: Identifique os pontos onde os conselheiros concordam plenamente.
2. **Divergências e Nuances**: Destaque contradições ou abordagens diferentes entre os modelos.
3. **Insights Exclusivos**: Aponte informações valiosas que apenas um modelo forneceu.
4. **Conclusão Unificada**: Elabore uma resposta final completa, precisa e bem estruturada, combinando o melhor de todas as visões. Evite mencionar "o modelo X disse isso", foque na resposta em si, a menos que a atribuição seja crucial para explicar uma divergência.

Gere a resposta em Markdown profissional, utilizando formatação clara (negrito, listas, títulos).
"""
