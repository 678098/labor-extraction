import json

from nlp_utils import NLPProcessor, sort_by_count
from load_data import load_resume
from extract import extract_memes, extract_profession


class SchemaEvaluator:
    def __init__(self):
        with open('schema.json', 'r', encoding='utf-8') as f:
            self.schema = json.load(f)
        self.proc = NLPProcessor()

    def evaluate(self, position: str, description: str):
        prof, prof_text = extract_profession(self.proc, position)
        if not prof in self.schema:
            return {}

        sc = self.schema[prof]

        doc = self.proc.process(description)
        memes = extract_memes(doc)

        res = {perk['lemma']: False for perk in sc['perks']}
        for meme_pair in memes:
            meme = meme_pair[0]
            if meme in res:
                res[meme] = True

        return res


def main():
    eval = SchemaEvaluator()

    df = load_resume()
    for i in range(df.shape[0]):
        schema = eval.evaluate(df['position'][i], df['description'][i])
        print(schema)



if __name__ == "__main__":
    main()
