import os, requests

MISTRAL_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_ENDPOINT = "https://api.mistral.ai/v1/chat/completions"

if not MISTRAL_KEY:
    raise RuntimeError("MISTRAL_API_KEY not set in environment")

def mistral_generate_root(comment: str) -> str:
    headers = {
        "Authorization": f"Bearer {MISTRAL_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistral-small",
        "messages": [
            {"role": "system", "content": "You are a helpful AI that returns a single concise overarching descriptive topic topic for any comment."},
            {"role": "user", "content": f"Give me a one-word or short-phrase topic label for this comment:\n\n{comment}"}
        ],
        "max_tokens": 5,
        "temperature": 0.0
    }
    res = requests.post(MISTRAL_ENDPOINT, json=payload, headers=headers)
    res.raise_for_status()
    reply = res.json()["choices"][0]["message"]["content"].strip()

    # Strip any wrapping quotes and unescape
    clean = reply.strip().strip('"').strip("'")
    clean = clean.replace("\\u0027", "'")
    return clean.split()[0]

def mistral_generate_subtopics(comment: str, max_n: int = 4) -> list[str]:
    headers = {
        "Authorization": f"Bearer {MISTRAL_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistral-small",
        "messages": [
            {"role": "system", "content": "You return subtopics in JSON array form."},
            {"role": "user", "content": f"Extract up to {max_n} short subtopics from this comment as a JSON list:\n\n{comment}"}
        ],
        "max_tokens": max_n * 10,
        "temperature": 0.0
    }
    res = requests.post(MISTRAL_ENDPOINT, json=payload, headers=headers)
    res.raise_for_status()
    text = res.json()["choices"][0]["message"]["content"].strip()

    # Try JSON parse first
    try:
        raw = requests.utils.json.loads(text)
    except Exception:
        # Fallback split
        raw = [t.strip() for t in text.strip("[]").split(",") if t]

    # Clean each entry
    out = []
    for topic in raw:
        t = topic.strip().strip('"').strip("'")
        t = t.replace("\\u0027", "'")
        if t:
            out.append(t)
        if len(out) >= max_n:
            break

    return out
