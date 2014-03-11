'''
This is an implementation of the observer pattern.  It uses function
decorators to achieve the desired event registration mechanism.

For further reference, see

http://en.wikipedia.org/wiki/Observer_pattern

The idea is based on this thread:
http://stackoverflow.com/questions/1904351/python-observer-pattern-examples-tips

'''
__all__ = ['event', 'signal', 'SUPPORTS_DEFAULT_ARGUMENTS']
__version__ = '0.2'

import sys
import types
try:
    from black_magic.decorator import wraps
    SUPPORTS_DEFAULT_ARGUMENTS = True
except ImportError:
    import functools
    try:
        from inspect import signature
    except ImportError:     # python2
        SUPPORTS_DEFAULT_ARGUMENTS = False
        def wraps(wrapped):
            def update_wrapper(wrapper):
                return functools.wraps(wrapped)(wrapper)
            return update_wrapper
    else:                   # python3
        SUPPORTS_DEFAULT_ARGUMENTS = True
        def wraps(wrapped):
            def update_wrapper(wrapper):
                wrapper.__signature__ = signature(wapped)
                return functools.wraps(wrapped)(wrapper)
            return update_wrapper

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
    ...     print("destroy earth ({0})".format(question))

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
    destroy earth (42+1)

    What happens if we disobey the call signature?

    >>> earth2 = Earth()
    >>> earth2.calculate(answer=42)  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    TypeError: progress() missing 1 required positional argument: 'question'

    Class based access is possible as well:

    >>> Earth.calculate.connect(earth2, vogons)
    >>> Earth.calculate(earth2, "answer to everything", 42)
    answer to everything = 42
    destroy earth (answer to everything)

    On python3 (and on python2 if you have black-magic installed) default
    arguments work as expected:

    >>> if SUPPORTS_DEFAULT_ARGUMENTS:
    ...     earth2.calculate('the real answer')
    ... else:   # default arguments not supported, so let's cheat...
    ...     earth2.calculate('the real answer', 43)
    the real answer = 43
    destroy earth (the real answer)

    And check out the help ``help(Earth)`` or ``help(earth.calculate)``, you
    won't notice a thing (at least if you have black-magic installed).

    '''
    def __init__(self, function):
        '''
        Constructor.

        * function -- The function to be wrapped by the decorator.

        '''
        key = ' ' + function.__name__
        def handlers(instance):
            try:
                return getattr(instance, key)
            except AttributeError:
                handlers = []
                setattr(instance, key, handlers)
                return handlers
        @wraps(function)
        def emit(instance, *args, **kwargs):
            result = function(instance, *args, **kwargs)
            for f in handlers(instance)[:]:
                f(*args, **kwargs)
            return result
        def connect(instance, handler):
            handlers(instance).append(handler)
        def disconnect(instance, handler):
            handlers(instance).remove(handler)
        emit.connect = connect
        emit.disconnect = disconnect
        self.__function = emit

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
            return self.__function
        # attribute access via instance:
        else:
            # Copy the unbound function before setting the connector
            # methods. This is necessary since the instance method acquired
            # later on doesn't support setting attributes.
            orig = self.__function
            copy = copy_function(orig)
            copy.connect = orig.connect.__get__(instance)
            copy.disconnect = orig.disconnect.__get__(instance)
            return copy.__get__(instance)

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

    >>> if SUPPORTS_DEFAULT_ARGUMENTS:
    ...     sig()
    ... else:
    ...     sig('bar')
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
    @wraps(function)
    def wrapper(*args, **kwargs):
        result = function(*args, **kwargs)
        for f in event_handlers[:]:
            f(*args, **kwargs)
        return result
    wrapper.connect = event_handlers.append
    wrapper.disconnect = event_handlers.remove
    return wrapper

if sys.version_info >= (3,0):
    def copy_function(func):
        return types.FunctionType(func.__code__, func.__globals__,
                                  func.__name__, func.__defaults__,
                                  func.__closure__)
else:
    def copy_function(func):
        return types.FunctionType(func.func_code, func.func_globals,
                                  func.func_name, func.func_defaults,
                                  func.func_closure)
