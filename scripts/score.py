import string
from typing import Iterable, Tuple, List

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

# --- example ---
if __name__ == "__main__":
    # pretend these came from find_matching_ids_with_num_char_and_sentence(...)
    demo = {
        (101, -1, 'o', "where are"),   # original typed text
        (101,  0, 'r', "xhere are"),   # replace first letter
        (101,  5, 'a', "wheree are"),  # add after 'e' in "where" (spaces ignored for idx)
        (202,  2, 'd', "whre are"),    # delete 'e' in "where"
    }
    print(score_matches(demo))
