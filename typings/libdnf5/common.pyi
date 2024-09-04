"""
This type stub file was generated by pyright.
"""

if __package__ or "." in __name__:
    ...
else:
    ...

class _SwigNonDynamicMeta(type):
    """Meta class to enforce nondynamic attributes (no new attributes) for a class"""

    __setattr__ = ...

class SwigPyIterator:
    thisown = ...
    def __init__(self, *args, **kwargs) -> None: ...

    __repr__ = ...
    __swig_destroy__ = ...
    def value(self): ...
    def incr(self, n=...): ...
    def decr(self, n=...): ...
    def distance(self, x): ...
    def equal(self, x): ...
    def copy(self): ...
    def next(self): ...
    def __next__(self): ...
    def previous(self): ...
    def advance(self, n): ...
    def __eq__(self, x) -> bool: ...
    def __ne__(self, x) -> bool: ...
    def __iadd__(self, n): ...
    def __isub__(self, n): ...
    def __add__(self, n): ...
    def __sub__(self, *args): ...
    def __iter__(self):  # -> Self:
        ...

class VectorString:
    thisown = ...
    __repr__ = ...
    def iterator(self): ...
    def __iter__(self): ...
    def __nonzero__(self): ...
    def __bool__(self): ...
    def __len__(self): ...
    def __getslice__(self, i, j): ...
    def __setslice__(self, *args): ...
    def __delslice__(self, i, j): ...
    def __delitem__(self, *args): ...
    def __getitem__(self, *args): ...
    def __setitem__(self, *args): ...
    def pop(self): ...
    def append(self, x): ...
    def empty(self): ...
    def size(self): ...
    def swap(self, v): ...
    def begin(self): ...
    def end(self): ...
    def rbegin(self): ...
    def rend(self): ...
    def clear(self): ...
    def get_allocator(self): ...
    def pop_back(self): ...
    def erase(self, *args): ...
    def __init__(self, *args) -> None: ...
    def push_back(self, x): ...
    def front(self): ...
    def back(self): ...
    def assign(self, n, x): ...
    def insert(self, *args): ...
    def reserve(self, n): ...
    def capacity(self): ...

    __swig_destroy__ = ...

class SetString:
    thisown = ...
    __repr__ = ...
    def iterator(self): ...
    def __iter__(self): ...
    def __nonzero__(self): ...
    def __bool__(self): ...
    def __len__(self): ...
    def append(self, x): ...
    def __contains__(self, x): ...
    def __getitem__(self, i): ...
    def add(self, x): ...
    def discard(self, x): ...
    def __init__(self, *args) -> None: ...
    def empty(self): ...
    def size(self): ...
    def clear(self): ...
    def swap(self, v): ...
    def count(self, x): ...
    def begin(self): ...
    def end(self): ...
    def rbegin(self): ...
    def rend(self): ...
    def erase(self, *args): ...
    def find(self, x): ...
    def lower_bound(self, x): ...
    def upper_bound(self, x): ...
    def equal_range(self, x): ...
    def insert(self, __x): ...

    __swig_destroy__ = ...

class PairStringString:
    thisown = ...
    __repr__ = ...
    def __init__(self, *args) -> None: ...

    first = ...
    second = ...
    def __len__(self):  # -> Literal[2]:
        ...

    def __repr__(self):  # -> str:
        ...

    def __getitem__(self, index):  # -> Any:
        ...

    def __setitem__(self, index, val):  # -> None:
        ...
    __swig_destroy__ = ...

class VectorPairStringString:
    thisown = ...
    __repr__ = ...
    def iterator(self): ...
    def __iter__(self): ...
    def __nonzero__(self): ...
    def __bool__(self): ...
    def __len__(self): ...
    def __getslice__(self, i, j): ...
    def __setslice__(self, *args): ...
    def __delslice__(self, i, j): ...
    def __delitem__(self, *args): ...
    def __getitem__(self, *args): ...
    def __setitem__(self, *args): ...
    def pop(self): ...
    def append(self, x): ...
    def empty(self): ...
    def size(self): ...
    def swap(self, v): ...
    def begin(self): ...
    def end(self): ...
    def rbegin(self): ...
    def rend(self): ...
    def clear(self): ...
    def get_allocator(self): ...
    def pop_back(self): ...
    def erase(self, *args): ...
    def __init__(self, *args) -> None: ...
    def push_back(self, x): ...
    def front(self): ...
    def back(self): ...
    def assign(self, n, x): ...
    def insert(self, *args): ...
    def reserve(self, n): ...
    def capacity(self): ...

    __swig_destroy__ = ...

class MapStringString:
    thisown = ...
    __repr__ = ...
    def iterator(self): ...
    def __iter__(self): ...
    def __nonzero__(self): ...
    def __bool__(self): ...
    def __len__(self): ...
    def __iter__(self): ...
    def iterkeys(self): ...
    def itervalues(self): ...
    def iteritems(self): ...
    def __getitem__(self, key): ...
    def __delitem__(self, key): ...
    def has_key(self, key): ...
    def keys(self): ...
    def values(self): ...
    def items(self): ...
    def __contains__(self, key): ...
    def key_iterator(self): ...
    def value_iterator(self): ...
    def __setitem__(self, *args): ...
    def asdict(self): ...
    def __init__(self, *args) -> None: ...
    def empty(self): ...
    def size(self): ...
    def swap(self, v): ...
    def begin(self): ...
    def end(self): ...
    def rbegin(self): ...
    def rend(self): ...
    def clear(self): ...
    def get_allocator(self): ...
    def count(self, x): ...
    def erase(self, *args): ...
    def find(self, x): ...
    def lower_bound(self, x): ...
    def upper_bound(self, x): ...

    __swig_destroy__ = ...

class MapStringMapStringString:
    thisown = ...
    __repr__ = ...
    def iterator(self): ...
    def __iter__(self): ...
    def __nonzero__(self): ...
    def __bool__(self): ...
    def __len__(self): ...
    def __iter__(self): ...
    def iterkeys(self): ...
    def itervalues(self): ...
    def iteritems(self): ...
    def __getitem__(self, key): ...
    def __delitem__(self, key): ...
    def has_key(self, key): ...
    def keys(self): ...
    def values(self): ...
    def items(self): ...
    def __contains__(self, key): ...
    def key_iterator(self): ...
    def value_iterator(self): ...
    def __setitem__(self, *args): ...
    def asdict(self): ...
    def __init__(self, *args) -> None: ...
    def empty(self): ...
    def size(self): ...
    def swap(self, v): ...
    def begin(self): ...
    def end(self): ...
    def rbegin(self): ...
    def rend(self): ...
    def clear(self): ...
    def get_allocator(self): ...
    def count(self, x): ...
    def erase(self, *args): ...
    def find(self, x): ...
    def lower_bound(self, x): ...
    def upper_bound(self, x): ...

    __swig_destroy__ = ...

class MapStringPairStringString:
    thisown = ...
    __repr__ = ...
    def iterator(self): ...
    def __iter__(self): ...
    def __nonzero__(self): ...
    def __bool__(self): ...
    def __len__(self): ...
    def __iter__(self): ...
    def iterkeys(self): ...
    def itervalues(self): ...
    def iteritems(self): ...
    def __getitem__(self, key): ...
    def __delitem__(self, key): ...
    def has_key(self, key): ...
    def keys(self): ...
    def values(self): ...
    def items(self): ...
    def __contains__(self, key): ...
    def key_iterator(self): ...
    def value_iterator(self): ...
    def __setitem__(self, *args): ...
    def asdict(self): ...
    def __init__(self, *args) -> None: ...
    def empty(self): ...
    def size(self): ...
    def swap(self, v): ...
    def begin(self): ...
    def end(self): ...
    def rbegin(self): ...
    def rend(self): ...
    def clear(self): ...
    def get_allocator(self): ...
    def count(self, x): ...
    def erase(self, *args): ...
    def find(self, x): ...
    def lower_bound(self, x): ...
    def upper_bound(self, x): ...

    __swig_destroy__ = ...

class Iterator:
    def __init__(self, container, begin, end) -> None: ...
    def __iter__(self):  # -> Self:
        ...

    def __next__(self): ...

QueryCmp_NOT: int = ...
QueryCmp_ICASE: int = ...
QueryCmp_ISNULL: int = ...
QueryCmp_EQ: int = ...
QueryCmp_NEQ: int = ...
QueryCmp_GT: int = ...
QueryCmp_GTE: int = ...
QueryCmp_LT: int = ...
QueryCmp_LTE: int = ...
QueryCmp_EXACT: int = ...
QueryCmp_NOT_EXACT: int = ...
QueryCmp_IEXACT: int = ...
QueryCmp_NOT_IEXACT: int = ...
QueryCmp_CONTAINS: int = ...
QueryCmp_NOT_CONTAINS: int = ...
QueryCmp_ICONTAINS: int = ...
QueryCmp_NOT_ICONTAINS: int = ...
QueryCmp_STARTSWITH: int = ...
QueryCmp_ISTARTSWITH: int = ...
QueryCmp_ENDSWITH: int = ...
QueryCmp_IENDSWITH: int = ...
QueryCmp_REGEX: int = ...
QueryCmp_IREGEX: int = ...
QueryCmp_GLOB: int = ...
QueryCmp_NOT_GLOB: int = ...
QueryCmp_IGLOB: int = ...
QueryCmp_NOT_IGLOB: int = ...

def __sub__(lhs, rhs):
    r"""
    Returns the value of the left operand with the bits zeroed that are set in the right operand.
    Can be used eg for removing `NOT` or `ICASE` flags.
    """
    ...

def match_int64(*args): ...
def match_string(*args): ...

class PreserveOrderMapStringString:
    r"""
    PreserveOrderMap is an associative container that contains key-value pairs with unique unique keys.
    It is similar to standard std::map. But it preserves the order of items and the complexity is linear.
    """

    thisown = ...
    __repr__ = ...
    def empty(self): ...
    def size(self): ...
    def max_size(self): ...
    def reserve(self, new_capacity): ...
    def capacity(self): ...
    def shrink_to_fit(self): ...
    def begin(self, *args): ...
    def cbegin(self): ...
    def end(self, *args): ...
    def cend(self): ...
    def rbegin(self, *args): ...
    def crbegin(self): ...
    def rend(self, *args): ...
    def crend(self): ...
    def clear(self): ...
    def insert(self, value): ...
    def erase(self, *args): ...
    def count(self, key): ...
    def find(self, *args): ...
    def at(self, *args): ...
    def __contains__(self, key): ...
    def __len__(self): ...
    def __getitem__(self, key): ...
    def __setitem__(self, key, v): ...
    def __delitem__(self, key): ...
    def __iter__(self): ...
    def __init__(self) -> None: ...

    __swig_destroy__ = ...

cvar = ...
msg_err_exact_one_object = ...

class PreserveOrderMapStringPreserveOrderMapStringString:
    r"""
    PreserveOrderMap is an associative container that contains key-value pairs with unique unique keys.
    It is similar to standard std::map. But it preserves the order of items and the complexity is linear.
    """

    thisown = ...
    __repr__ = ...
    def empty(self): ...
    def size(self): ...
    def max_size(self): ...
    def reserve(self, new_capacity): ...
    def capacity(self): ...
    def shrink_to_fit(self): ...
    def begin(self, *args): ...
    def cbegin(self): ...
    def end(self, *args): ...
    def cend(self): ...
    def rbegin(self, *args): ...
    def crbegin(self): ...
    def rend(self, *args): ...
    def crend(self): ...
    def clear(self): ...
    def insert(self, value): ...
    def erase(self, *args): ...
    def count(self, key): ...
    def find(self, *args): ...
    def at(self, *args): ...
    def __contains__(self, key): ...
    def __len__(self): ...
    def __getitem__(self, key): ...
    def __setitem__(self, key, v): ...
    def __delitem__(self, key): ...
    def __iter__(self): ...
    def __init__(self) -> None: ...

    __swig_destroy__ = ...
