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

    >>> class A(object):
    ...     def __init__(self, name):
    ...         self.name = name
    ...
    ...     @event
    ...     def progress(self, first, second):
    ...         print("Doing something...")

    A.progress is the event.  It is triggered after executing the code in the
    decorated progress routine.

    Now that we have a class with some event, let's create an event handler.

    >>> def handler(self, first, second):
    ...     print("%s %s and %s!" % (first, self.name, second))

    Note that the handler (and signal calls) must have the signature defined
    by the decorated event method.

    This handler only greets the object that triggered the event by using its
    name attribute.  Let's create some instances of A and register our new
    event handler to their progress event.

    >>> a = A("Foo")
    >>> b = A("Bar")
    >>> a.progress.connect(partial(handler, a))
    >>> b.progress.connect(partial(handler, b))

    Now everything has been setup.  When we call the method, the event will be
    triggered:

    >>> a.progress("Hello", "World")
    Doing something...
    Hello Foo and World!
    >>> b.progress(second="Others", first="Hi")
    Doing something...
    Hi Bar and Others!

    What happens if we disobey the call signature?

    >>> c = A("World")
    >>> c.progress(second="World")  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    TypeError: progress() missing 1 required positional argument: 'first'

    Class based access is possible as well:

    >>> A.progress(a, "Hello", "Y")
    Doing something...
    Hello Foo and Y!

    Bound methods keep the instance alive:

    >>> f = a.progress
    >>> import weakref, gc
    >>> wr = weakref.ref(a)
    >>> del a
    >>> c=gc.collect()
    >>> assert wr() is not None
    >>> f("Hi", "Z")
    Doing something...
    Hi Foo and Z!

    If we delete the hard reference to the bound method and run the garbage
    collector (to make sure it is run at all), the object will be gone:

    >>> del f
    >>> c=gc.collect()
    >>> assert wr() is None

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
                return self.__get__(instance, owner)(*args, **kwargs)
            return wrapper
        else:
            try:
                evt_handlers = getattr(instance, self.__key)
            except AttributeError:
                evt_handlers = []
                setattr(instance, self.__key, evt_handlers)
            func = partial(self.__function, instance)
            return signal(func, evt_handlers)

def signal(function, event_handlers=None):
    '''
    Signals are objects are primitive event emitter objects.

    * function -- templace function (will be executed before event handlers)
    * event_handlers -- event handler list object to use

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
    @wraps(function)
    def wrapper(*args, **kwargs):
        result = function(*args, **kwargs)
        for f in event_handlers[:]:
            f(*args, **kwargs)
        return result
    wrapper.connect = event_handlers.append
    wrapper.disconnect = event_handlers.remove
    return wrapper
