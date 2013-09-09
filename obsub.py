'''
This is an implementation of the observer pattern.  It uses function
decorators to achieve the desired event registration mechanism.

For further reference, see

http://en.wikipedia.org/wiki/Observer_pattern

The idea is based on this thread:
http://stackoverflow.com/questions/1904351/python-observer-pattern-examples-tips

'''

import functools


__all__ = ['event']


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
    >>> a.progress += handler
    >>> b.progress += handler

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
    >>> from weakref import ref
    >>> wr = ref(a)
    >>> assert wr() is not None
    >>> del a
    >>> assert wr() is not None
    >>> f("Hi", "Z")
    Doing something...
    Hi Foo and Z!
    >>> del f
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

    def __set__(self, instance, value):
        '''
        This is a NOP preventing that a boundevent instance is stored.

        This prevents  operations like  `a.progress += handler`  to have
        side effects that result in a cyclic reference.

        http://stackoverflow.com/questions/18287336/memory-leak-when-invoking-iadd-via-get-without-using-temporary

        '''
        pass

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
            @functools.wraps(self.__function)
            def wrapper(instance, *args, **kwargs):
                return self.__get__(instance, owner)(*args, **kwargs)
            return wrapper
        else:
            return functools.wraps(self.__function)(boundevent(instance, self.__function))


class boundevent(object):
    '''Private helper class for event system.'''

    def __init__(self, instance, function):
        '''
        Constructor.

        * instance -- the instance whose member the event is

        '''
        self.instance = instance
        self.__function = function
        self.__key = function.__name__

    @property
    def __event_handlers(self):
        if self.__key not in self.instance.__dict__:
            self.instance.__dict__[self.__key] = []
        return self.instance.__dict__[self.__key]

    def __iadd__(self, function):
        '''
        Overloaded += operator.  It registers event handlers to the event.

        * function -- The right-hand-side argument of the operator; this is the
            event handling function that registers to the event.

        '''
        # Add the function as a new event handler
        self.__event_handlers.append(function)
        # Return the boundevent instance itself for coherent syntax behaviour
        return self

    def __isub__(self, function):
        '''
        Overloaded -= operator.  It removes registered event handlers from
        the event.

        * function -- The right-hand-side argument of the operator; this is the
            function that needs to be removed from the list of event handlers.

        '''
        # Remove the function from the list of registered event handlers
        self.__event_handlers.remove(function)
        # Return the boundevent instance itself for coherent syntax behaviour
        return self

    def __call__(self, *args, **kwargs):
        '''
        Overloaded call method; it defines the behaviour of boundevent().
        When the event is called, all registered event handlers are called.

        * *args -- Arguments given to the event handlers.
        * **kwargs -- Keyword arguments given to the event handlers.

        '''
        # Enforce signature and possibly execute entry code. This makes sure
        # any inconsistent call will be caught immediately, independent of
        # connected handlers.
        result = self.__function(self.instance, *args, **kwargs)
        # Call all registered event handlers
        for f in self.__event_handlers[:]:
            f(self.instance, *args, **kwargs)
        return result

