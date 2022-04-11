Changelog
---------

v0.2
~~~~

From a user perspective the preservation of function signatures and a couple of
bug fixes are probably most relevant. Python 2.5 is no longer tested by
continuous integration, though we try to avoid unnecessary changes that might
break backwards compatibility.

In addition, there are quite a number of changes that mostly concern
developers.

- Function signatures are now preserved correctly by the event decorator. This
  is true only for python3. On python2 there is no support for default
  arguments, currently
- Some fixes to memory handling and tests thereof. This includes a more generic
  handling of the garbage collection process within the test suite to make it
  pass on pypy, too.
- Massive refactoring of test suite from one very long doctest to more focused
  unit tests.
- The documentation has been converted from Markdown to reStructuredText, since
  it is compatible with both PyPI and GitHub.
- Various improvements and some streamlining of the documentation.
- Fix package name in license.
- Continuous integration now includes coveralls.io support.
- Support for Python 2.5 is no longer tested using Travis CI, since they have
  dropped support for this version.


v0.1.1
~~~~~~

- Add __all__ attribute to module
- Fix a couple of documentation issues


v0.1
~~~~

*Initial release*
