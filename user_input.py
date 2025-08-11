def find_matching_ids_with_num_char_and_sentence(sentences_with_num_and_char, word_to_ids, id_to_list):
    """
    sentences_with_num_and_char: [(str, int, any)] - list of tuples (sentence, number, char)
    word_to_ids: dict[str, set[int]] - dictionary mapping word to a set of row IDs
    id_to_list: dict[int, list] - dictionary mapping row ID to a list where the first element is a sentence

    Returns: set[(int, int, any, str)] - set of tuples (row ID, number, char, sentence)
    """

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

                pos = 0
                found_all = True
                for w in words:
                    try:
                        pos = reference_words.index(w, pos) + 1
                    except ValueError:
                        found_all = False
                        break
                if found_all:
                    matching.add((row_id, number, char, sentence))

    return matching


