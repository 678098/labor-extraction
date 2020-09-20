import os
import json


def filter_nouns():
    with open('output/counters_NOUN.json', 'r', encoding='utf-8') as f:
        nouns = json.load(f)

    main_words = []
    non_main_words = []

    for word in nouns:
        print(f'{word} {nouns[word]}')
        res = input('1 main word, 2 non main word, 3 exit: ')

        if res == '1':
            main_words.append(word)
        elif res == '2':
            non_main_words.append(word)
        elif res == '3':
            break

    main_words = sorted(main_words)
    non_main_words = sorted(non_main_words)
    print('main_words = ', main_words)
    print('non_main_words = ', non_main_words)


if __name__ == "__main__":
    filter_nouns()
