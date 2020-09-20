import json
from typing import Dict

import csv
import pandas as pd


def fix_multiline_text(text: str) -> str:
    text = text + '.'
    text = text.replace('\r', '.\r\n')
    previous_text = None
    while text != previous_text:
        previous_text = text
        for delimeter in [';', '.', ',', '!', '?', ':', ' ']:
            text = text.replace(delimeter + '.', '.')
    return text


def load_df(fname: str) -> pd.DataFrame:
    data = []
    with open(fname, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            row['description'] = fix_multiline_text(row['description'])
            data.append(row)
    df = pd.DataFrame(data)
    pd.set_option('display.max_columns', None)
    print(df.head())
    return df


def load_resume() -> pd.DataFrame:
    return load_df('resume_to_hackaton.csv')


def load_vacancies() -> pd.DataFrame:
    return load_df('vacancies_to_hackaton.csv')
