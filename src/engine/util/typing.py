from typing import Union, Literal
from decimal import Decimal

Zero = Literal[0]
Number = Union[int, float, Decimal]
Array = Union[list, tuple]
Object = object

def decimalize(n: Number) -> Decimal:
    return Decimal(str(n))
