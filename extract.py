import os
import json
import time

from load_data import load_resume, save_descriptions
from nlp_utils import NLPProcessor, sort_by_count
from config import main_words, non_main_words


def extract_profession(proc: NLPProcessor, text: str) -> str:
    text = str(text).replace('.', ' ')
    text = str(text).replace(',', ' ')
    doc = proc.process(text)

    tokens_by_id = {token.id: token for token in doc.tokens}

    root_id = None
    for token in doc.tokens:
        # skipping non-main word
        if token.rel in ['root', 'appos']:
            root_id = token.id
            break

    if root_id is None:
        return tokens_by_id[min(tokens_by_id.keys())].lemma

    ids = {root_id}
    expand_factor = 1
    for i in range(expand_factor):
        next_ids = set(ids)
        for token in doc.tokens:
            if token.head_id in ids:
                next_ids.add(token.id)
        ids = next_ids

    prf_words = [token.lemma for token in doc.tokens if token.id in ids]
    return ' '.join(prf_words)


def extract_memes(doc):
    memes = []

    tokens_by_id = {token.id: token for token in doc.tokens}
    for token in doc.tokens:
        if token.pos != 'NOUN':
            continue
        if not token.head_id in tokens_by_id:
            continue
        parent = tokens_by_id[token.head_id]
        if parent.pos != 'NOUN':
            continue
        if (parent.lemma in non_main_words) or (not parent.lemma in main_words):
            continue
        meme = f'{parent.lemma} {token.lemma}'
        memes.append(meme)
    return set(memes)


def segment_text(data):
    tstart = time.time()

    proc = NLPProcessor()

    memes = dict()
    wcounters_by_type = dict()

    for i in range(data.shape[0]):
        text = data['description'][i]
        # print(text)
        doc = proc.process(text)

        for meme in extract_memes(doc):
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

    print(f'Word types: {list(wcounters_by_type.keys())}')
    print(memes)

    for wtype in wcounters_by_type:
        with open(f'output/counters_{wtype}.json', 'w', encoding='utf-8') as f:
            wcounters_by_type[wtype] = sort_by_count(wcounters_by_type[wtype])
            f.write(json.dumps(wcounters_by_type[wtype], ensure_ascii=False))

    with open(f'output/memes.json', 'w', encoding='utf-8') as f:
        memes = sort_by_count(memes)
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