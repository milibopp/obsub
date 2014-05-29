"""
This is an implementation of the observer pattern.  It uses function
decorators to achieve the desired event registration mechanism.

For further reference, see

http://en.wikipedia.org/wiki/Observer_pattern

The idea is based on this thread:
http://stackoverflow.com/questions/1904351/python-observer-pattern-examples-tips
"""

__all__ = ['event', 'static_event', 'SUPPORTS_DEFAULT_ARGUMENTS']
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
        wraps = functools.wraps
    else:                   # python3
        SUPPORTS_DEFAULT_ARGUMENTS = True
        def wraps(wrapped):
            """Like functools.wraps, but also preserve the signature."""
            def update_wrapper(wrapper):
                wrapper.__signature__ = signature(wrapped)
                return functools.wraps(wrapped)(wrapper)
            return update_wrapper


def _emitter_method(function):

    """Internal utility that creates an event method with connectors."""

    key = '_ obsub _' + function.__name__
    def get_handlers(instance):
        return instance.__dict__.get(key, ())

    # Wrap the event emitter function to retain docstring and signature:
    @wraps(function)
    def emit(*self__args, **kwargs):
        self = self__args[0]
        args = self__args[1:]
        result = function(self, *args, **kwargs)
        # Invoke instance-specfic handlers:
        for f in get_handlers(self)[:]:
            f(*args, **kwargs)
        # Invoke (base) class-specfic handlers:
        try:
            mro = self.__class__.__mro__
        except AttributeError:              # Old style class..
            pass
        else:
            for cls in mro:
                for f in get_handlers(cls)[:]:
                    f(self, *args, **kwargs)
        return result

    # create basic tools for managing connection/disconnection of handlers
    def make_handlers(instance):
        try:
            # Use item access to ensure we are querying an attribute that
            # is specific to this instance/class:
            return instance.__dict__[key]
        except KeyError:
            handlers = []
            # In case 'instance' is the owner class, instance.__dict__ can
            # be a read-only proxy. Therefore, we need to use setattr()
            # rather than item access:
            setattr(instance, key, handlers)
            return handlers

    def connect(instance, handler):
        """Connect an event handler."""
        make_handlers(instance).append(handler)

    def disconnect(instance, handler):
        """Disconnect an event handler."""
        make_handlers(instance).remove(handler)

    emit.connect = connect
    emit.disconnect = disconnect
    return emit


def _class_connector(owner, method):

    """Internal utility to create class based connect/disconnect functions."""

    def connector(*instance__handler):
        """
        Connect/disconnect an event handler.

        :param instance: optional
        :param handler: required

        If the instance parameter is specified, the connection will be
        managed with regard to the list of instance specific event handlers.

        Otherwise, the handler will be the list of class-specific event
        handlers is managed. Class specific connections enable to receive
        notifications from all instances of any subclass. In these events
        the instance is given as the first argument to the handler.
        """
        try:
            method(*instance__handler)
        except TypeError:
            assert hasattr(owner, '__mro__'), \
                "Class based connection requires new style classes!"
            method(owner, *instance__handler)

    connector.__name__ = method.__name__
    return connector


class event(object):

    """
    Decorator for instance events (analogous to member functions).

    The following example demonstrates its functionality.
    A class method can be decorated as follows:

    >>> class Earth(object):
    ...     @event
    ...     def calculate(self, question, answer=43):
    ...         '''Calling this method will invoke all registered handlers.'''
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
    """

    def __init__(self, function):
        """
        Create an instance event based on the member function parameter.

        * function -- The function to be wrapped by the decorator.
        """
        self.__emit = _emitter_method(function)

    def __get__(self, instance, owner):
        """
        Query event for specific to one instance or class.

        * instance -- The instance of event invoked.
        * owner -- The owner class.
        """
        orig = self.__emit
        # Copy the unbound function before setting the connector methods.
        # This is necessary since the instance method acquired later on
        # doesn't support setting attributes.
        emit = copy_function(orig)
        if instance is None:
            # access via class:
            emit.connect = _class_connector(owner, orig.connect)
            emit.disconnect = _class_connector(owner, orig.disconnect)
            return emit
        else:
            # access via instance:
            emit.connect = orig.connect.__get__(instance)
            emit.disconnect = orig.disconnect.__get__(instance)
            return emit.__get__(instance)


def static_event(function, event_handlers=None):
    """
    Decorator for static event functions.

    * function -- templace function (will be executed before event handlers)
    * event_handlers -- event handler list object to use

    Calling a static_event emits the event, i.e. all registered event
    handlers are called with the given arguments. Before the event handlers
    are called, the base function gets a chance to execute.

    You can use `static_event` as a decorator, for example:

    >>> @static_event
    ... def sig(foo="bar"):
    ...     '''I'm a docstring!'''
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
    """
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
        """Create a copy of a function instance."""
        return types.FunctionType(func.__code__, func.__globals__,
                                  func.__name__, func.__defaults__,
                                  func.__closure__)
else:
    def copy_function(func):
        """Create a copy of a function instance."""
        return types.FunctionType(func.func_code, func.func_globals,
                                  func.func_name, func.func_defaults,
                                  func.func_closure)
