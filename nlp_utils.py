from typing import Dict

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


class NLPProcessor:
    def __init__(self):
        self.segmenter = Segmenter()
        self.morph_vocab = MorphVocab()

        self.emb = NewsEmbedding()
        self.morph_tagger = NewsMorphTagger(self.emb)
        self.syntax_parser = NewsSyntaxParser(self.emb)
        self.ner_tagger = NewsNERTagger(self.emb)

        self.names_extractor = NamesExtractor(self.morph_vocab)

    def process(self, text: str) -> Doc:
        doc = Doc(text)
        doc.segment(self.segmenter)
        doc.tag_morph(self.morph_tagger)

        for token in doc.tokens:
            token.lemmatize(self.morph_vocab)

        doc.parse_syntax(self.syntax_parser)
        return doc


def filter_by_count(d: Dict[str, int], min_num) -> Dict[str, int]:
    return {key:d[key] for key in d if d[key] >= min_num}


def sort_by_count(d: Dict[str, int]) -> Dict[str, int]:
    srt = sorted(d.items(), key=lambda x: x[1], reverse=True)
    return {v[0]:v[1] for v in srt}
