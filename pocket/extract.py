#!/usr/bin/env python
# coding: utf-8


def main(args):
    import sys
    import json
    raw_classifiy = classifiers[args.target]
    classify = inverse(raw_classifiy) if args.negation else raw_classifiy
    with open(args.input) as f:
        dump_json = json.load(f)
    original = dump_json['list']
    classified = {key: value for key, value in original.items() if classify(value) }
    if args.evaluate:
        evaluation = Evaluation(original, classified)
        print('total: {}'.format(evaluation.total))
        print('precision: {}'.format(evaluation.precision))
        print('recall: {}'.format(evaluation.recall))
        print('F: {}'.format(evaluation.f))
    else:
        dump_json['list'] = classified
        json.dump(dump_json, sys.stdout)


class Evaluation(object):
    def __init__(self, original, classified):
        from functools import reduce
        tp = reduce(lambda c, _: c + 1, filter(classify_favorite, classified.values()), 0)
        correct_count = reduce(lambda c, _: c + 1, filter(classify_favorite, original.values()), 0)
        classified_count = len(classified)
        self.__total = len(original)
        self.__precision = tp / float(classified_count) if classified_count > 0 else 0
        self.__recall = tp / float(correct_count) if correct_count > 0 else 0

    @property
    def total(self):
        return self.__total

    @property
    def precision(self):
        return self.__precision

    @property
    def recall(self):
        return self.__recall

    @property
    def f(self):
        recall = self.recall
        precision = self.precision
        return (2 * recall * precision) / (recall + precision) if recall + precision > 0 else 0


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
    parser.add_argument('--evaluate', default=False, action='store_true')
    parser.add_argument('--negation', default=False, action='store_true')
    return parser.parse_args(args)


if __name__ == '__main__':
    import sys
    main(parse(sys.argv[1:]))
