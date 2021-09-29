def gap_search(lyrics: list, words: list, gap: int) -> list:
    if words:
        index = lyrics.index(words[0])
        try:
            if index is not None:
                if index > len(lyrics) - len(words) or index > gap:
                    return str(False)
                return str(index) + str(gap_search(lyrics[index+1:], words[1:], gap))
            else:
                return str(False)
        except ValueError:  # word not found in lyrics 
            return str(False)
    else:
        return str(True)


sentence = "I'm not as tall what you said what you said as ."
words = "as said"

sentence = sentence.split(" ")
words = words.split(" ")
res = gap_search(sentence, words, 2)
print("bool:", res.endswith("True"))
