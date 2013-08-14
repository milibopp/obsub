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
    ...     def progress(self):
    ...         pass
    ...
    ...     def do_something(self):
    ...         print("Doing something...")
    ...         self.progress()

    A.progress is the event.  It is triggered within the method A.do_something.
    Now that we have a class with some event, let's create an event handler.

    >>> def handler(self):
    ...     print("Hello %s!" % self.name)

    This handler only greets the object that triggered the event by using its
    name attribute.  Let's create some instances of A and register our new
    event handler to their progress event.

    >>> a = A("Foo")
    >>> b = A("Bar")
    >>> a.progress += handler
    >>> b.progress += handler

    Now everything has been setup.  When we call the method, the event will be
    triggered:

    >>> a.do_something()
    Doing something...
    Hello Foo!
    >>> b.do_something()
    Doing something...
    Hello Bar!

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
            be = instance.__dict__[self._key] = boundevent(instance)
            return be


class boundevent(object):
    '''
    Private helper class for event system.
    '''

    def __init__(self, instance):
        '''
        Constructor.

        * instance -- the instance whose member the event is

        '''
        # Create empty list of registered event handlers.
        self.__event_handlers = []
        self.__instance = weakref.ref(instance)

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
        # Call all registered event handlers
        for f in self.__event_handlers[:]:
            f(instance, *args, **kwargs)

