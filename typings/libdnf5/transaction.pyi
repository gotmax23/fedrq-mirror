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

TransactionItemAction_INSTALL = ...
TransactionItemAction_UPGRADE = ...
TransactionItemAction_DOWNGRADE = ...
TransactionItemAction_REINSTALL = ...
TransactionItemAction_REMOVE = ...
TransactionItemAction_REPLACED = ...
TransactionItemAction_REASON_CHANGE = ...
TransactionItemAction_ENABLE = ...
TransactionItemAction_DISABLE = ...
TransactionItemAction_RESET = ...

class InvalidTransactionItemAction:
    thisown = ...
    __repr__ = ...
    def __init__(self, action) -> None: ...
    def get_domain_name(self): ...
    def get_name(self): ...

    __swig_destroy__ = ...

def transaction_item_action_to_string(action): ...
def transaction_item_action_from_string(action): ...
def transaction_item_action_to_letter(action): ...
def transaction_item_action_is_inbound(action): ...
def transaction_item_action_is_outbound(action): ...

TransactionItemReason_NONE = ...
TransactionItemReason_DEPENDENCY = ...
TransactionItemReason_USER = ...
TransactionItemReason_CLEAN = ...
TransactionItemReason_WEAK_DEPENDENCY = ...
TransactionItemReason_GROUP = ...
TransactionItemReason_EXTERNAL_USER = ...

class InvalidTransactionItemReason:
    thisown = ...
    __repr__ = ...
    def __init__(self, reason) -> None: ...
    def get_domain_name(self): ...
    def get_name(self): ...

    __swig_destroy__ = ...

def transaction_item_reason_to_string(reason): ...
def transaction_item_reason_from_string(reason): ...
def transaction_item_reason_compare(lhs, rhs):
    r"""
    Compare transaction items and return:
    -1 if lhs < rhs
    1 if lhs > rhs
    0 if lhs == rhs
    Higher number means a better (or a stronger) reason.
    """
    ...

def __lt__(lhs, rhs) -> bool: ...
def __le__(lhs, rhs) -> bool: ...
def __gt__(lhs, rhs) -> bool: ...
def __ge__(lhs, rhs) -> bool: ...

TransactionItemState_STARTED = ...
TransactionItemState_OK = ...
TransactionItemState_ERROR = ...

class InvalidTransactionItemState:
    thisown = ...
    __repr__ = ...
    def __init__(self, state) -> None: ...
    def get_domain_name(self): ...
    def get_name(self): ...

    __swig_destroy__ = ...

def transaction_item_state_to_string(state): ...
def transaction_item_state_from_string(state): ...

class TransactionItem:
    thisown = ...
    def __init__(self, *args, **kwargs) -> None: ...

    __repr__ = ...
    def get_action(self):
        r"""Get action associated with the transaction item in the transaction"""
        ...

    def get_reason(self):
        r"""Get reason of the action associated with the transaction item in the transaction"""
        ...

    def get_repoid(self):
        r"""Get transaction item repoid (text identifier of a repository)"""
        ...

    def get_state(self):
        r"""Get transaction item state"""
        ...
    __swig_destroy__ = ...

class CompsGroup(TransactionItem):
    r"""
    CompsGroup contains a copy of important data from comps::CompsGroup that is used
    to perform comps transaction and then stored in the transaction (history) database.
    """

    thisown = ...
    def __init__(self, *args, **kwargs) -> None: ...

    __repr__ = ...
    def to_string(self):
        r"""Get string representation of the object, which equals to group_id"""
        ...
    __swig_destroy__ = ...

class CompsGroupPackage:
    r"""CompsGroupPackage represents a package associated with a comps group"""

    thisown = ...
    __repr__ = ...
    def __init__(self) -> None: ...

    __swig_destroy__ = ...

class CompsEnvironment(TransactionItem):
    r"""
    CompsEnvironment contains a copy of important data from comps::CompsEnvironment that is used
    to perform comps transaction and then stored in the transaction (history) database.
    """

    thisown = ...
    def __init__(self, *args, **kwargs) -> None: ...

    __repr__ = ...
    def to_string(self):
        r"""Get string representation of the object, which equals to environment_id"""
        ...
    __swig_destroy__ = ...

class CompsEnvironmentGroup:
    thisown = ...
    __repr__ = ...
    def __init__(self) -> None: ...

    __swig_destroy__ = ...

class Package(TransactionItem):
    r"""
    Package contains a copy of important data from rpm::Package that is used
    to perform rpm transaction and then stored in the transaction (history) database.
    """

    thisown = ...
    def __init__(self, *args, **kwargs) -> None: ...

    __repr__ = ...
    def get_name(self):
        r"""Get package name"""
        ...

    def get_epoch(self):
        r"""Get package epoch"""
        ...

    def get_release(self):
        r"""Get package release"""
        ...

    def get_arch(self):
        r"""Get package arch"""
        ...

    def get_version(self):
        r"""Get package version"""
        ...

    def to_string(self):
        r"""Get string representation of the object, which equals to package NEVRA"""
        ...
    __swig_destroy__ = ...

class TransactionHistory:
    r"""A class for working with transactions recorded in the transaction history database."""

    thisown = ...
    __repr__ = ...
    def __init__(self, *args) -> None: ...
    def get_weak_ptr(self): ...
    def list_transaction_ids(self):
        r"""
        Lists all transaction IDs from the transaction history database. The
        result is sorted in ascending order.

        :rtype: std::vector< int64_t,std::allocator< int64_t > >
        :return: The list of transaction IDs.
        """
        ...

    def list_transactions(self, *args):
        r"""
        *Overload 1:*
        Lists transactions from the transaction history for transaction ids in `ids`.

        :type ids: std::vector< int64_t,std::allocator< int64_t > >
        :param ids: The ids to list.
        :rtype: std::vector< libdnf5::transaction::Transaction,std::allocator< libdnf5::transaction::Transaction > >
        :return: The listed transactions.

        |

        *Overload 2:*
        Lists transactions from the transaction history for transaction ids
        within the [start, end] range (inclusive).

        :type start: int
        :param start: The first id of the range to be listed.
        :type end: int
        :param end: The last id of the range to be listed.
        :rtype: std::vector< libdnf5::transaction::Transaction,std::allocator< libdnf5::transaction::Transaction > >
        :return: The listed transactions.
        """
        ...

    def list_all_transactions(self):
        r"""
        Lists all transactions from the transaction history.

        :rtype: std::vector< libdnf5::transaction::Transaction,std::allocator< libdnf5::transaction::Transaction > >
        :return: The listed transactions.
        """
        ...

    def get_base(self):
        r"""
        :rtype: libdnf5::BaseWeakPtr
        :return: The `Base` object to which this object belongs.
        Since: 5.0
        """
        ...
    __swig_destroy__ = ...

class TransactionHistoryWeakPtr:
    r"""
    WeakPtr is a "smart" pointer. It contains a pointer to resource and to guard of resource.
    WeakPtr pointer can be owner of the resource. However, the resource itself may depend on another resource.
    WeakPtr registers/unregisters itself at the guard of resource. And the resource guard invalidates
    the registered WeakPtrs when the resource is unusable (eg. its dependecny was released).
    Note on thread safety:
    It is safe to create, access and destroy WeakPtrs in multiple threads simultaneously.
    """

    thisown = ...
    __repr__ = ...
    def __init__(self, *args) -> None: ...

    __swig_destroy__ = ...
    def __deref__(self):
        r"""Provides access to the managed object. Generates exception if object is not valid."""
        ...

    def get(self):
        r"""Returns a pointer to the managed object. Generates exception if object is not valid."""
        ...

    def is_valid(self):
        r"""Checks if managed object is valid."""
        ...

    def has_same_guard(self, other):
        r"""Checks if the other WeakPtr instance has the same WeakPtrGuard."""
        ...

    def __ref__(self): ...
    def __eq__(self, other) -> bool: ...
    def __ne__(self, other) -> bool: ...
    def __lt__(self, other) -> bool: ...
    def __gt__(self, other) -> bool: ...
    def __le__(self, other) -> bool: ...
    def __ge__(self, other) -> bool: ...
    def __hash__(self) -> int: ...
    def get_weak_ptr(self): ...
    def list_transaction_ids(self):
        r"""
        Lists all transaction IDs from the transaction history database. The
        result is sorted in ascending order.

        :rtype: std::vector< int64_t,std::allocator< int64_t > >
        :return: The list of transaction IDs.
        """
        ...

    def list_transactions(self, *args):
        r"""
        *Overload 1:*
        Lists transactions from the transaction history for transaction ids in `ids`.

        :type ids: std::vector< int64_t,std::allocator< int64_t > >
        :param ids: The ids to list.
        :rtype: std::vector< libdnf5::transaction::Transaction,std::allocator< libdnf5::transaction::Transaction > >
        :return: The listed transactions.

        |

        *Overload 2:*
        Lists transactions from the transaction history for transaction ids
        within the [start, end] range (inclusive).

        :type start: int
        :param start: The first id of the range to be listed.
        :type end: int
        :param end: The last id of the range to be listed.
        :rtype: std::vector< libdnf5::transaction::Transaction,std::allocator< libdnf5::transaction::Transaction > >
        :return: The listed transactions.
        """
        ...

    def list_all_transactions(self):
        r"""
        Lists all transactions from the transaction history.

        :rtype: std::vector< libdnf5::transaction::Transaction,std::allocator< libdnf5::transaction::Transaction > >
        :return: The listed transactions.
        """
        ...

    def get_base(self):
        r"""
        :rtype: libdnf5::BaseWeakPtr
        :return: The `Base` object to which this object belongs.
        Since: 5.0
        """
        ...

TransactionState_STARTED = ...
TransactionState_OK = ...
TransactionState_ERROR = ...

def transaction_state_to_string(state): ...
def transaction_state_from_string(state): ...

class InvalidTransactionState:
    thisown = ...
    __repr__ = ...
    def __init__(self, state) -> None: ...
    def get_domain_name(self): ...
    def get_name(self): ...

    __swig_destroy__ = ...

class Transaction:
    r"""
    Transaction holds information about a transaction.
    It contains transaction items such as packages, comps groups and environments.
    Transaction object are used to retrieve information about past transactions
    from the transaction history database as well as for performing a transaction
    to change packages on disk.
    """

    thisown = ...
    def __init__(self, *args, **kwargs) -> None: ...

    __repr__ = ...
    __swig_destroy__ = ...
    def __eq__(self, other) -> bool: ...
    def __lt__(self, other) -> bool: ...
    def __gt__(self, other) -> bool: ...
    def get_id(self):
        r"""
        Get Transaction database id (primary key)
        Return 0 if the id wasn't set yet
        """
        ...

    def get_dt_start(self):
        r"""Get date and time of the transaction start"""
        ...

    def get_dt_end(self):
        r"""Get date and time of the transaction end"""
        ...

    def get_rpmdb_version_begin(self):
        r"""
        Get RPM database version before the transaction
        Format: `<rpm_count>`:`<sha1 of sorted SHA1HEADER fields of installed RPMs>`
        """
        ...

    def get_rpmdb_version_end(self):
        r"""
        Get RPM database version after the transaction
        Format: `<rpm_count>`:`<sha1 of sorted SHA1HEADER fields of installed RPMs>`
        """
        ...

    def get_releasever(self):
        r"""Get $releasever variable value that was used during the transaction"""
        ...

    def get_user_id(self):
        r"""Get UID of a user that started the transaction"""
        ...

    def get_description(self):
        r"""Get the description of the transaction (e.g. the CLI command that was executed)"""
        ...

    def get_comment(self):
        r"""Get a user-specified comment describing the transaction"""
        ...

    def get_state(self):
        r"""Get transaction state"""
        ...

    def get_comps_environments(self):
        r"""Return all comps environments associated with the transaction"""
        ...

    def get_comps_groups(self):
        r"""Return all comps groups associated with the transaction"""
        ...

    def get_packages(self):
        r"""Return all rpm packages associated with the transaction"""
        ...

    def serialize(self):
        r"""
        Warning: This method is experimental/unstable and should not be relied on. It may be removed without warning
        Serialize the transaction into a json data format which can be later loaded
        into a `libdnf5::Goal` and replayed.
        """
        ...

class VectorTransaction:
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

class VectorTransactionPackage:
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
