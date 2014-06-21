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


def _invoke_all(handlers, args, kwargs):
    """
    Internal utility to invoke all handlers in a list.

    Unlike ``map(fn, list)`` this applies one set of arguments to a list of
    functions rather than multiple arguments to a single function.
    """
    for f in handlers[:]:
        f(*args, **kwargs)


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
        _invoke_all(get_handlers(self), args, kwargs)
        # Invoke (base) class-specfic handlers:
        try:
            mro = self.__class__.__mro__
        except AttributeError:              # Old style class..
            pass
        else:
            for cls in mro:
                _invoke_all(get_handlers(cls), self__args, kwargs)
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
    emit.__func__ = function
    return emit


class _event_method_proxy(object):

    """Abstract base class for bound/unbound method proxies."""

    def __init__(self, function, instance):
        """Create a method proxy from a function and an instance/class."""
        self.function = function
        self._instance = instance

    def connect(self, handler):
        """Connect an event handler."""
        self.function.connect(self._instance, handler)

    def disconnect(self, handler):
        """Connect an event handler."""
        self.function.disconnect(self._instance, handler)

    def __eq__(self, other):
        """Compare equality."""
        try:
            return (self.function == other.function and
                    self._instance is other._instance)
        except AttributeError:
            return False

    @property
    def __func__(self):
        """The function behind this proxy."""
        return self.function

    def __get__(self, instance, owner=None):
        """
        Query event for specific to one instance or class.

        * instance -- The instance of event invoked.
        * owner -- The owner class.
        """
        if instance is None:
            return unbound_event(self.__func__, owner)
        else:
            return bound_event(self.__func__, instance)


class bound_event(_event_method_proxy):

    """Method proxy for events bound to an instance."""

    @property
    def __self__(self):
        """The instance that this proxy is attached to."""
        return self._instance

    def __call__(*self__args, **kwargs):
        """Invoke ```function(self.__self__, *args, **kwargs).``."""
        self = self__args[0]
        args = self__args[1:]
        return self.function(self._instance, *args, **kwargs)


class unbound_event(_event_method_proxy):

    """Method proxy for events bound not bound to an instance."""

    def __call__(*self__args, **kwargs):
        """Invoke ```self.function(*args, **kwargs).``."""
        self = self__args[0]
        args = self__args[1:]
        # instance must be given in *args:
        return self.function(*args, **kwargs)


class event(object):

    """
    Decorator for instance events (analogous to member functions).

    The basic usage should be easy to grasp:


    Define an instance specific event inside a class
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    >>> from obsub import event

    >>> class Earth(object):
    ...     @event
    ...     def calculate(self, answer=43):
    ...         print("Answer is: {0}".format(answer))

    >>> earth = Earth()


    Connect an event handler
    ~~~~~~~~~~~~~~~~~~~~~~~~

    >>> def vogons(answer):
    ...     print("{0} vogons destroy earth".format(answer))
    >>> earth.calculate.connect(vogons)


    Trigger the event
    ~~~~~~~~~~~~~~~~~

    >>> earth.calculate(42)
    Answer is: 42
    42 vogons destroy earth


    Disconnect an event handler
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    >>> earth.calculate.disconnect(vogons)


    Class based access
    ~~~~~~~~~~~~~~~~~~

    The function name in the class can be used to invoke events like you
    would expect from normal member functions:

    >>> earth.calculate.connect(vogons)
    >>> Earth.calculate(earth, "less than 44")
    Answer is: less than 44
    less than 44 vogons destroy earth


    Class-specific connections
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    If connecting via the class attribute, you can leave the instance
    argument to obtain a class-wide subscription:

    >>> def UN(instance, answer):
    ...     print("do nothing")

    >>> Earth.calculate.connect(UN)

    >>> earth2 = Earth()
    >>> earth2.calculate("correct")
    Answer is: correct
    do nothing


    Disobey the call signature?
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    >>> earth2.calculate(question=42)  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    TypeError: calculate() got an unexpected keyword argument 'question'


    Default arguments
    ~~~~~~~~~~~~~~~~~

    On python3 (and on python2 if you have black-magic installed) default
    arguments work as expected:

    >>> if SUPPORTS_DEFAULT_ARGUMENTS:
    ...     earth2.calculate()
    ... else:   # let's cheat for the sake of this doctest:
    ...     earth2.calculate(43)
    Answer is: 43
    do nothing


    Help
    ~~~~

    And check out the help ``help(Earth)`` or ``help(earth.calculate)``, you
    won't notice a thing (at least if you have black-magic installed).
    """

    def __init__(self, function):
        """
        Create an instance event based on the member function parameter.

        * function -- The function to be wrapped by the decorator.
        """
        self.__emit = _event_method_proxy(_emitter_method(function), None)

    def __get__(self, instance, owner):
        """
        Query event for specific to one instance or class.

        * instance -- The instance of event invoked.
        * owner -- The owner class.
        """
        return self.__emit.__get__(instance, owner)


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
        _invoke_all(event_handlers, args, kwargs)
        return result
    wrapper.connect = event_handlers.append
    wrapper.disconnect = event_handlers.remove
    return wrapper
