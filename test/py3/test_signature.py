'''
Test that the decorator correctly preserves the signature. Currently, this
is only possible for python3.
'''

from obsub import event

try:
    from inspect import signature
except ImportError:
    raise NotImplementedError


referenced = {}
def on_blubb(
        self:0,
        obscure:"NOTE: default argument is a by reference: "=referenced,
        *,
        with_kwonlyarg:int,
        **kwargs):
    return obscure

class A(object):
    on_blubb = event(on_blubb)


def test_signature():
    # Define a test class and an event handler
    a = A()

    # signature is preserved: (!!)
    assert signature(a.on_blubb) == signature(on_blubb)

    # NOTE: we even got the exact object as default parameter, not only an
    # exact copy:
    assert a.on_blubb(with_kwonlyarg="xyz") is referenced

