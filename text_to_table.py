from pathlib import Path
import pandas as pd
import re
from collections import defaultdict

def normalize_text(s: str) -> str:
    """הופך לאותיות קטנות, מסיר פיסוק ותווים מיוחדים, מכווץ רווחים."""
    s = s.lower()
    s = re.sub(r"[♦◆◇]", "", s)  
    s = re.sub(r"[^\w\s]", "", s)  
    s = re.sub(r"\s+", " ", s).strip()
    return s

def query_to_trigram_intersection(trigram_index: dict[str, set[int]], prompt: str = "Enter words to search for: ") -> tuple[set[int], list[str]]:
    """
    קוראת מחרוזת חיפוש מהמשתמש, מנרמלת, מחלקת לטריגרמות ומבצעת חיתוך על האינדקס.
    מחזירה (ids, trigrams). אם אין טריגרמות (שאילתא קצרה מדי) תחזיר (set(), []).
    """
    search = input(prompt).strip().lower()
    q = re.sub(r"[^\w\s]", "", search)
    q = re.sub(r"\s+", " ", q).strip()

    if len(q) < 3:
        print("The search is too short (less than 3 characters) — no trigrams.\n")
        return set(), []

    trigrams = [q[i:i+3] for i in range(len(q) - 2)]
    print("trigrams:", trigrams)

    # חיתוך בין הקבוצות
    ids = trigram_index.get(trigrams[0], set()).copy()
    for tri in trigrams[1:]:
        ids &= trigram_index.get(tri, set())
        if not ids:
            break

    return ids, trigrams

def build_table_and_trigram_index_from_file(file_path: str, skip_empty: bool = True, max_bytes: int = 50_000_000):
    """סורק קובץ יחיד ובונה טבלה ואינדקס טריגרמות."""
    rows, uid = [], 0
    trigram_index = defaultdict(set)
    p = Path(file_path)
    if not p.exists() or not p.is_file():
        raise FileNotFoundError(f"File not found: {p}")
    try:
        if p.stat().st_size > max_bytes:
            raise OSError("File too large")
    except OSError:
        print(f"[WARN] skipping large file: {p}")
        return pd.DataFrame(columns=["id","file_name","file_path","line_no","text"]), trigram_index

    read_ok = False
    for enc in ("utf-8", "latin-1"):
        try:
            with p.open("r", encoding=enc, errors="ignore") as f:
                for line_no, line in enumerate(f, start=1):
                    text = line.rstrip("\r\n")
                    if skip_empty and not text.strip():
                        continue
                    rows.append({
                        "id": uid,
                        "file_name": p.name,
                        "file_path": str(p.resolve()),
                        "line_no": line_no,
                        "text": text
                    })
                    norm = normalize_text(text)
                    if len(norm) >= 3:
                        for i in range(len(norm) - 2):
                            trigram_index[norm[i:i+3]].add(uid)
                    uid += 1
            read_ok = True
            break
        except Exception:
            continue
    if not read_ok:
        print(f"[WARN] couldn't read file: {p}")

    df = pd.DataFrame(rows, columns=["id","file_name","file_path","line_no","text"])
    return df, trigram_index

def build_corpus_and_trigram_index_from_dir(root_dir: str, skip_empty: bool = True, max_bytes: int = 50_000_000):
    rows = []
    uid = 0
    trigram_index = defaultdict(set)  # טריגרמה -> סט של ids
    root = Path(root_dir)

    for file_path in root.rglob("*"):
        if not file_path.is_file():
            continue

        try:
            if file_path.stat().st_size > max_bytes:
                continue
        except OSError:
            continue

        opened = False
        for enc in ("utf-8", "latin-1"):
            try:
                with file_path.open("r", encoding=enc, errors="ignore") as f:
                    for line_no, line in enumerate(f, start=1):
                        text = line.rstrip("\r\n")
                        if skip_empty and not text.strip():
                            continue
                        # הוספת השורה לטבלה
                        rows.append({
                            "id": uid,
                            "file_name": file_path.name,
                            "file_path": str(file_path),
                            "line_no": line_no,
                            "text": text
                        })
                        # נרמול והוספת טריגרמות
                        norm = normalize_text(text)
                        if len(norm) >= 3:
                            for i in range(len(norm) - 3 + 1):
                                trigram = norm[i:i+3]
                                trigram_index[trigram].add(uid)
                        uid += 1
                opened = True
                break
            except Exception:
                continue

        if not opened:
            print(f"[WARN] לא הצלחתי לקרוא את הקובץ: {file_path}")

    df = pd.DataFrame(rows, columns=["id", "file_name", "file_path", "line_no", "text"])
    return df, trigram_index

def main():
    # קלט נתיב (אפשר להדביק עם מרכאות)
    raw_path = input("Enter a path to a file or folder: ").strip()
    path_str = raw_path.strip().strip('"').strip("'")
    p = Path(path_str)

    # בניית הטבלה + אינדקס
    if p.is_dir():
        df, trigram_index = build_corpus_and_trigram_index_from_dir(str(p))
    elif p.is_file():
        df, trigram_index = build_table_and_trigram_index_from_file(str(p))
    else:
        print(f"Path not found: {path_str}")
        return

    print("Rows in the table:", len(df), "\n")
    print("Different trigrams:", len(trigram_index), "\n")
    if not df.empty:
        print(df.head())

    # קלט חיפוש
    ids, _tris = query_to_trigram_intersection(trigram_index)

    if ids:
        print(f"{len(ids)} matches found (showing up to 20):\n")
        subset = df[df["id"].isin(list(ids)[:20])][["id", "file_name", "line_no", "text"]]
        print(subset.to_string(index=False))
    else:
        print("No results found (no intersection between all trigrams).")

if __name__ == "__main__":
    main()
