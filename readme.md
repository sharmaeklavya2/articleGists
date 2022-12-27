# Article Gists

Create a website that lists the gists of research articles and categorizes them by topics.
This is useful for writing the 'Related Work' section in research papers.

Place information about each article in a JSON file.
The `createWebsite.py` script takes as input a directory containing these JSON files and outputs a website.
The `articles` directory contains JSON files that I curated.
Example invocation:

    python3 createWebsite.py articles output

## Type checking

Python code has been type-annotated. To type-check using [mypy](http://mypy-lang.org/), run

    mypy --strict createWebsite.py

## Freedom to use

&copy; 2022 Eklavya Sharma

All code is licensed under [GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/).
This roughly means that you are free to use, modify and distribute this code.
