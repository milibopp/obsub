'''
These tests that the event handling mechanism does not produce memory leaks.
This could in principle happen, since it introduces a cyclic dependency that
might prevent garbage collection.

'''

import weakref
import gc
import functools

from obsub import event


def test_memory_leak():

    # Define a test class and an event handler
    class A(object):
        @event
        def on_blubb(self):
            pass

    def handler():
        pass

    # Instantiate and attach event handler
    a = A()
    a.on_blubb.connect(handler)

    # Weak reference for testing
    wr = weakref.ref(a)

    # At first, weak reference exists
    assert wr() is not None

    # (implicitly) delete the A-instance by reassigning the only hard-ref.
    # This is equivalent to `del a` but serves the purpose to demonstrate
    # that there are very subtle ways to delete an instance:
    a = None

    # Trigger the garbage collection manually
    gc.collect()

    # after deletion it should be dead
    assert wr() is None


def test_object_stays_alive_during_handler_execution():

    # Define a test class and event handlers
    class A(object):
        @event
        def on_blubb(self):
            pass
        deleted = False

    class B(object):
        def __init__(self, a):
            # capture the only hard-ref on the A-instance:
            self.a = a
            self.a.on_blubb.connect(self.handler)

        def handler(self):
            # delete the A-instance
            self.a.deleted = True
            del self.a
            gc.collect()

    def handler(wr):
        # We want a valid reference to the handled object, ...
        a = wr()
        assert a is not None
        # ..., even if the deletion handler has already been called:
        assert a.deleted

    # Instantiate and attach event handler
    b = B(A())

    wr = weakref.ref(b.a)
    b.a.on_blubb.connect(functools.partial(handler, wr))

    b.a.on_blubb()

    # Trigger the garbage collection manually
    gc.collect()

    # make sure, b.a has been deleted after event handling
    assert wr() is None
