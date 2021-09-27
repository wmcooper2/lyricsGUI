def gap_search(lyrics: list, words: list, gap: int) -> list:
#     print(f"lyrics: {lyrics}")
#     print(f"words: {words}")
    if words:
        lyrics_index = lyrics.index(words[0])
#         print(f"lyrics_index: {lyrics_index}")
        try:
            if lyrics_index is not None:
                if lyrics_index > len(lyrics) - len(words) or lyrics_index > gap:
#                     return [False]
                    return str(False)
#                 return [lyrics_index] + [gap_search(lyrics[lyrics_index+1:], words[1:])]
                return str(lyrics_index) + str(gap_search(lyrics[lyrics_index+1:], words[1:], gap))
            else:
#                 return [False]
                return str(False)
        except ValueError:  # word not found in lyrics 
#             return [False]
            return str(False)
    else:
#         return [True]
        return str(True)


# sentence = "I'm not as tall as what you said."
# sentence = "I'm not as tallas what you said."
sentence = "I'm not as tall what you said what you said as ."
# words = "as tall said you as cat"
# words = "as tall said you as"
words = "as said"

sentence = sentence.split(" ")
words = words.split(" ")
res = gap_search(sentence, words, 2)
print("bool:", res.endswith("True"))

if res.endswith("True"):
    final_seq = res.rstrip("True")
    print(f"final_seq: {final_seq}")
else:
    print(False)
