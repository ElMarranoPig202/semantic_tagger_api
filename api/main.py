import os, sys

# optional hack to ensure project‐root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI, HTTPException, Body
from sentence_transformers import SentenceTransformer, util

# your core logic
from core.tree_manager        import create_tree, load_tree, insert_comment, list_main_topics
from core.topic_extractor     import extract_main_topic, extract_topics
from core.mistral_integration import mistral_generate_root, mistral_generate_subtopics

app = FastAPI()

# Preload the embedding model once
model = SentenceTransformer("all-MiniLM-L6-v2")
MAIN_THRESHOLD = 0.5


@app.post("/trees")
def create_tree_endpoint():
    key = create_tree()
    return {"tree_key": key}


@app.post("/trees/{tree_key}/tag")
def tag_comment_endpoint(tree_key: str, comment: str = Body(..., embed=True)):
    # 1) Get or generate main topic via Mistral
    main = extract_main_topic(
        comment,
        tree_key,
        threshold=MAIN_THRESHOLD,
        root_generator=mistral_generate_root
    )

    # 2) Extract noun‐based subtopics
    noun_topics = extract_topics(comment)

    # 3) Ask Mistral for subtopics
    mistral_topics = mistral_generate_subtopics(comment)

    # 4) Build the “paths” list
    paths = []
    if noun_topics:
        paths.append(noun_topics)
    if mistral_topics:
        paths.append(mistral_topics)

    # 5) Insert into JSON tree file
    try:
        insert_comment(tree_key, main, paths, comment)
    except FileNotFoundError:
        raise HTTPException(404, "Tree key not found")

    return {"tree_key": tree_key, "main": main, "paths": paths}


@app.get("/trees/{tree_key}")
def get_tree_endpoint(tree_key: str):
    try:
        tree = load_tree(tree_key)
    except FileNotFoundError:
        raise HTTPException(404, "Tree not found")
    return {"tree_key": tree_key, "tree": tree}
