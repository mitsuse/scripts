#!/usr/bin/env python3
# coding: utf-8

import copy
import json
import re
import sys

from functools import reduce


def main():
    rows = reduce(
        lambda rows, f: f(rows),
        [
            provide_type_explictly,
            filter_payment,
            sanitize_store_and_note,
            extract_installment
        ],
        json.load(sys.stdin)
    )

    for r in rows:
        print(r)


def provide_type_explictly(rows):
    status_key = '確定情報'
    store_key = 'ご利用店名（海外ご利用店名／海外都市名）'
    type_key = 'type'
    installment_head = '分割払い'
    payment_type = 'normal'

    for r in rows:
        if len(r[status_key]) > 0:
            r[type_key] = payment_type
        else:
            if installment_head in r[store_key]:
                payment_type = 'installment'
        yield r


def filter_payment(rows):
    status_key = '確定情報'
    return filter(lambda x: len(x[status_key]) > 0, rows)


def sanitize_store_and_note(rows):
    translation = {
        ord('０'): '0',
        ord('１'): '1',
        ord('２'): '2',
        ord('３'): '3',
        ord('４'): '4',
        ord('５'): '5',
        ord('６'): '6',
        ord('７'): '7',
        ord('８'): '8',
        ord('９'): '9',
        ord('，'): ',',
        ord('\u3000'): ' '
    }

    store_key = 'ご利用店名（海外ご利用店名／海外都市名）'
    note_key = '現地通貨額・通貨名称・換算レート'

    def translate(row):
        copied_row = copy.deepcopy(row)
        copied_row[store_key] = row[store_key].translate(translation).strip()
        copied_row[note_key] = row[note_key].translate(translation).strip()
        return copied_row

    return map(translate, rows)


def extract_installment(rows):
    def extract(row):
        note_key = '現地通貨額・通貨名称・換算レート'
        payment_key = 'ご利用金額（円）'
        type_key = 'type'

        if row[type_key] != 'installment':
            return row

        copied_row = copy.deepcopy(row)
        copied_row[payment_key] = first(lambda x: len(x) > 0, row[note_key].split())

        return copied_row

    return map(extract, rows)


def first(f, iterable):
    for x in iterable:
        if f(x):
            return x
    return None


if __name__ == '__main__':
    main()
