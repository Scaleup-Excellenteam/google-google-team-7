import string
from typing import List, Tuple

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

if __name__ == "__main__":
    sentence = "where are"
    edits = all_one_edits_sentence_tuples(sentence)

    # Expected counts for english letters (A=26):
    # "where" (n=5) -> 26*(2*5+1)=286
    # "are"   (n=3) -> 26*(2*3+1)=182
    # total (with duplicates) = 468
    print(f'Sentence: "{sentence}"')
    print("Total tuples:", len(edits))  # expect 468

    # Unique sentences after dedup (due to duplicates from inserts near repeated letters) -> 460
    unique_sentences = {s for (s, _, _) in edits}
    print("Unique sentences:", len(unique_sentences))  # expect 460
    print("-" * 40)

    # Print EVERYTHING
    for i, (s, wi, idx) in enumerate(edits, 1):
        print(f"{i:4d}. ({s!r}, word_idx={wi}, index={idx})")
