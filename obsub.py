'''
This is an implementation of the observer pattern.  It uses function
decorators to achieve the desired event registration mechanism.

For further reference, see

http://en.wikipedia.org/wiki/Observer_pattern

The idea is based on this thread:
http://stackoverflow.com/questions/1904351/python-observer-pattern-examples-tips

'''
__all__ = ['event', 'signal']
__version__ = '0.2'

import functools
from black_magic.decorator import partial, wraps


class event(object):
    '''
    This class serves as a utility to decorate a function as an event.

    The following example demonstrates its functionality in an abstract way.
    A class method can be decorated as follows:

    >>> class Earth(object):
    ...     @event
    ...     def calculate(self, question, answer=43):
    ...         """Calling this method will invoke all registered handlers."""
    ...         print("{0} = {1}".format(question, answer))

    A.progress is the event.  It is triggered after executing the code in the
    decorated progress routine.

    Now that we have a class with some event, let's create an event handler.

    >>> def vogons(question, answer):
    ...     print("destroy earth ({0}, {1})".format(question, answer))

    Note that the handler (and signal calls) must have the signature defined
    by the decorated event method.

    This handler only greets the object that triggered the event by using its
    name attribute.  Let's create some instances of A and register our new
    event handler to their progress event.

    >>> earth = Earth()
    >>> earth.calculate.connect(vogons)

    Now everything has been setup.  When we call the method, the event will be
    triggered:

    >>> earth.calculate("42+1", "42")
    42+1 = 42
    destroy earth (42+1, 42)

    What happens if we disobey the call signature?

    >>> earth2 = Earth()
    >>> earth2.calculate(answer=42)  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    TypeError: progress() missing 1 required positional argument: 'question'

    Class based access is possible as well:

    >>> earth2.calculate.connect(vogons)
    >>> Earth.calculate(earth2, "answer to everything")
    answer to everything = 43
    destroy earth (answer to everything, 43)

    And check out the help ``help(Earth)`` or ``help(earth.calculate)``, you
    won't notice a thing!

    '''
    def __init__(self, function):
        '''
        Constructor.

        * function -- The function to be wrapped by the decorator.

        '''
        # Copy docstring and other attributes from function
        functools.update_wrapper(self, function)
        # Used to enforce call signature even when no slot is connected.
        # Can also execute code (called before handlers)
        self.__function = function
        self.__key = ' ' + function.__name__

    def __get__(self, instance, owner):
        '''
        Overloaded __get__ method.  Defines the object resulting from
        a method/function decorated with @event.

        See http://docs.python.org/reference/datamodel.html?highlight=__get__#object.__get__
        for a detailed explanation of what this special method usually does.

        * instance -- The instance of event invoked.
        * owner -- The owner class.

        '''
        # this case corresponds to access via the owner class:
        if instance is None:
            @wraps(self.__function)
            def wrapper(instance, *args, **kwargs):
                return _emit(partial(self.__function, instance),
                             self.__handlers(instance),
                             *args, **kwargs)
            return wrapper
        # attribute access via instance:
        else:
            return signal(partial(self.__function, instance),
                          self.__handlers(instance))

    def __handlers(self, instance):
        try:
            return getattr(instance, self.__key)
        except AttributeError:
            handlers = []
            setattr(instance, self.__key, handlers)
            return handlers

def signal(function, event_handlers=None, _decorate=True):
    '''
    Signals are objects are primitive event emitter objects.

    * function -- templace function (will be executed before event handlers)
    * event_handlers -- event handler list object to use
    * _decorate -- whether to return a nicely decorated function object

    Calling a signal emits the event, i.e. all registered event handlers are
    called with the given arguments. Before the event handlers are called,
    the base function gets a chance to execute.

    You can use `signal` as a decorator, for example:

    >>> @signal
    ... def sig(foo="bar"):
    ...     """I'm a docstring!"""
    ...     print('In sig!')
    ...     return 'Return value.'

    >>> def handler(foo):
    ...     print("foo=%s" % foo)
    >>> sig.connect(handler)

    >>> sig()
    In sig!
    foo=bar
    'Return value.'

    >>> sig("hello")
    In sig!
    foo=hello
    'Return value.'

    '''
    if event_handlers is None:
        event_handlers = []
    def wrapper(*args, **kwargs):
        return _emit(function, event_handlers, *args, **kwargs)
    if _decorate:
        wrapper = wraps(function)(wrapper)
    wrapper.connect = event_handlers.append
    wrapper.disconnect = event_handlers.remove
    return wrapper

def _emit(function, event_handlers, *args, **kwargs):
    """Private function. Emit the specified event."""
    result = function(*args, **kwargs)
    for f in event_handlers[:]:
        f(*args, **kwargs)
    return result
