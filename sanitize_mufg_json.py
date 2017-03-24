#!/usr/bin/env python3
# coding: utf-8

import copy
import json
import re
import sys

from functools import reduce


status_key = '確定情報'
store_key = 'ご利用店名（海外ご利用店名／海外都市名）'
payment_key = 'ご利用金額（円）'
note_key = '現地通貨額・通貨名称・換算レート'
type_key = 'type'

installment_head = '分割払い'


class PaymentType:
    NORMAL = 'normal'
    INSTALLMENT = 'installment'


def main():
    rows = list(
        reduce(
            lambda rows, f: f(rows),
            [
                provide_type_explictly,
                filter_payment,
                sanitize_store_and_note,
                sanitize_installament_description,
                extract_installment
            ],
            json.load(sys.stdin)
        )
    )

    print(json.dumps(rows))


def provide_type_explictly(rows):
    payment_type = PaymentType.NORMAL

    for r in rows:
        if len(r[status_key]) > 0:
            copied_row = copy.deepcopy(r)
            copied_row[type_key] = payment_type
            yield copied_row
        else:
            if installment_head in r[store_key]:
                payment_type = PaymentType.INSTALLMENT
            yield r


def filter_payment(rows):
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

    def translate(row):
        copied_row = copy.deepcopy(row)
        copied_row[store_key] = row[store_key].translate(translation).strip()
        copied_row[note_key] = row[note_key].translate(translation).strip()
        return copied_row

    return map(translate, rows)


def extract_installment(rows):
    def extract(row):
        if row[type_key] != 'installment':
            return row

        copied_row = copy.deepcopy(row)
        copied_row[payment_key] = first(lambda x: len(x) > 0, row[note_key].split())

        return copied_row

    return map(extract, rows)


def sanitize_installament_description(rows):
    pattern = re.compile('[0-9]+\s*(回払い|ｶｲﾊﾞﾗｲ)\s*([0-9]+\s*(回目|ｶｲﾒ))?')

    def sanitize(row):
        copied_row = copy.deepcopy(row)
        copied_row[store_key] = pattern.sub('', row[store_key]).strip()
        return copied_row

    return map(sanitize, rows)


def first(f, iterable):
    for x in iterable:
        if f(x):
            return x
    return None


if __name__ == '__main__':
    main()
