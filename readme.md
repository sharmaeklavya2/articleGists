# Article Gists

A website that lists the gists of research articles and categorizes them by topics.

I'm often interested in knowing the precise statement of all the main claim(s) of a research paper,
but doing so involves finding the paper's PDF and then manually searching it.
This takes time, especially if the paper uses non-standard notation.
Ideally, the abstract should give me this information, but it either doesn't,
or the useful info is buried in a long paragraph.
Hence, I decided that whenever I read a paper (even if I read it briefly),
I'm going to note down the main claims.
This is useful if I need to look at the paper many times in the future,
e.g., when writing the 'Related Work' section of my papers,
or when I need to look at multiple papers together to get a high-level overview of the state of research in a topic.

Information about each article is placed in a JSON file.
The `createWebsite.py` script takes as input a directory containing these JSON files and outputs a website.
The `articles` directory contains JSON files that I curated.
Example invocation:

    python3 createWebsite.py -i articles -o output

## Filtering

You can filter articles based on topics and subtopics.
There's currently no UI for this.
You'll have to open your browser's console and call the `filterArticles` function.
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

&copy; 2023 Eklavya Sharma

The JSON files in the `articles` directory are under [CC0](https://choosealicense.com/licenses/cc0-1.0/).
Other than that, all code is licensed under [GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/).
This roughly means that you are free to use, modify, and distribute this data and code.
