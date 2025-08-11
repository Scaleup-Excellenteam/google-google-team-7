import string
from typing import Iterable, Tuple, List
from min_heap import FixedSizeMaxKeeper

ALPHABET = string.ascii_lowercase  # swap to Hebrew letters if needed

def all_one_edits_tuples(word: str, alphabet: str = ALPHABET) -> List[Tuple[str, int]]:
    """Return (new_word, index) for every delete/replace/insert on `word`."""
    out: List[Tuple[str, int]] = []
    n = len(word)
    # DELETE
    for i in range(n):
        out.append((word[:i] + word[i+1:], i))
    # REPLACE
    for i in range(n):
        orig = word[i]
        for c in alphabet:
            if c != orig:
                out.append((word[:i] + c + word[i+1:], i))
    # INSERT
    for i in range(n + 1):
        for c in alphabet:
            out.append((word[:i] + c + word[i:], i))
    return out

def all_one_edits_sentence_tuples(sentence: str, alphabet: str = ALPHABET) -> List[Tuple[str, int, int]]:
    """
    Return (new_sentence, word_idx, index) for every one-edit on any single word.
    - word_idx: which word changed (0-based)
    - index   : position inside the ORIGINAL word (for insert: the gap 0..len(word))
    """
    words = sentence.split()
    out: List[Tuple[str, int, int]] = []
    for wi, w in enumerate(words):
        for new_w, idx in all_one_edits_tuples(w, alphabet):
            new_words = list(words)
            new_words[wi] = new_w
            out.append((" ".join(new_words), wi, idx))
    return out


# --- helpers ---

def _count_letters_and_spaces(s: str) -> int:
    """Count letters + spaces (ignore punctuation and other symbols)."""
    return sum(1 for ch in s if (ch.isalpha() or ch == ' '))

def _penalty_for_replace(pos: int) -> int:
    if pos < 0: return 0
    if pos == 0: return 5
    if pos == 1: return 4
    if pos == 2: return 3
    if pos == 3: return 2
    return 1

def _penalty_for_add_or_delete(pos: int) -> int:
    if pos < 0: return 0
    if pos == 0: return 10
    if pos == 1: return 8
    if pos == 2: return 6
    if pos == 3: return 4
    return 2

def compute_score(typed_sentence: str, idx: int, kind: str) -> int:
    """
    typed_sentence: the user-typed variant (we score THIS string)
    idx: global index of the changed character, counting letters only (spaces ignored)
    kind: 'o' (original), 'r' (replace), 'a' (add), 'd' (delete)
    """
    base = 2 * _count_letters_and_spaces(typed_sentence)

    if kind == 'o':
        penalty = 0
    elif kind == 'r':
        penalty = _penalty_for_replace(idx)
    elif kind in ('a', 'd'):
        penalty = _penalty_for_add_or_delete(idx)
    else:
        raise ValueError(f"unknown kind '{kind}' (expected 'o','r','a','d')")

    return base - penalty

# --- main API you asked for ---

def score_matches(
    matches: Iterable[Tuple[int, int, str, str]]
) -> List[Tuple[int, int]]:
    """
    matches: iterable of (row_id, number, char, sentence)
             where:
               - row_id: int
               - number: idx (0-based across the whole sentence, spaces ignored; -1 for original)
               - char  : 'o' | 'r' | 'a' | 'd'
               - sentence: the typed text we score
    returns: list of (score, row_id)
    """
    out: List[Tuple[int, int]] = []
    for row_id, idx, kind, sent in matches:
        score = compute_score(sent, idx, kind)
        out.append((score, row_id))
    return out

def insert_list_to_heap(lst):
    pq = FixedSizeMaxKeeper(max_size=5)
    for elem in lst:
        pq.push(elem)
    return pq    



