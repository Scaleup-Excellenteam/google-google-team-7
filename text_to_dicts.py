from pathlib import Path
from collections import defaultdict
import re
import pickle
from datetime import datetime

# ===== Cache file (Pickle) =====
CACHE_FILE = "index_cache.pkl"

# ===== Normalization and tokenization =====
_PUNCT = re.compile(r"[^\w\s]")   # Matches any non-word/non-space characters
_SPACE = re.compile(r"\s+")       # Matches multiple spaces

def normalize_line(s: str) -> str:
    # Convert to lowercase, remove punctuation, and normalize spaces
    s = s.lower()
    s = _PUNCT.sub("", s)
    s = _SPACE.sub(" ", s).strip()
    return s

def tokenize(s: str) -> list[str]:
    # Split the normalized string into words
    return normalize_line(s).split() if s else []

# ===== Build dictionaries (for file or directory) =====
def build_id_and_word_index(path: str, skip_empty: bool = True, max_bytes: int = 50_000_000):
    """
    Returns:
      id_map: dict[int, list[text, file_name, line_no, file_path]]
      word_index: dict[str, set[int]]
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Path not found: {p}")

    id_map: dict[int, list] = {}                                # Maps id -> [text, file_name, line_no, file_path]
    word_index: defaultdict[str, set[int]] = defaultdict(set)   # Maps word -> set of ids
    uid = 0

    def process_file(file_path: Path):
        nonlocal uid
        # Skip files larger than max_bytes
        try:
            if file_path.stat().st_size > max_bytes:
                return
        except OSError:
            return
        # Try reading with UTF-8, fallback to Latin-1
        for enc in ("utf-8", "latin-1"):
            try:
                with file_path.open("r", encoding=enc, errors="ignore") as f:
                    for line_no, raw in enumerate(f, start=1):
                        text = raw.rstrip("\r\n")
                        if skip_empty and not text.strip():
                            continue
                        # Store in id_map
                        id_map[uid] = [text, file_path.name, line_no, str(file_path)]
                        # Update word_index for each token
                        for w in tokenize(text):
                            if w:
                                word_index[w].add(uid)
                        uid += 1
                return
            except Exception:
                continue
        # If reading fails completely
        print(f"[WARN] couldn't read file: {file_path}")

    if p.is_file():
        process_file(p)
    elif p.is_dir():
        for fp in p.rglob("*"):
            if fp.is_file():
                process_file(fp)
    else:
        raise ValueError(f"Not file/dir: {p}")

    return id_map, word_index

# ===== Search: Intersection of IDs for all words =====
def search_all_words_ids(query: str, word_index: dict[str, set[int]]) -> set[int]:
    """
    Takes a query string, returns the set of IDs where all words appear.
    """
    words = tokenize(query)
    if not words:
        return set()
    # If any word doesn't exist in the index -> no results
    if any(w not in word_index for w in words):
        return set()
    # Start with the rarest word to reduce intersection size early
    words_sorted = sorted(words, key=lambda w: len(word_index[w]))
    ids = set(word_index[words_sorted[0]])
    for w in words_sorted[1:]:
        ids &= word_index[w]
        if not ids:
            break
    return ids

# ===== Print results based on id_map =====
def print_results(ids: set[int], id_map: dict[int, list], limit: int = 20):
    if not ids:
        print("No results found.")
        return
    print(f"{len(ids)} rows found (showing up to {limit}):\n")
    for rid in list(ids)[:limit]:
        text, file_name, line_no, file_path = id_map[rid]
        print(f"The sentence: {text}\n File name: {file_name}\n Line number: {line_no}\n path: ({file_path})\n")

# ===== Persistent interactive refinement loop (prints top 5 each step) =====
def run_interactive_query_refinement(id_map: dict[int, list], word_index: dict[str, set[int]]):
    """
    לולאת חיפוש מצטברת:
    - בכל צעד מדפיסה עד 5 תוצאות לשאילתה המצטברת.
    - מקבלת תוספת מילים שתתווסף לשאילתה הקודמת.
    - פקודות: /new או /clear לאיפוס. # לסיום.
    """
    current_query = ""
    print("\nIncremental search mode. Type words to search for. Type '#' to end, '/new' to reset.\n")

    while True:
        try:
            prompt = "Search words" if not current_query else f"Current query: [{current_query}] | Add words"
            user = input(f"{prompt}: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExit.")
            break

        if user == "#":
            print("End search.")
            break
        if user in ("/new", "/clear"):
            current_query = ""
            print("The query has been reset.\n")
            continue
        if user == "":
            # להציג שוב תוצאות לפי השאילתה הנוכחית (אם קיימת)
            if not current_query:
                print("No query has been entered yet.\n")
                continue
        else:
            # לשרשר את הקלט החדש לשאילתה הקיימת
            current_query = (current_query + " " + user).strip() if current_query else user

        # חיפוש לפי השאילתה המצטברת
        ids = search_all_words_ids(current_query, word_index)
        if not ids:
            print("There are no results for the current query.\n")
            continue

        # הצגת עד 5 תוצאות
        print(f"\n{len(ids)} rows found (showing up to 5):\n")
        for rid in list(ids)[:5]:
            text, file_name, line_no, file_path = id_map[rid]
            print(f"Sentence: {text}\nFile name: {file_name}\nLine number: {line_no}\nPath: {file_path}\n")

# ===== Pickle helpers =====
def save_index_pickle(id_map, word_index, root_path: str | None):
    meta = {
        "root_path": root_path,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "rows": len(id_map),
        "unique_words": len(word_index),
    }
    with open(CACHE_FILE, "wb") as f:
        pickle.dump((id_map, word_index, meta), f)
    print(f"\n[cache] Saved index to {CACHE_FILE}")
    print(f"[cache] meta: {meta}")

def load_index_pickle():
    p = Path(CACHE_FILE)
    if not p.exists():
        return None, None, None
    try:
        with open(CACHE_FILE, "rb") as f:
            id_map, word_index, meta = pickle.load(f)
        print(f"[cache] Loaded index from {CACHE_FILE}")
        if meta:
            print(f"[cache] meta: {meta}")
        return id_map, word_index, meta
    except Exception as e:
        print(f"[cache] Failed to load cache ({e}).")
        return None, None, None

# ===== Example interactive run =====
if __name__ == "__main__":
    # 1) נסה לטעון מהמטמון
    id_map, word_index, meta = load_index_pickle()

    # 2) אם אין מטמון — בנה ושמור
    if id_map is None or word_index is None:
        raw_path = input("Paste a path to a file or folder: ").strip()
        path = raw_path.strip().strip('"').strip("'")
        id_map, word_index = build_id_and_word_index(path, skip_empty=True)
        print("Indexed rows:", len(id_map), '\n')
        print("Unique words in index:", len(word_index), '\n')
        save_index_pickle(id_map, word_index, root_path=path)
    else:
        print("\n[cache] Using cached index.")
        print("Indexed rows:", len(id_map), '\n')
        print("Unique words in index:", len(word_index), '\n')

    # 3) מצב חיפוש מצטבר עם שרשור שאילתות
    run_interactive_query_refinement(id_map, word_index)
