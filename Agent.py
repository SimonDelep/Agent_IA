import json
import os
from datetime import datetime
from openai import AzureOpenAI, OpenAI
from dotenv import load_dotenv

# =========================================================
# 1. Initialisation du client AzureOpenAI
# =========================================================

load_dotenv("dev.env")

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT
    )

# =========================================================
# 2. Outils Python disponibles pour l'agent
# =========================================================

def get_current_time() -> str:
    """
    Retourne la date et l'heure actuelles.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def calculator(expression: str) -> str:
    """
    Calcule une expression arithmétique simple.
    Attention : exemple pédagogique.
    En production, il faut durcir davantage la validation.
    """
    allowed_chars = set("0123456789+-*/(). ")
    if not set(expression).issubset(allowed_chars):
        return "Erreur : expression non autorisée."

    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Erreur de calcul : {e}"


def local_knowledge_search(query: str) -> str:
    """
    Petite base de connaissances locale pour démonstration.
    """
    kb = {
    "agent": "Un agent est un système capable de percevoir, raisonner, décider et agir pour atteindre un objectif.",
    "llm": "Un LLM est un grand modèle de langage capable de comprendre et générer du texte.",
    "orchestration": "L’orchestration consiste à coordonner plusieurs composants, outils ou agents dans un flux cohérent.",
    "rag": "Le RAG combine récupération d'information et génération, afin de fournir au modèle un contexte externe pertinent."
    }

    q = query.lower()
    results = []

    for key, value in kb.items():
        if key in q:
            results.append(f"{key} : {value}")

    if not results:
        return "Aucune information pertinente trouvée dans la base locale."

    return "\n".join(results)


# =========================================================
# 3. Registre des outils appelables par le modèle
# =========================================================

TOOLS = [
    {
    "type": "function",
    "name": "get_current_time",
    "description": "Retourne la date et l'heure courantes.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False
        }
    },
    {
    "type": "function",
    "name": "calculator",
    "description": "Évalue une expression mathématique simple.",
    "parameters": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Expression arithmétique, par exemple : 25 * (4 + 2)"
            }
        },
        "required": ["expression"],
        "additionalProperties": False
        }
    },
    {
    "type": "function",
    "name": "local_knowledge_search",
    "description": "Recherche une définition dans une base de connaissances locale.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Question ou mot-clé à rechercher"
            }
        },
        "required": ["query"],
        "additionalProperties": False
        }
    }
    ]


# =========================================================
# 4. Routage des outils côté Python
# =========================================================

def call_tool(tool_name: str, arguments: dict) -> str:
    if tool_name == "get_current_time":
        return get_current_time()

    if tool_name == "calculator":
        return calculator(arguments["expression"])

    if tool_name == "local_knowledge_search":
        return local_knowledge_search(arguments["query"])

    return f"Outil inconnu : {tool_name}"


# =========================================================
# 5. Boucle principale de l'agent
# =========================================================

# Nombre maximum d'itérations outil pour éviter une boucle infinie
MAX_TOOL_ITERATIONS = 10


def run_agent(user_question: str) -> str:
    """
    Exécute un agent simple avec boucle d'appels d'outils.
    Boucle jusqu'à obtenir une réponse sans nouvel appel d'outil, ou jusqu'à MAX_TOOL_ITERATIONS.
    """
    instructions = (
        "Tu es un agent académique formel. "
        "Tu dois répondre en français, de manière claire, concise et structurée. "
        "Lorsque nécessaire, utilise les outils disponibles avant de répondre."
    )

    response = client.responses.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        instructions=instructions,
        input=user_question,
        tools=TOOLS
    )

    for _ in range(MAX_TOOL_ITERATIONS):
        function_calls = [
            item for item in response.output
            if item.type == "function_call"
        ]

        if not function_calls:
            return response.output_text

        tool_outputs = []

        for call in function_calls:
            tool_name = call.name
            arguments = json.loads(call.arguments)
            result = call_tool(tool_name, arguments)

            tool_outputs.append({
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": result
            })

        response = client.responses.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            previous_response_id=response.id,
            input=tool_outputs
        )

    # Limite atteinte : on renvoie la dernière réponse disponible
    return response.output_text or "Limite d'itérations atteinte sans réponse finale."


# =========================================================
# 6. Démonstration
# =========================================================

if __name__ == "__main__":
    questions = [
        "Calcule 25 * (4 + 2).",
        "Quelle heure est-il ?",
        "Explique ce qu'est un agent et le rôle de l'orchestration."
    ]

    for q in questions:
        print("=" * 80)
        print("QUESTION :", q)
        print()
        answer = run_agent(q)
        print("RÉPONSE :")
        print(answer)
        print()

