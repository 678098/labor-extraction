import json

from nlp_utils import NLPProcessor, sort_by_count
from load_data import load_resume
from extract import extract_memes, extract_profession


def load_actual_memes():
    with open('output/memes.json', 'r', encoding='utf-8') as f:
        memes = json.load(f)
    return memes


def parse_resume():
    pass


def main():
    good_memes = load_actual_memes().keys()

    df = load_resume()
    proc = NLPProcessor()

    schema = {}

    for i in range(df.shape[0]):
        doc = proc.process(df['description'][i])
        prof = extract_profession(proc, df['position'][i])

        if prof in schema:
            schema[prof]['total'] += 1
        else:
            schema[prof] = {'total': 1}

        memes = extract_memes(doc)
        for meme in memes:
            if not meme in good_memes:
                continue
            if meme in schema[prof]:
                schema[prof][meme] += 1
            else:
                schema[prof][meme] = 1


    for prof in schema:
        schema[prof] = sort_by_count(schema[prof])

    with open(f'output/schema.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(schema, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    main()
