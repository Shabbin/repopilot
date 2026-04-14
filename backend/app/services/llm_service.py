import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "phi3"


def shorten(text: str, max_chars: int = 1200) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n... [truncated]"


def build_prompt(question: str, contexts: list[dict]) -> str:
    context_text = "\n\n".join(
        [
            f"FILE: {c['file_path']} (lines {c['start_line']}-{c['end_line']})\n{shorten(c['content'])}"
            for c in contexts
        ]
    )

    return f"""
You are an expert software engineering assistant.

Answer the user's question using ONLY the provided repository code context.

Be precise, technical, and concise.
If the answer is not clearly present in the context, say that.

Question:
{question}

Repository Code Context:
{context_text}

Answer:
""".strip()


def generate_answer(question: str, contexts: list[dict]) -> str:
    if not contexts:
        return "No relevant code found in the repository."

    prompt = build_prompt(question, contexts)

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 200,
                    "temperature": 0.2,
                },
            },
            timeout=120,
        )

        if not response.ok:
            return f"Ollama error {response.status_code}: {response.text}"

        data = response.json()
        return data.get("response", "").strip() or "Ollama returned an empty response."

    except requests.exceptions.RequestException as exc:
        return f"Ollama request failed: {exc}"