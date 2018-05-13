from collections import defaultdict as ddict
from itertools import chain
from typing import Iterable
from inspect import Signature, signature, isclass, isfunction, \
    _VAR_KEYWORD,_KEYWORD_ONLY,_VAR_POSITIONAL,_POSITIONAL_ONLY,_POSITIONAL_OR_KEYWORD,_empty
from typing import Any


# Custom Error for this class


def _merge_annotations(func, functions: Iterable):
    if func is not None:
        initial=getattr(func,'__annotations__')
    else:
        initial={}

    new=ddict(set)

    for f in functions:
        for k,v in getattr(f,'__annotations__',{}).items():
            if k not in initial:
                new[k].add(v)

    for k,v in new.items():
        initial[k]=tuple(v)

    return initial

# Modification of inspect.Signature._bind method to:
# >> Check against type annotations
# >> Remove return mapping (unnecessary, requires maintaining a mapping dictionary which could impact performance)
# >> Raise TypeCheckError if the arguments cannot be mapped to the parameters
