# save as: text_cleaner.py
import re
import unicodedata

def clean_english_text(text: str) -> str:
    """
    - Lowercase
    - Strip accents (é -> e)
    - Keep ONLY English letters a–z and digits 0–9
    - Replace everything else with a single space
    - Collapse multiple spaces
    """
    # Normalize (remove accents / non-ASCII marks)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    # Keep letters + digits; everything else -> space
    text = re.sub(r"[^a-z0-9]+", " ", text)
    # Collapse extra spaces and trim
    return re.sub(r"\s+", " ", text).strip()

if __name__ == "__main__":
    tests = [
        "Hello, WORLD!!! 123",                         # punctuation + digits
        "Café — déjà vu @#$ 2025-08-11",               # accents + symbols + date
        "Order #A-42b: 3x Apples @ $1.99",             # mixed punctuation + numbers
        "ID: ABC123xyz\t\n",                           # tabs/newlines + alnum
        "Phones: +1 (555) 123-4567",                   # phone formatting
    ]

    for i, t in enumerate(tests, 1):
        cleaned = clean_english_text(t)
        print(f"{i}. IN : {t!r}")
        print(f"   OUT: {cleaned!r}\n")

    