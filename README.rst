obsub
=====

|Version| |License|

Small python module that implements the observer pattern via a
decorator.

**Deprecation notice**

This module has been unmaintained since around 2014. The authors have
moved on to other alternatives to event handling. There is also
`observed <https://github.com/DanielSank/observed>`_ by @DanielSank, which
was partially inspired by *obsub*, however, has not seen many updates lately.
@milibopp has been writing with functional reactive programming (FRP), but
not for Python.

FRP is a higher-level abstraction than the observer pattern, that essentially
is a purely functional approach to unidirectional dataflow, composing your
programs of event stream transformations. Experience has shown, that is easier
to compose and to test than the raw observer pattern. A solid implementation in
Python is `RxPY <https://github.com/ReactiveX/RxPY>`_, part of the ReactiveX
project.


Description
-----------

This is based on a `thread on stackoverflow
<http://stackoverflow.com/questions/1904351/python-observer-pattern-examples-tips>`_
(the example of C#-like events by Jason Orendorff), so I don't take any
credit for the idea. I merely made a fancy module with documentation and
tests out of it, since I needed it in a bigger project. It is quite
handy and I've been using it in a couple of projects, which require some
sort of event handling.

Thus it is `licensed as
CC0 <http://creativecommons.org/publicdomain/zero/1.0/>`__, so basically
do-whatever-you-want to the extent legally possible.


Installation
------------

*obsub* is available on PyPI, so you can simply install it using
``pip install obsub`` or you do it manually using ``setup.py`` as with
any python package.


Usage
-----

The ``event`` decorator from the ``obsub`` module is used as follows:

.. code:: python

    from obsub import event

    # Define a class with an event
    class Subject(object):
        @event
        def on_stuff(self, arg):
            print('Stuff {} happens'.format(arg))

    # Now define an event handler, the observer
    def handler(subject, arg):
        print('Stuff {} is handled'.format(arg))

    # Wire everything up...
    sub = Subject()
    sub.on_stuff += handler

    # And try it!
    sub.on_stuff('foo')

You should now get both print messages from the event itself and the
event handler function, like so:

::

    Stuff foo happens
    Stuff foo is handled


Contribution and feedback
-------------------------

*obsub* is developed on `github <https://github.com/milibopp/obsub>`__.

If you have any questions about this software or encounter bugs, you're welcome
to open a `new issue on github <https://github.com/milibopp/obsub/issues/new>`__.

In case you do not want to use github for some reason, you can alternatively
send an email one of us:

- `Emilia Bopp <contact@ebopp.de>`__
- `André-Patrick Bubel <code@andre-bubel.de>`__
- `Thomas Gläßle <t_glaessle@gmx.de>`__

Feel free to contribute patches as pull requests as you see fit. Try to be
consistent with PEP 8 guidelines as far as possible and test everything.
Otherwise, your commit messages should start with a capitalized verb for
consistency. Unless your modification is completely trivial, also add a message
body to your commit.


Credits
-------

Thanks to Jason Orendorff on for the idea on stackoverflow. I also want
to thank @coldfix and @Moredread for contributions and feedback.

.. |Version| image:: https://img.shields.io/pypi/v/obsub.svg
   :target: https://pypi.python.org/pypi/obsub/
   :alt: Latest Version
.. |License| image:: https://img.shields.io/pypi/l/obsub.svg
   :target: https://pypi.python.org/pypi/obsub/
   :alt: License
