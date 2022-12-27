#!/usr/bin/env python3

"""
Reads JSON files in a directory and outputs a single JSON file
whose keys are file names and values are file contents.
"""

import argparse
import json
import os
import shutil
from collections.abc import Collection, Mapping, Sequence
from os.path import dirname, abspath, relpath, splitext
from os.path import join as pjoin
from typing import Callable, TypeVar

from jinja2 import Template


KT = TypeVar('KT')
VT = TypeVar('VT')
ArticleT = dict[str, object]
ArticlesT = dict[str, ArticleT]

BASE_DIR = dirname(abspath(__file__))
TEMPLATE_PATH = pjoin(BASE_DIR, 'template')

USEFUL_FIELDS = {'title', 'status', 'pubData', 'topics'}
STATIC_FILES = ['style.css']
CONFIG = {
    "title": "Article Gists",
    "mathengine": "mathjax",
}


def processArticle(article: ArticleT) -> None:
    # add authorsStr
    assert 'pubData' in article
    pubData = article['pubData']
    assert isinstance(pubData, dict)
    authorsList = [firstName + ' ' + lastName for firstName, lastName
        in pubData.get('authors', [])]
    if len(authorsList) == 0:
        authorsStr = None
    elif len(authorsList) == 1:
        authorsStr = authorsList[0]
    elif len(authorsList) == 2:
        authorsStr = authorsList[0] + ' and ' + authorsList[1]
    else:
        authorsList[-1] = 'and ' + authorsList[-1]
        authorsStr = ', '.join(authorsList)
    pubData['authorsStr'] = authorsStr

    # add topicsStr
    if 'topics' in article:
        article['topicsStr'] = json.dumps(article['topics'])


def prettyJsonHelper(obj: object) -> tuple[str, int]:
    if isinstance(obj, str):
        return (json.dumps(obj), 0)
    elif isinstance(obj, Sequence):
        maxHeight = 0
        serials = []
        for x in obj:
            jx, hx = prettyJsonHelper(x)
            serials.append(jx)
            maxHeight = max(maxHeight, hx)
        sep = ',\n' if maxHeight >= 1 else ', '
        delims = ('[\n', '\n]') if maxHeight >= 1 else ('[', ']')
        return (delims[0] + sep.join(serials) + delims[1], maxHeight + 1)
    elif isinstance(obj, Mapping):
        maxHeight = 0
        serials = []
        for k, v in obj.items():
            jv, hv = prettyJsonHelper(v)
            serials.append(json.dumps(k) + ': ' + jv)
            maxHeight = max(maxHeight, hv)
        sep = ',\n' if maxHeight >= 1 else ', '
        delims = ('{\n', '\n}') if maxHeight >= 1 else ('{', '}')
        return (delims[0] + sep.join(serials) + delims[1], maxHeight + 1)
    else:
        return (json.dumps(obj), 0)


def prettyJsonize(obj: object) -> str:
    return prettyJsonHelper(obj)[0]


def jsonConcat(ipath: str) -> ArticlesT:
    objs: dict[str, ArticleT] = {}
    for (dpath, dnames, fnames) in os.walk(ipath):
        for fname in fnames:
            basename, ext = splitext(fname)
            if ext == '.json':
                fpath = pjoin(dpath, fname)
                with open(fpath) as fp:
                    d = json.load(fp)
                assert isinstance(d, dict)
                key = relpath(fpath, ipath)[:-5].replace('\\', '.').replace('/', '.')
                if key in objs:
                    raise ValueError('duplicate key: ' + key)
                objs[key] = d
    return objs


def sortDict(d: Mapping[KT, VT], sortKey: Callable[[tuple[KT, VT]], int]) -> dict[KT, VT]:
    return dict(sorted(d.items(), key=sortKey))


def articleSortKey(kvPair: tuple[str, object]) -> int:
    k, v = kvPair
    try:
        assert isinstance(v, Mapping)
        value = v['pubData']['year']
        assert isinstance(value, int)
        return value
    except (KeyError, IndexError):
        return 0


def pruneKeys(d: Mapping[KT, VT], usefulKeys: Collection[KT]) -> dict[KT, VT]:
    return {k: v for k, v in d.items() if k in usefulKeys}


def pruneArticles(articles: ArticlesT) -> ArticlesT:
    return {id: pruneKeys(articleInfo, USEFUL_FIELDS) for id, articleInfo in articles.items()}


def createWebsite(ipath: str, opath: str) -> None:
    articles = jsonConcat(ipath)
    articles = sortDict(articles, articleSortKey)
    for k, v in articles.items():
        processArticle(v)
    articlesPruned = pruneArticles(articles)

    os.makedirs(opath, exist_ok=True)
    with open(pjoin(opath, 'articles.json'), 'w') as fp:
        j = prettyJsonize(articlesPruned)
        fp.write(j)

    for fname in STATIC_FILES:
        shutil.copyfile(pjoin(TEMPLATE_PATH, fname), pjoin(opath, fname))

    context = {'config': CONFIG, 'articles': articles}
    with open(pjoin(TEMPLATE_PATH, 'index.html.jinja2')) as fp:
        indexTemplate = Template(fp.read(), trim_blocks=True)
    indexPage = indexTemplate.render(context)
    with open(pjoin(opath, 'index.html'), 'w') as fp:
        fp.write(indexPage)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ipath', help='path to directory containing JSON files')
    parser.add_argument('opath', help='path to output directory')
    args = parser.parse_args()

    createWebsite(args.ipath, args.opath)
