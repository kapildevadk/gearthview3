# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

def parse(s: str) -> list:
    """
    Parses a string in s-expression format and returns a nested list.
    """
    s = s.strip()
    expr = []
    while s:
        if s[0] == '(':
            newSexp = []
            if expr:
                expr[-1].append(newSexp)
            expr.append(newSexp)
            s = s[1:]
            continue
        if s[0] == ')':
            aList = expr.pop()
            s = s[1:]
            if not expr:
                return aList
            continue
        i = 0
        while i < len(s) and s[i].isdigit():
            i += 1
        if i == 0:
            raise ValueError("Invalid input: expected a number")
        length = int(s[:i])
        if length > len(s):
            raise ValueError("Invalid input: number too large")
        data = s[i + 1:i + 1 + length]
        expr[-1].append(data)
        s = s[i + 1 + length:]
    if expr:
        raise ValueError("Invalid input: unmatched opening parenthesis")
    return expr[0]

def pack(sexp: list) -> str:
    """
    Converts a nested list in s-expression format to a string.
    """
    s = ""
    for o in sexp:
        if isinstance(o, (tuple, list)):
            s += '('
