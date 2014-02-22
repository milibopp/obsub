"""
Test the core functionality.

Contains a converted version of all of the doctests.

"""
# test utilities
import unittest
import weakref, gc

# tested module
import obsub
from obsub import event


class NewStyle(object):
    def __init__(self):
        self.count = 0
    @event
    def emit(self, first, second):
        self.count += 1

class NewStyleNoDecorator(object):
    def __init__(self):
        self.count = 0
    def emit(self, first, second):
        self.count += 1

class NewStyleWithMeta(NewStyleNoDecorator):
    __metaclass__ = obsub.EventMetaclass
    _event_methods = ['emit']

class OldStyle:
    def __init__(self):
        self.count = 0
    @event
    def emit(self, first, second):
        self.count += 1

class Observer(object):
    def __init__(self, call_stack):
        self.call_stack = call_stack
    def __call__(self, source, first, second):
        diff = (sum(1 for call in self.call_stack if call[2] == source)
                - source.count) + 1
        self.call_stack.append((self, diff, source, first, second))

class TestCore(unittest.TestCase):
    """Test the obsub module for new style classes."""
    cls = NewStyle

    def setUp(self):
        self.call_stack = []
        self.maxDiff = None

    def observer(self, instance):
        observer = Observer(self.call_stack)
        instance.emit += observer
        return observer

    def check_stack(self, expected):
        self.assertEqual(expected, self.call_stack)

    def test_single_handler(self):
        """A single handler is invoked correctly."""
        src = self.cls()
        obs = self.observer(src)
        src.emit("Hello", "World")
        self.check_stack([(obs, 0, src, "Hello", "World")])

    def test_remove_handler(self):
        """Removal of event handlers works correctly."""
        src = self.cls()
        obs = self.observer(src)
        src.emit -= obs
        src.emit("something", "arbitrary")
        self.check_stack([])

    def test_multiple_handlers(self):
        """Multiple handlers are invoked in correct order."""
        src = self.cls()
        obs = [self.observer(src) for i in range(10)]
        src.emit("Hello", "World")
        self.check_stack([(obs[i], i, src, "Hello", "World")
                          for i in range(10)])

    def test_multiple_sources(self):
        """Multiple instances of the event source class can coexist."""
        src = [self.cls() for i in range(10)]
        obs = [self.observer(s) for s in src]
        for s in src:
            s.emit("Hello", "World")
        self.check_stack([(obs[i], 0, src[i], "Hello", "World")
                          for i in range(10)])

    def test_keyword_arguments(self):
        """Keyword arguments can be used."""
        src = self.cls()
        obs = self.observer(src)
        src.emit(second="World", first="Hello")
        self.check_stack([(obs, 0, src, "Hello", "World")])

    def test_wrong_signature(self):
        """Any incorrect call signature raises a TypeError."""
        src = self.cls()
        self.assertRaises(TypeError, src.emit, "Hello")
        self.assertRaises(TypeError, src.emit, first="Hello", third="!")
        self.assertRaises(TypeError, src.emit, second="World")
        obs = self.observer(src)
        self.assertRaises(TypeError, src.emit, forth=":)")
        self.check_stack([])

    def test_class_based_access(self):
        """The emitter function can be invoked via its class."""
        src = self.cls()
        obs = self.observer(src)
        self.cls.emit(src, "Hello", "World")
        self.check_stack([(obs, 0, src, "Hello", "World")])

    def test_keep_alive(self):
        """A reference to a bound event method keeps its owner instance alive."""
        src = self.cls()
        obs = self.observer(src)
        emit = src.emit

        # remove original reference:
        wr = weakref.ref(src)
        del src
        gc.collect()

        # the emitter function is still functioning:
        assert wr() is not None
        emit("Hello", "World")
        self.check_stack([(obs, 0, wr(), "Hello", "World")])

        # removing the bound method makes the instance disappear:
        del emit
        self.call_stack[0] = None
        gc.collect()
        assert wr() is None

class TestCoreMeta(TestCore):
    cls = NewStyleWithMeta

# ERRORS:
class TestCoreOldStyle(TestCore):
    cls = OldStyle

