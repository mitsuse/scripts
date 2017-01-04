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
            extract_payment,
            sanitize_installment
        ],
        json.load(sys.stdin)
    )

    for r in rows:
        print(r)


def replace_spaces(rows):
    return rows


def provide_type_explictly(rows):
    status_key = '確定情報'
    store_key = 'ご利用店名（海外ご利用店名／海外都市名）'
    type_key = 'type'
    installment_head = '分割払い既存ご利用明細'
    payment_type = 'normal'

    for r in rows:
        if len(r[status_key]) > 0:
            r[type_key] = payment_type
        else:
            if installment_head in r[store_key]:
                payment_type = 'installment'
        yield r


def extract_payment(rows):
    status_key = '確定情報'
    return filter(lambda x: len(x[status_key]) > 0, rows)


def sanitize_installment(rows):
    conversion = {
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
        ord('，'): ','
    }

    def sanitize(row):
        installment_key = '現地通貨額・通貨名称・換算レート'
        payment_key = 'ご利用金額（円）'

        installment = row.get(installment_key)
        if len(installment) == 0:
            return row

        pattern = re.compile('\u3000+')
        payment = first(lambda x: len(x) > 0, pattern.split(installment))
        normalized_payment = payment.translate(conversion)

        copied_row = copy.deepcopy(row)
        copied_row[payment_key] = normalized_payment
        copied_row[installment_key] = ''

        return copied_row

    return map(sanitize, rows)


def first(f, iterable):
    for x in iterable:
        if f(x):
            return x
    return None


if __name__ == '__main__':
    main()
