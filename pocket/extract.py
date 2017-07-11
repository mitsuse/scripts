#!/usr/bin/env python
# coding: utf-8


def main(args):
    import sys
    import json
    raw_classifiy = classifiers[args.target]
    classify = inverse(raw_classifiy) if args.negation else raw_classifiy
    with open(args.input) as f:
        dump_json = json.load(f)
    dump_list = dump_json['list']
    extracted_list = {key: value for key, value in dump_list.items() if classify(value) }
    if args.count:
        print(len(extracted_list))
    else:
        dump_json['list'] = extracted_list
        json.dump(dump_json, sys.stdout)


def inverse(f):
    return lambda x: not f(x)


def classify_favorite(article):
    return article.get('favorite') == '1'


def classify_empty_title(article):
    title = article.get('given_title')
    return title is None or title.strip() == ''


classifiers = {
    'favorite': classify_favorite,
    'empty_title': classify_empty_title
}


def parse(args):
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('target', choices=classifiers.keys(), type=str)
    parser.add_argument('--input', type=str)
    parser.add_argument('--count', default=False, action='store_true')
    parser.add_argument('--negation', default=False, action='store_true')
    return parser.parse_args(args)


if __name__ == '__main__':
    import sys
    main(parse(sys.argv[1:]))
