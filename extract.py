import os
import json
import time

from load_data import load_resume
from nlp_utils import NLPProcessor, sort_by_count
from config import main_words, non_main_words


def load_good_memes():
    with open('output/memes.json', 'r', encoding='utf-8') as f:
        memes = json.load(f)
    return memes


def extract_profession(proc: NLPProcessor, text: str) -> (str, str):
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
        token = tokens_by_id[min(tokens_by_id.keys())]
        return token.lemma, token.text

    ids = {root_id}
    expand_factor = 1
    for i in range(expand_factor):
        next_ids = set(ids)
        for token in doc.tokens:
            if token.head_id in ids:
                next_ids.add(token.id)
        ids = next_ids

    prf_words = [token.text for token in doc.tokens if token.id in ids]
    prf_lemmas = [token.lemma for token in doc.tokens if token.id in ids]
    return ' '.join(prf_lemmas), ' '.join(prf_words).lower()


def extract_memes(doc):
    memes = []

    tokens_by_id = {token.id: token for token in doc.tokens}
    for token in doc.tokens:
        if token.pos != 'NOUN':
            continue
        if not token.head_id in tokens_by_id:
            continue
        if token.head_id == token.id:
            continue
        parent = tokens_by_id[token.head_id]
        if parent.pos != 'NOUN':
            continue
        if (parent.lemma in non_main_words) or (not parent.lemma in main_words):
            continue
        if parent.lemma == token.lemma:
            continue

        if parent.stop < token.start:
            dist = token.start - parent.stop
        else:
            dist = parent.start - token.stop
        if dist > 10:
            continue

        meme_lemma = f'{parent.lemma} {token.lemma}'
        meme_text = f'{parent.text} {token.text}'.lower()
        memes.append((meme_lemma, meme_text))
    return memes


def dump_counters_memes(df):
    tstart = time.time()

    proc = NLPProcessor()

    memes = dict()
    wcounters_by_type = dict()

    for i in range(df.shape[0]):
        text = df['description'][i]
        # print(text)
        doc = proc.process(text)

        for meme_pair in extract_memes(doc):
            meme = meme_pair[0]
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


def dump_professions(df):
    proc = NLPProcessor()
    professions = {}

    for i in range(df.shape[0]):
        prof_lemma, prof_full = extract_profession(proc, df['position'][i])
        # print(prof_lemma, prof_full)
        # print(prof, df['position'][i])
        if prof_lemma in professions:
            professions[prof_lemma] += 1
        else:
            professions[prof_lemma] = 1

    professions = sort_by_count(professions)
    print(professions)

    with open(f'output/professions.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(professions, ensure_ascii=False))


def dump_schema_build_info(df):
    good_memes = load_good_memes().keys()

    proc = NLPProcessor()

    schema = {}
    for i in range(df.shape[0]):
        doc = proc.process(df['description'][i])
        prof, prof_text = extract_profession(proc, df['position'][i])

        if prof in schema:
            schema[prof]['total'] += 1
        else:
            schema[prof] = {'name': prof_text, 'total': 1, 'counters': {}, 'explanations': {}}

        memes = extract_memes(doc)
        for meme_pair in memes:
            meme, meme_text = meme_pair
            if not meme in good_memes:
                continue
            schema[prof]['explanations'][meme] = meme_text
            if meme in schema[prof]['counters']:
                schema[prof]['counters'][meme] += 1
            else:
                schema[prof]['counters'][meme] = 1


    for prof in schema:
        schema[prof]['counters'] = sort_by_count(schema[prof]['counters'])

    with open(f'output/schema_builder.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(schema, indent=4, ensure_ascii=False))


def dump_descriptions(df):
    with open('output/descs.txt', 'w') as f:
        for i in range(df.shape[0]):
            f.write(df['description'][i])
            f.write('\n\n=====================================\n\n')


def main():
    try:
        os.makedirs('output')
    except FileExistsError:
        pass
    df = load_resume()
    # dump_descriptions(df)
    # dump_counters_memes(df)
    # dump_professions(df)
    dump_schema_build_info(df)


if __name__ == "__main__":
    main()