# obsub

Small python module that implements the observer pattern via a decorator.


## Description

This is based on a [thread on stackoverflow]
(http://stackoverflow.com/questions/1904351/python-observer-pattern-examples-tips)
(the example of C#-like events by Jason
Orendorff), so I don't take any credit for the
idea. I merely made a fancy module with documentation and tests out of it,
since I needed it in a bigger project. It is quite handy and I've been using
it in a couple of projects, which require some sort of event handling.

Thus it is [licensed as CC0](http://creativecommons.org/publicdomain/zero/1.0/),
so basically do-whatever-you-want to the extent legally possible.


## Installation

*obsub* is available on PyPI, so you can simply install it using
`pip install obsub` or you do it manually using `setup.py` as with any python
package.


## Usage

The `event` decorator from the `obsub` module is used as follows:

```python
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

```

You should now get both print messages from the event itself and the event
handler function, like so:

```
Stuff foo happens
Stuff foo is handled
```


## Continuous integration

For the fun of it, [Travis CI](https://travis-ci.org/aepsil0n/obsub) is used
for continuous integration. As long as everything is fine, the button below
should be green and shiny!

[![Build Status](https://api.travis-ci.org/aepsil0n/obsub.png?branch=master)](https://travis-ci.org/aepsil0n/obsub)


## Contributing

*obsub* is developed on [github](https://github.com/aepsil0n/obsub). Feel free to
contribute patches as pull requests as you see fit.

Try to be consistent with PEP 8 guidelines as far as possible and test
everything. Otherwise, your commit messages should start with a capitalized
verb for consistency. Unless your modification is completely trivial, also add
a message body to your commit.


## Credits

Thanks to Jason Orendorff on for the idea on stackoverflow. I also want to
thank @coldfix and @Moredread for contributions and feedback.

