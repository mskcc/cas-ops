#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script for converting KB, MB, GB values to Bytes
https://stackoverflow.com/questions/42865724/python-parse-human-readable-filesizes-into-bytes

$ cut -f14 logs/2020-04-24_21-22-31/trace.txt | tail -n +2 | ./mem_convert.py

$ ./mem_convert.py '4 GB' '8 GB' "1MB" "4GB" "10.5 KB"
"""
import sys
import re

units = {
    "B": 1,
    "KB": 10**3,
    "MB": 10**6,
    "GB": 10**9,
    "TB": 10**12
}

def parse_size(size):
    """
    Convert human readable bytes sizes into interger number of bytes

    Parameters
    ----------
    size: str
        a string denoting the size

    Output
    ------
    int
        the integer size in bytes

    Examples
    --------

    >>> parse_size('4 GB')
    4000000000

    >>> parse_size('1MB')
    1000000

    >>> parse_size('10.5 KB')
    10500
    """
    size = size.upper()
    if not re.match(r' ', size):
        # try to split the unit apart from the number
        size = re.sub(r'([KMGT]?B)', r' \1', size)
    number, unit = [string.strip() for string in size.split()]
    return int(float(number)*units[unit])


def main():
    """
    """
    args = sys.argv[1:]
    input_values = []
    if len(args) < 1:
        # read list of values from stdin
        input_values = [ item.strip() for item in sys.stdin.readlines() ]
    else:
        # get input values from CLI args
        input_values = args

    for value in input_values:
        print(parse_size(value))


if __name__ == '__main__':
    main()
