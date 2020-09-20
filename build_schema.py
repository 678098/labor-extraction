import json

from nlp_utils import filter_by_count


def main():
    with open('output/schema_builder.json', 'r', encoding='utf-8') as f:
        schema_build_info = json.load(f)

    schema = {}
    for prof in schema_build_info:
        anno = schema_build_info[prof]
        total_num = anno['total']
        if total_num < 15:
            continue

        anno['counters'] = filter_by_count(anno['counters'], total_num / 20)

        desc = {
            'lemma': prof,
            'name': anno['name'],
            'total': anno['total'],
            'perks': []
        }

        to_pick = list(anno['counters'].keys())[:20]
        for perk in to_pick:
            perk_desc = {
                'lemma': perk,
                'text': anno['explanations'][perk],
                'type': 'bool'
            }
            desc['perks'].append(perk_desc)
        schema[prof] = desc

    with open(f'schema.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(schema, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    main()
