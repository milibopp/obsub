'''
This is an implementation of the observer pattern.  It uses function
decorators to achieve the desired event registration mechanism.

For further reference, see

http://en.wikipedia.org/wiki/Observer_pattern

The idea is based on this thread:
http://stackoverflow.com/questions/1904351/python-observer-pattern-examples-tips

'''

import weakref


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

    '''

    def __init__(self, function):
        '''
        Constructor.

        * function -- the function

        '''
        # Copy docstring from function
        self.__doc__ = function.__doc__
        # Use its name as key
        self._key = ' ' + function.__name__
        # Used to enforce call signature even when no slot is connected.
        # Can also execute code (called before handlers)
        self._function = function

    def __get__(self, instance, owner):
        '''
        Overloaded __get__ method.  Defines the object resulting from
        a method/function decorated with @event.

        See http://docs.python.org/reference/datamodel.html?highlight=__get__#object.__get__
        for a detailed explanation of what this special method usually does.

        * instance -- The instance of event invoked.
        * owner -- The owner class.

        '''
        try:
            # Try to return the dictionary entry corresponding to the key.
            return instance.__dict__[self._key]
        except KeyError:
            # On the first try this raises a KeyError,
            # The error is caught to write the new entry into the instance dictionary.
            # The new entry is an instance of boundevent, which exhibits the event behaviour.
            be = instance.__dict__[self._key] = boundevent(instance, self._function)
            return be


class boundevent(object):
    '''
    Private helper class for event system.
    '''

    def __init__(self, instance, function):
        '''
        Constructor.

        * instance -- the instance whose member the event is

        '''
        # Create empty list of registered event handlers.
        self.__event_handlers = []
        self.__instance = weakref.ref(instance)
        self.__function = function

    @property
    def instance(self):
        return self.__instance()

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
        # Create a hard ref to the instance to make sure it survives
        # througout this function call
        instance = self.instance
        # Enforce signature and possibly execute entry code. This makes sure
        # any inconsistent call will be caught immediately, independent of
        # connected handlers.
        result = self.__function(instance, *args, **kwargs)
        # Call all registered event handlers
        for f in self.__event_handlers[:]:
            f(instance, *args, **kwargs)
        return result

# Execute the doctests if run from the command line.
# Verbose tests: python event.py -v
if __name__ == "__main__":
    import doctest
    doctest.testmod()
