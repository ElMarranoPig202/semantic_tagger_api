import os
import sys
from typing import Optional

# Make sure our `core` package is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer, util

from core.tree_manager       import create_tree, load_tree, insert_comment, list_main_topics
from core.topic_extractor    import extract_main_topic, extract_topics
from core.mistral_integration import mistral_generate_root, mistral_generate_subtopics

# ─── App & Security Setup ──────────────────────────────────────────────────────
app = FastAPI()

MY_API_KEY = os.getenv("MY_API_KEY", "")
api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)

def require_api_key(key: str = Depends(api_key_header)):
    if key != MY_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")
    return key

# ─── Request Models ────────────────────────────────────────────────────────────
class TagRequest(BaseModel):
    comment: str
    mistral_api_key: Optional[str] = None  # will be ignored server-side

# ─── Preload Embedding Model ──────────────────────────────────────────────────
model = SentenceTransformer("all-MiniLM-L6-v2")
MAIN_THRESHOLD = 0.5

# ─── Endpoints ─────────────────────────────────────────────────────────────────
@app.post("/trees", dependencies=[Depends(require_api_key)])
def create_tree_endpoint():
    """
    Create a fresh tree and return its key.
    """
    key = create_tree()
    return {"tree_key": key}


@app.post(
    "/trees/{tree_key}/tag",
    dependencies=[Depends(require_api_key)],
    response_model=dict
)
def tag_comment_endpoint(
    tree_key: str,
    payload: TagRequest = Body(...)
):
    """
    Tag a comment under `tree_key`. Returns the main topic and subtopic paths.
    """
    # 1) Extract the raw comment text
    comment = payload.comment

    # 2) Drop any user-supplied mistral_api_key
    payload.mistral_api_key = None

    # 3) Generate or fetch main topic
    main = extract_main_topic(
        comment,
        tree_key,
        threshold=MAIN_THRESHOLD,
        root_generator=mistral_generate_root
    )

    # 4) Get noun-based subtopics
    noun_topics = extract_topics(comment)

    # 5) Ask Mistral for additional subtopics
    mistral_topics = mistral_generate_subtopics(comment)

    # 6) Combine into “paths”
    paths: list[list[str]] = []
    if noun_topics:
        paths.append(noun_topics)
    if mistral_topics:
        paths.append(mistral_topics)

    # 7) Insert into the JSON tree
    try:
        insert_comment(tree_key, main, paths, comment)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Tree key not found")

    # 8) Return the tagging result
    return {"tree_key": tree_key, "main": main, "paths": paths}


@app.get("/trees/{tree_key}", dependencies=[Depends(require_api_key)])
def get_tree_endpoint(tree_key: str):
    """
    Fetch the full JSON tree for a given key.
    """
    try:
        tree = load_tree(tree_key)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Tree not found")
    return {"tree_key": tree_key, "tree": tree}


@app.get("/trees/{tree_key}/topics", dependencies=[Depends(require_api_key)])
def list_topics_endpoint(tree_key: str):
    """
    List only the top-level (main) topics in this tree.
    """
    try:
        topics = list_main_topics(tree_key)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Tree not found")
    return {"tree_key": tree_key, "main_topics": topics}
