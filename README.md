# ripit (Forked from BoilerPy3 a beautiful library.)

![PyPI - Version](https://img.shields.io/pypi/v/ripit)
[![Updates](https://pyup.io/repos/github/pyupio/pyup/shield.svg)](https://pyup.io/repos/github/pyupio/pyup/)
![](https://github.com/sourcepirate/ripit/actions/workflows/test.yml/badge.svg)
![](https://github.com/sourcepirate/ripit/actions/workflows/publish.yml/badge.svg)

Original Boilerpy3 was not maintianed. I forked it to add some features changes.
No changes to license 

## About

BoilerPy3 is a native Python [port](https://github.com/natural/java2python) of Christian Kohlschütter's [Boilerpipe](https://github.com/kohlschutter/boilerpipe) library, released under the Apache 2.0 Licence.

This package is based on [sammyer's](https://github.com/sammyer) [BoilerPy](https://github.com/sammyer/BoilerPy), specifically [mercuree's](https://github.com/mercuree) [Python3-compatible fork](https://github.com/mercuree/BoilerPy). This fork updates the codebase to be more Pythonic (proper attribute access, docstrings, type-hinting, snake case, etc.) and make use Python 3.6 features (f-strings), in addition to switching testing frameworks from Unittest to PyTest.

**Note**: This package is based on Boilerpipe 1.2 (at or before [this commit](https://github.com/kohlschutter/boilerpipe/tree/b0816590340f4317f500c64565b23beb4fb9a827)), as that's when the code was originally ported to Python. I experimented with updating the code to match Boilerpipe 1.3, however because it performed worse in my tests, I ultimately decided to leave it at 1.2-equivalent.


## Installation

To install the latest version from PyPI, execute:

```shell
pip install ripit
```


## Usage

The top-level interfaces are the Extractors. Use the `get_content()` methods to extract the filtered text.

```python
from ripit import extractors

extractor = extractors.ArticleExtractor()

# From a URL
content = extractor.get_content_from_url('http://www.example.com/')

# From a file
content = extractor.get_content_from_file('tests/test.html')

# From raw HTML
content = extractor.get_content('<html><body><h1>Example</h1></body></html>')
```

Alternatively, use `get_doc()` to return a Boilerpipe document from which you can get more detailed information.

```python
from ripit import extractors

extractor = extractors.ArticleExtractor()

doc = extractor.get_doc_from_url('http://www.example.com/')
content = doc.content
title = doc.title
```


## Extractors


### DefaultExtractor

Usually worse than ArticleExtractor, but simpler/no heuristics. A quite generic full-text extractor. 


### ArticleExtractor

A full-text extractor which is tuned towards news articles. In this scenario it achieves higher accuracy than DefaultExtractor. Works very well for most types of Article-like HTML.

### ArticleSentencesExtractor

A full-text extractor which is tuned towards extracting sentences from news articles.


### LargestContentExtractor

A full-text extractor which extracts the largest text component of a page. For news articles, it may perform better than the DefaultExtractor but usually worse than ArticleExtractor


### CanolaExtractor

A full-text extractor trained on [krdwrd](http://krdwrd.org) [Canola](https://krdwrd.org/trac/attachment/wiki/Corpora/Canola/CANOLA.pdf). Works well with SimpleEstimator, too.


### KeepEverythingExtractor

Dummy extractor which marks everything as content. Should return the input text. Use this to double-check that your problem is within a particular Extractor or somewhere else.


### NumWordsRulesExtractor

A quite generic full-text extractor solely based upon the number of words per block (the current, the previous and the next block).
