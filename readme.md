# Article Gists

Create a website that lists the gists of research articles and categorizes them by topics.
This is useful for writing the 'Related Work' section in research papers.

Place information about each article in a JSON file.
The `createWebsite.py` script takes as input a directory containing these JSON files and outputs a website.
The `articles` directory contains JSON files that I curated.
Example invocation:

    python3 createWebsite.py articles output

## Filtering

You can filter articles based on topics and subtopics.
To do this, you'll have to open your browser's console and call the `filterArticles` function.
Here are a few examples:

    filterArticles(hasTopicF('marketEquilibrium'));
    filterArticles(hasSubtopicF('fairDivision', 'ef1'));

You can compose conditions using functions `andF` and `orF`:

    filterArticles(andF([hasSubtopicF('fairDivision', 'ef1'), hasSubtopicF('fairDivision', 'prop')]));
    filterArticles(orF([hasSubtopicF('fairDivision', 'ef1'), hasSubtopicF('fairDivision', 'prop')]));

`filterArticles` works by reading `articles.json`, which is written to the output directory
by `createWebsite.py`. You can also create your own filter functions if you want to filter
on something other than topics and subtopics. See `script.js` to get started.

If you have ideas for a better UI for filtering, please let me know by
opening an issue or pull request or contacting me personally.

## Type checking

Python code has been type-annotated. To type-check using [mypy](http://mypy-lang.org/), run

    mypy --strict createWebsite.py

## Freedom to use

&copy; 2022 Eklavya Sharma

All code is licensed under [GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/).
This roughly means that you are free to use, modify and distribute this code.
