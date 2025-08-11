# search.py
from __future__ import annotations
import re
from typing import Dict, List, Set

# ===== Normalization and tokenization =====
_PUNCT = re.compile(r"[^\w\s]")   # non-word/non-space
_SPACE = re.compile(r"\s+")       # multi spaces

def normalize_line(s: str) -> str:
    s = s.lower()
    s = _PUNCT.sub("", s)
    s = _SPACE.sub(" ", s).strip()
    return s

def tokenize(s: str) -> List[str]:
    return normalize_line(s).split() if s else []

# ===== Search: intersection of IDs for all words =====
def search_all_words_ids(query: str, word_index: Dict[str, Set[int]]) -> Set[int]:
    """
    Takes a query string, returns the set of IDs where all words appear.
    Strategy: start intersecting from the rarest word to shrink early.
    """
    words = tokenize(query)
    if not words:
        return set()
    if any(w not in word_index for w in words):
        return set()
    words_sorted = sorted(words, key=lambda w: len(word_index[w]))
    ids = set(word_index[words_sorted[0]])
    for w in words_sorted[1:]:
        ids &= word_index[w]
        if not ids:
            break
    return ids

# ===== Pretty print results =====
def print_results(ids: Set[int], id_map: Dict[int, list], limit: int = 20) -> None:
    if not ids:
        print("No results found.")
        return
    print(f"{len(ids)} rows found (showing up to {limit}):\n")
    for rid in list(ids)[:limit]:
        text, file_name, line_no, file_path = id_map[rid]
        print(f"The sentence: {text}\n File name: {file_name}\n Line number: {line_no}\n path: ({file_path})\n")

# ===== Incremental interactive CLI =====
def run_interactive_query_refinement(id_map: Dict[int, list], word_index: Dict[str, Set[int]]) -> None:
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
            if not current_query:
                print("No query has been entered yet.\n")
                continue
        else:
            current_query = (current_query + " " + user).strip() if current_query else user

        ids = search_all_words_ids(current_query, word_index)
        if not ids:
            print("There are no results for the current query.\n")
            continue

        print(f"\n{len(ids)} rows found (showing up to 5):\n")
        for rid in list(ids)[:5]:
            text, file_name, line_no, file_path = id_map[rid]
            print(f"Sentence: {text}\nFile name: {file_name}\nLine number: {line_no}\nPath: {file_path}\n")
    