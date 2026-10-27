"""Compact constructors for iq_problems_*.py"""
import math


def H(text, col="y", **k):
    return dict(k="head", text=text, col=col, **k)


def F(text, col="g", at=0.65, **k):
    return dict(k="foot", text=text, col=col, at=at, **k)


def BIG(text, col="y", **k):
    return dict(k="big", text=text, col=col, **k)


def ROW(items, **k):
    return dict(k="row", items=items, **k)


def BARS(vals, **k):
    return dict(k="bars", vals=vals, **k)


def GRID(rows, cols, **k):
    return dict(k="grid", rows=rows, cols=cols, **k)


def NODES(labels, **k):
    return dict(k="nodes", labels=labels, **k)


def TL(items, **k):
    return dict(k="tl", items=items, **k)


def EQ(lines, cols=None, **k):
    return dict(k="eq", lines=lines, cols=cols or [], **k)


def PIE(fracs, **k):
    return dict(k="pie", fracs=fracs, **k)


def NUM(lo, hi, **k):
    return dict(k="numline", min=lo, max=hi, **k)


def S(say, parts, steps=None, stamp=None):
    return dict(say=say, parts=parts, steps=steps or [], stamp=stamp)


def prob(id, org, tag, title, sub, hook_say, hook_text, q, qparts, steps, ans, ans_say, hook_sub=""):
    return dict(id=id, org=org, tag=tag, title=title, sub=sub, hook_say=hook_say, hook_text=hook_text, hook_sub=hook_sub, q=q, qparts=qparts,
                steps=steps, ans=ans, ans_say=ans_say)


def spoken(n):
    """small integers as words for the voice"""
    w = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
         "seventeen", "eighteen", "nineteen", "twenty"]
    return w[n] if 0 <= n <= 20 else str(n)


def birthday_p(n):
    q = 1.0
    for i in range(n):
        q *= (365 - i) / 365
    return 1 - q
