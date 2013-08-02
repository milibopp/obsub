'''
These tests that the event handling mechanism does not produce memory leaks.
This could in principle happen, since it introduces a cyclic dependency that
might prevent garbage collection.
'''

import weakref

from event import event


def test_memory_leak():

    # Define a test class and an event handler
    class A(object):
        @event
        def on_blubb():
            pass

    def handler(self):
        pass

    # Instantiate and attach event handler
    a = A()
    a.on_blubb += handler

    # Weak reference for testing
    wr = weakref.ref(a)

    # At first, weak reference exists but after deletion it should be dead
    assert wr() is not None
    del a
    assert wr() is None

