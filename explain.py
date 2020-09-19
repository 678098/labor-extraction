import time

from load_data import load_resume, load_vacancies
from nlp_utils import NLPProcessor


def extract_profession(proc: NLPProcessor, text: str) -> str:
    doc = proc.process(text)

    tokens_by_id = {token.id: token for token in doc.tokens}

    # print(doc.tokens)

    for token in doc.tokens:
        # skipping non-main word
        if token.rel in ['root', 'appos']:
            return token.lemma

        if token.pos != 'NOUN':
            continue
        if not token.head_id in tokens_by_id:
            continue
        parent = tokens_by_id[token.head_id]
        if parent.pos != 'NOUN':
            continue
        meme = f'{parent.lemma} {token.lemma}'

    return tokens_by_id[min(tokens_by_id.keys())].lemma


def main():
    proc = NLPProcessor()
    professions = {}

    df = load_vacancies()
    for i in range(df.shape[0]):
        prof = extract_profession(proc, df['name'][i])
        if prof in professions:
            professions[prof] += 1
        else:
            professions[prof] = 1

    nouns = professions
    nouns = {word: nouns[word] for word in nouns if nouns[word] > 10}
    nouns = sorted(nouns.items(), key=lambda x: x[1], reverse=True)
    print(nouns)


if __name__ == "__main__":
    main()