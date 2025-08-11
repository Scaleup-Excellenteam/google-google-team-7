# main.py
from __future__ import annotations
from pathlib import Path
from indexing import (
    build_id_and_word_index, save_index_pickle, load_index_pickle,
    CACHE_FILE, normalize_line
)
# אם הפונקציות באמת ב-scoring, השאירי כך; אחרת ייבאי מהמקום הנכון
from scoring import (
    all_one_edits_sentence_tuples, all_one_edits_tuples,
    find_matching_ids_with_num_char_and_sentence,
    score_matches, insert_list_to_heap
)

def prompt_for_path() -> str:
    raw_path = input("Paste path to file or folder for indexing: ").strip()
    return raw_path.strip('"').strip("'")

def compute(user_input: str) -> None:
    # 1) בניית אינדקס ושמירה
    path = prompt_for_path()
    if not path:
        print("No path entered. Exit.")
        return

    p = Path(path)
    if not p.exists():
        print(f"Error: Path does not exist: {p}")
        return

    skip_empty = True
    max_bytes = 50_000_000  # 50MB

    print(f"\n[build] starting index of: {p.resolve()}")
    id_map, word_index = build_id_and_word_index(str(p), skip_empty=skip_empty, max_bytes=max_bytes)
    print(f"[build] Completed. Indexed rows: {len(id_map)} | Unique words: {len(word_index)}")

    save_index_pickle(id_map, word_index, root_path=str(p.resolve()), cache_file=CACHE_FILE)
    print("[done] The index has been saved. You can continue with the scoring stages.")

    # 2) טען מהמטמון (או השתמש ישירות ב-id_map/word_index שיצרת)
    id_map, word_index, meta = load_index_pickle(CACHE_FILE)
    if id_map is None or word_index is None:
        print("Cache loading failed.")
        return

    # 3) נרמול קלט
    normalized = normalize_line(user_input)

    # 4) יצירת וריאציות והמרה לפורמט שה-matcher צריך: (sentence, number, char)
    if " " in normalized:
        # all_one_edits_sentence_tuples -> (new_sentence, word_idx, index)
        raw = all_one_edits_sentence_tuples(normalized)
        sentences_with_num_and_char = [(s, idx, 'r') for (s, _wi, idx) in raw]
    else:
        # all_one_edits_tuples -> (new_word, index)
        raw = all_one_edits_tuples(normalized)
        sentences_with_num_and_char = [(w, idx, 'r') for (w, idx) in raw]

    # 5) מציאת התאמות (שימי לב לסדר הפרמטרים!)
    # word_to_ids = word_index, id_to_list = id_map
    matches = find_matching_ids_with_num_char_and_sentence(
        sentences_with_num_and_char,
        word_index,  # נכון: word_to_ids
        id_map       # נכון: id_to_list
    )

    if not matches:
        print("No matches found.")
        return

    # 6) ניקוד
    scored_matches = score_matches(matches)  # [(score, row_id), ...]
    if not scored_matches:
        print("There's nothing to point out.")
        return

    # 7) Top-5
    pq = insert_list_to_heap(scored_matches)  # ← להעביר את הנתונים, לא את הפונקציה
    top5 = sorted(pq.get_items(), reverse=True)  # גבוה -> נמוך

    print("\n== Top 5 ==")
    for rank, (score, rid) in enumerate(top5, start=1):
        text, file_name, line_no, file_path = id_map[rid]
        print(f"{rank}. score={score} | rid={rid}")
        print(f"   {text}")
        print(f"   [{file_name}:{line_no}] {file_path}\n")

if __name__ == "__main__":
    compute('be a')
