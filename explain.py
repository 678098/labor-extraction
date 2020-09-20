import json

from load_data import load_resume, load_vacancies
from nlp_utils import NLPProcessor, filter_by_count, sort_by_count
from extract import extract_profession


def main():
    proc = NLPProcessor()
    professions = {}

    df = load_resume()
    for i in range(df.shape[0]):
        prof = extract_profession(proc, df['position'][i])
        # print(prof, df['position'][i])
        if prof in professions:
            professions[prof] += 1
        else:
            professions[prof] = 1

    professions = sort_by_count(professions)
    print(professions)

    with open(f'output/professions.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(professions, ensure_ascii=False))


if __name__ == "__main__":
    main()