import os, json, uuid, re

# turn “Sweden’s Internet” → “swedens_internet”
def normalize_label(label: str) -> str:
    s = label.lower().strip()
    # replace non-alnum with underscore
    s = re.sub(r"[^a-z0-9]+", "_", s)
    # collapse multiple underscores
    s = re.sub(r"_+", "_", s)
    return s.strip("_")

# Base directory for storing each tree’s JSON
BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "trees")
os.makedirs(BASE_DIR, exist_ok=True)

def _path(tree_key: str) -> str:
    return os.path.join(BASE_DIR, f"{tree_key}.json")

def create_tree() -> str:
    """
    Generate a new UUID key and initialize an empty tree file.
    """
    key = uuid.uuid4().hex
    save_tree(key, {})
    return key

def load_tree(tree_key: str) -> dict:
    """
    Load and return the JSON tree for this key.
    Raises FileNotFoundError if missing.
    """
    p = _path(tree_key)
    if not os.path.exists(p):
        raise FileNotFoundError(f"Tree {tree_key} not found")
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def save_tree(tree_key: str, tree: dict):
    """
    Overwrite the JSON file for this key.
    """
    with open(_path(tree_key), "w", encoding="utf-8") as f:
        json.dump(tree, f, indent=2)

def insert_comment(tree_key: str, main: str, paths: list[list[str]], comment: str) -> dict:
    tree = load_tree(tree_key)

    # normalize the main topic key
    main_norm = normalize_label(main)
    if main_norm not in tree:
        tree[main_norm] = {"__label": main, "__children": {}}

    node = tree[main_norm]["__children"]

    for path in paths:
        for raw_tag in path:
            tag = normalize_label(raw_tag)
            if tag not in node:
                node[tag] = {"__label": raw_tag, "__children": {}}
            node = node[tag]["__children"]

        # we’re at the leaf – comments list
        comments = node.setdefault("comments", [])
        if comment not in comments:
            comments.append(comment)

        # reset for next path
        node = tree[main_norm]["__children"]

    save_tree(tree_key, tree)
    return tree

def list_main_topics(tree_key: str) -> list[str]:
    """
    Return the list of top-level (main) topic labels in a given tree.
    """
    tree = load_tree(tree_key)
    # Each key is the normalized slug; __label holds the human text
    topics = []
    for slug, data in tree.items():
        label = data.get("__label") or slug
        topics.append(label)
    return topics
