#!/usr/bin/env python
# coding: utf-8


def classify(article):
    title = article.get('resolved_title')
    return title is None or title.strip() == ''


if __name__ == '__main__':
    from runner import run
    run(classify)
