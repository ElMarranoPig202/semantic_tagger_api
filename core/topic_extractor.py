import nltk
from nltk import word_tokenize, pos_tag
from sentence_transformers import SentenceTransformer, util
from core.tree_manager import list_main_topics

# Download NLTK resources
nltk.download("punkt")
nltk.download("punkt_tab")
nltk.download("averaged_perceptron_tagger")
nltk.download("averaged_perceptron_tagger_eng") 

_model = SentenceTransformer("all-MiniLM-L6-v2")

def extract_main_topic(comment: str, tree_key: str, threshold: float = 0.5, root_generator=None) -> str:
    roots = list_main_topics(tree_key)
    if roots:
        c_emb = _model.encode(comment)
        root_embs = _model.encode(roots)
        sims = util.cos_sim(c_emb, root_embs)[0]
        idx = sims.argmax().item()
        score = sims[idx].item()
        if score >= threshold:
            return roots[idx]

    if root_generator:
        return root_generator(comment)

    # fallback: first noun or 'general'
    tokens = word_tokenize(comment.lower())
    nouns = [w for w, t in pos_tag(tokens) if t.startswith("NN") and len(w) > 2]
    return nouns[0] if nouns else "general"

def extract_topics(comment: str, max_n=4) -> list[str]:
    tokens = word_tokenize(comment.lower())
    nouns = [w for w, t in pos_tag(tokens) if t.startswith("NN") and len(w) > 2]
    seen = set()
    out = []
    for n in nouns:
        if n not in seen:
            seen.add(n)
            out.append(n)
        if len(out) == max_n:
            break
    return out or ["general"]
