def find_matching_ids_with_num_char_and_sentence(sentences_with_num_and_char, word_to_ids, id_to_list):
    def contains_sublist(lst, sublst):
        for i in range(len(lst) - len(sublst) + 1):
            if lst[i:i+len(sublst)] == sublst:
                return True
        return False

    matching = set()

    for sentence, number, char in sentences_with_num_and_char:
        words = sentence.split()

        if not all(word in word_to_ids for word in words):
            continue

        intersection = set.intersection(*(word_to_ids[word] for word in words))

        for row_id in intersection:
            if row_id in id_to_list and len(id_to_list[row_id]) > 0:
                reference_sentence = id_to_list[row_id][0]
                reference_words = reference_sentence.split()

                if contains_sublist(reference_words, words):
                    matching.add((row_id, number, char, sentence))

    return matching


# ====== בדיקת הכל כלול ======

# ====== טסט נוסף - בדיקת רצף מדויק וחוסר רצף ======

sentences_with_num_and_char = [
    ("quick brown fox", 10, 'X'),   # רצף מדויק
    ("brown quick fox", 11, 'Y'),   # אותן מילים, סדר שונה - לא מתאים
    ("quick fox", 12, 'Z'),         # תת-רצף, לא רצף מלא של המילים
]

word_to_ids = {
    "quick": {100, 101},
    "brown": {100, 101},
    "fox": {100, 101},
}

id_to_list = {
    100: ["the quick hhh brown fox jumps"],
    101: ["the brown quick fox jumps"],
}

results = find_matching_ids_with_num_char_and_sentence(
    sentences_with_num_and_char,
    word_to_ids,
    id_to_list
)


# הרצה
results = find_matching_ids_with_num_char_and_sentence(
    sentences_with_num_and_char,
    word_to_ids,
    id_to_list
)


for r in sorted(results):
    print(r)

