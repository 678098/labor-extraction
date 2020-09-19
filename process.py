import os
import json


def filter_nouns():
    with open('output/counters_NOUN.json', 'r', encoding='utf-8') as f:
        nouns = json.load(f)

    nouns = {word: nouns[word] for word in nouns if nouns[word] > 10}
    nouns = sorted(nouns.items(), key=lambda x: x[1], reverse=True)

    with open('output/nouns_filtered.txt', 'w', encoding='utf-8') as f:
        json.dump(nouns, f, ensure_ascii=False)
    print(nouns)
    for n in nouns:
        print(n)


if __name__ == "__main__":
    filter_nouns()
