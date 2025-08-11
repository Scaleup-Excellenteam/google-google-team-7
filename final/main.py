# main.py
from __future__ import annotations
from typing import Tuple, Dict, List
from scoring import top5_for_query
import pickle
from pathlib import Path

CACHE_FILE = "index_cache.pkl"

def load_cache() -> Tuple[Dict[int, list], Dict[str, set], dict]:
    p = Path(CACHE_FILE)
    if not p.exists():
        raise FileNotFoundError(
            f"{CACHE_FILE} לא נמצא. יש להריץ קודם indexing.py כדי לבנות ולשמור את האינדקס."
        )
    with open(CACHE_FILE, "rb") as f:
        id_map, word_index, meta = pickle.load(f)
    return id_map, word_index, meta

def main() -> None:
    # 1) טען את האינדקס מהמטמון
    id_map, word_index, meta = load_cache()
    print("[cache] loaded:", meta)

    # 2) לולאה אינטראקטיבית של שרשור קלט
    cumulative: str = ""
    print("\n=== Interactive scoring search ===")
    print("הקלד טקסט חיפוש. הקלד '#' ליציאה.\n")

    while True:
        prompt = "קלט: " if not cumulative else f"קלט נוכחי: [{cumulative}] | הוסף: "
        try:
            user = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nיציאה.")
            break

        if user == "#":
            print("ביי 👋")
            break

        if user:
            cumulative = (cumulative + " " + user).strip() if cumulative else user
        else:
            if not cumulative:
                print("לא הוזן קלט.\n")
                continue

        # 3) הפעל ניקוד והחזר Top-5
        top5 = top5_for_query(cumulative, id_map, word_index, k=5)

        if not top5:
            print("\n(אין תוצאות מתאימות לשאילתה הנוכחית)\n")
            continue

        # 4) הדפסה
        print("\n== Top 5 ==")
        for rank, (score, rid, corpus_sentence, meta) in enumerate(top5, start=1):
            kind = {"o":"original","r":"replace","a":"add","d":"delete"}.get(meta["kind"], meta["kind"])
            wi = meta["word_idx"]
            idx = meta["index_in_word"]
            info = id_map[rid]  # [text, file_name, line_no, file_path]
            file_name, line_no, file_path = info[1], info[2], info[3]
            print(f"{rank}. score={score} | rid={rid} | kind={kind} | word_idx={wi} | index_in_word={idx}")
            print(f"   {corpus_sentence}")
            print(f"   [{file_name}:{line_no}] {file_path}\n")

        # הלולאה ממשיכה; המשתמש מוסיף קלט נוסף או '#'

if __name__ == "__main__":
    main()
