===============
Proglang Corpus
===============

This Python script will build a zip archive of some of the `most important Github
repositories <https://github.com/repositories>`_ using Github's `API
<http://developer.github.com/v3/repos/contents/>`_ to access the contents. The
files are then concatenated by programming language, as determined by
`Github's linguist repo <https://github.com/github/linguist/>`_.

The result is a corpus organized by programming languages and suitable for
training or evaluating keyboard layouts and other methods. All the code in the
corpus remains under its original copyright.



Requirements
------------

Both the excellent requests package and pyyaml library are necessary to run
this script (written for Python 3).

License
-------

This code is released under the MIT license
