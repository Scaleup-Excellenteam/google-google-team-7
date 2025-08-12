# indexing.py
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import re
import pickle
from typing import Tuple, Dict, List, Set, DefaultDict, Optional

# ===== Cache file (Pickle) =====
CACHE_FILE = "index_cache.pkl"

# ===== Normalization and tokenization =====
_PUNCT = re.compile(r"[^\w\s]")   # Matches any non-word/non-space characters
_SPACE = re.compile(r"\s+")       # Matches multiple spaces

def normalize_line(s: str) -> str:
    """Lowercase, strip punctuation, normalize whitespace."""
    s = s.lower()
    s = _PUNCT.sub("", s)
    s = _SPACE.sub(" ", s).strip()
    return s

def tokenize(s: str) -> List[str]:
    """Split normalized string to words."""
    return normalize_line(s).split() if s else []

# ===== Build dictionaries (for file or directory) =====
def build_id_and_word_index(
    path: str,
    skip_empty: bool = True,
    max_bytes: int = 50_000_000
) -> Tuple[Dict[int, List], DefaultDict[str, Set[int]]]:
    """
    Build:
      id_map:    dict[int, [text, file_name, line_no, file_path]]
      word_index:defaultdict[str, set[int]] mapping word -> set of ids
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Path not found: {p}")

    id_map: Dict[int, List] = {}
    word_index: DefaultDict[str, Set[int]] = defaultdict(set)
    uid = 0

    def process_file(file_path: Path):
        nonlocal uid
        try:
            if file_path.stat().st_size > max_bytes:
                return
        except OSError:
            return

        for enc in ("utf-8", "latin-1"):
            try:
                with file_path.open("r", encoding=enc, errors="ignore") as f:
                    for line_no, raw in enumerate(f, start=1):
                        text = raw.rstrip("\r\n")
                        if skip_empty and not text.strip():
                            continue
                        id_map[uid] = [text, file_path.name, line_no, str(file_path)]
                        for w in tokenize(text):
                            if w:
                                word_index[w].add(uid)
                        uid += 1
                return
            except Exception:
                continue

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

# ===== Pickle helpers =====
def save_index_pickle(
    id_map: Dict[int, List],
    word_index: DefaultDict[str, Set[int]],
    root_path: Optional[str] = None,
    cache_file: str = CACHE_FILE
) -> None:
    """Save index dictionaries + meta to a pickle file."""
    meta = {
        "root_path": root_path,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "rows": len(id_map),
        "unique_words": len(word_index),
    }
    with open(cache_file, "wb") as f:
        pickle.dump((id_map, word_index, meta), f)
    print(f"[cache] Saved index to {cache_file}")
    print(f"[cache] meta: {meta}")

def load_index_pickle(cache_file: str = CACHE_FILE):
    """Load index dictionaries + meta from a pickle file, or (None, None, None) if missing/failed."""
    p = Path(cache_file)
    if not p.exists():
        return None, None, None
    try:
        with open(cache_file, "rb") as f:
            id_map, word_index, meta = pickle.load(f)
        print(f"[cache] Loaded index from {cache_file}")
        if meta:
            print(f"[cache] meta: {meta}")
        return id_map, word_index, meta
    except Exception as e:
        print(f"[cache] Failed to load cache ({e}).")
        return None, None, None

def load_index_pickle(cache_file: str = CACHE_FILE):
    p = Path(cache_file)
    if not p.exists():
        return None, None, None
    try:
        with open(cache_file, "rb") as f:
            id_map, word_index, meta = pickle.load(f)  # ← זה tuple, לא dict
        print(f"[cache] Loaded index from {cache_file}")
        if meta:
            print(f"[cache] meta: {meta}")
        return id_map, word_index, meta
    except Exception as e:
        print(f"[cache] Failed to load cache ({e}).")
        return None, None, None