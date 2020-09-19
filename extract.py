import os
import json
import time

from load_data import load_resume, save_descriptions
from nlp_utils import NLPProcessor


from natasha import (
    Segmenter,
    MorphVocab,

    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,
    NewsNERTagger,

    PER,
    NamesExtractor,

    Doc
)


def segment_text(data):
    tstart = time.time()

    proc = NLPProcessor()

    memes = dict()
    wcounters_by_type = dict()

    for i in range(data.shape[0]):
        text = data['description'][i]
        # print(text)
        doc = proc.process(text)

        tokens_by_id = {token.id: token for token in doc.tokens}

        for token in doc.tokens:
            if token.pos != 'NOUN':
                continue
            if not token.head_id in tokens_by_id:
                continue
            parent = tokens_by_id[token.head_id]
            if parent.pos != 'NOUN':
                continue
            meme = f'{parent.lemma} {token.lemma}'
            if meme in memes:
                memes[meme] += 1
            else:
                memes[meme] = 1


        # print(doc.sents[0])
        # doc.sents[0].syntax.print()

        for token in doc.tokens:
            if not token.pos in wcounters_by_type:
                wcounters_by_type[token.pos] = {}

            # print(token)
            lemma = token.lemma
            if lemma in wcounters_by_type[token.pos]:
                wcounters_by_type[token.pos][lemma] += 1
            else:
                wcounters_by_type[token.pos][lemma] = 1
        # print(doc.tokens[:5])
        # print(doc.sents[:5])
        # print('\n\n')

    memes = {meme: memes[meme] for meme in memes if memes[meme] > 5}
    memes = sorted(memes.items(), key=lambda x: x[1], reverse=True)

    print(f'Word types: {list(wcounters_by_type.keys())}')
    print(memes)

    for wtype in wcounters_by_type:
        with open(f'output/counters_{wtype}.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(wcounters_by_type[wtype], ensure_ascii=False))

    with open(f'output/memes.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(memes, ensure_ascii=False))

    tend = time.time()
    print(f'Extraction took {tend - tstart} seconds')


def main():
    try:
        os.makedirs('output')
    except FileExistsError:
        pass
    df = load_resume()
    save_descriptions(df)
    segment_text(df)


if __name__ == "__main__":
    main()