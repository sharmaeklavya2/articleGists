#!/usr/bin/env python3

"""
Reads JSON files in a directory and outputs a single JSON file
whose keys are file names and values are file contents.
"""

import argparse
import json
import os
import sys
import shutil
from collections.abc import Collection, Mapping, Sequence
from os.path import dirname, abspath, relpath, splitext
from os.path import join as pjoin
from typing import Callable, Optional, TypedDict, TypeVar

from jinja2 import Template


class PubData(TypedDict, total=False):
    authors: Sequence[tuple[str, str]]
    authorsStr: Optional[str]
    doi: str
    arxiv: str
    url: str
    year: int
    venue: str
    type: str
    volume: str
    number: str
    pages: str
    month: int
    publisher: str
    address: str
    longVenue: str
    longPublisher: str


class Article(TypedDict, total=False):
    title: str
    bibtexTitle: str
    gistStatus: str
    paperStatus: str
    pubData: PubData
    topics: Mapping[str, Sequence[str]]
    description: str
    relatedWork: Sequence[str]
    results: Sequence[str]
    bibtex: str


KT = TypeVar('KT')
VT = TypeVar('VT')
ArticlesT = dict[str, Article]

BASE_DIR = dirname(abspath(__file__))
TEMPLATE_PATH = pjoin(BASE_DIR, 'template')

USEFUL_FIELDS = {'title', 'gistStatus', 'paperStatus', 'pubData', 'topics'}
STATIC_FILES = ['style.css', 'script.js']
CONFIG = {
    "title": "Article Gists",
    "mathengine": "mathjax",
}
BIBTEX_TRN = {
    'journal': ['longVenue', 'venue'],
    'booktitle': ['longVenue', 'venue'],
    'publisher': ['longPublisher', 'publisher'],
}
BIBTEX_FORMATS = {
    'article': ['journal', 'year', 'volume', 'number', 'pages'],
    'inproceedings': ['booktitle', 'year', 'volume', 'number', 'pages'],
    'misc': ['year'],
}

acronyms: Optional[Mapping[str, Mapping[str, str]]] = None


def generateBibEntry(id: str, title: str, pubData: PubData) -> str:
    pubType = pubData['type']
    header = '@' + pubType + '{' + id + ',\n'
    bibInfo = {'title': title}
    if 'authors' in pubData:
        bibInfo['author'] = ' and '.join(['{}, {}'.format(l, f) for f, l in pubData['authors']])

    for key in BIBTEX_FORMATS[pubType]:
        if key in BIBTEX_TRN:
            keySeq = BIBTEX_TRN[key]
        else:
            keySeq = [key]
        for key2 in keySeq:
            if key2 in pubData:
                bibInfo[key] = str(pubData[key2])  # type: ignore
                break

    if 'doi' in pubData:
        bibInfo['doi'] = pubData['doi']
    elif 'arxiv' in pubData:
        bibInfo['eprint'] = pubData['arxiv']
        bibInfo['archivePrefix'] = 'arXiv'
    elif 'url' in pubData:
        bibInfo['url'] = pubData['url']

    return header + ',\n'.join([k + '={' + v + '}' for k, v in bibInfo.items()]) + '\n}'


def processArticle(id: str, article: Article) -> None:
    assert 'pubData' in article
    pubData = article['pubData']

    # add authorsStr
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

    # expand acronyms
    if acronyms is not None:
        for k, longK in [('venue', 'longVenue'), ('publisher', 'longPublisher')]:
            try:
                pubData[longK] = acronyms[k][pubData[k]]  # type: ignore
            except KeyError:
                pass

    # bibtex
    if 'type' in pubData:
        article['bibtex'] = generateBibEntry(id,
            article.get('bibtexTitle') or article['title'], pubData)


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
    objs: dict[str, Article] = {}
    for (dpath, dnames, fnames) in os.walk(ipath):
        for fname in fnames:
            basename, ext = splitext(fname)
            if ext == '.json':
                fpath = pjoin(dpath, fname)
                key = relpath(fpath, ipath)[:-5].replace('\\', '.').replace('/', '.')
                if key in objs:
                    raise ValueError('duplicate key: ' + key)
                with open(fpath) as fp:
                    try:
                        d = json.load(fp)
                    except json.JSONDecodeError as e:
                        print(key + '.json is invalid JSON', file=sys.stderr)
                        raise e
                objs[key] = d
    return objs


def sortDict(d: Mapping[KT, VT], sortKey: Callable[[tuple[KT, VT]], int]) -> dict[KT, VT]:
    return dict(sorted(d.items(), key=sortKey))


def articleSortKey(kvPair: tuple[str, Article]) -> int:
    k, v = kvPair
    try:
        value = v['pubData']['year']
        return value
    except (KeyError, IndexError):
        return 0


def pruneKeys(d: Article, usefulKeys: Collection[KT]) -> Article:
    return {k: v for k, v in d.items() if k in usefulKeys}  # type: ignore


def pruneArticles(articles: ArticlesT) -> ArticlesT:
    return {id: pruneKeys(articleInfo, USEFUL_FIELDS) for id, articleInfo in articles.items()}


def createWebsite(ipath: str, opath: str, acronymsPath: str) -> None:
    global acronyms
    with open(acronymsPath) as fp:
        acronyms = json.load(fp)

    articles = jsonConcat(ipath)
    articles = sortDict(articles, articleSortKey)
    for k, v in articles.items():
        processArticle(k, v)
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
    parser.add_argument('-i', '--input', help='path to directory containing article JSON files')
    parser.add_argument('-o', '--output', required=True, help='path to output directory')
    parser.add_argument('--acronyms', help='path to acronyms JSON file')
    args = parser.parse_args()

    ipath = args.input or pjoin(BASE_DIR, 'articles')
    acronymsPath = args.acronyms or pjoin(BASE_DIR, 'acronyms.json')
    createWebsite(ipath, args.output, acronymsPath)
