from typing import Union, Callable
from operator import *
from engine.util.dunder import Dunder

BINARY_NUMERIC_OPERATORS = [
    add,
    and_,
    floordiv,
    ge,
    gt,
    iadd,
    iand,
    ifloordiv,
    ilshift,
    imatmul,
    imod,
    imul,
    ior,
    ipow,
    irshift,
    isub,
    itruediv,
    ixor,
    le,
    lshift,
    lt,
    matmul,
    mod,
    mul,
    ne,
    neg,
    or_,
    pos,
    pow,
    rshift,
    sub,
    truediv,
    xor
]

class BinaryNumericOverload:
    def __init_subclass__(parent, **kwargs):
        super().__init_subclass__(**kwargs)
        for operator in BINARY_NUMERIC_OPERATORS:
            name = operator.__name__
            dunder = Dunder(name)
            parent_operator = parent.create_operator(operator, dunder.is_augmented)
            setattr(parent, dunder.name, parent_operator)

    @staticmethod
    def create_operator(operator, is_augmented):
        def operator_method(self, other):
            return self.__operation__(other, operator, is_augmented)
        return operator_method
