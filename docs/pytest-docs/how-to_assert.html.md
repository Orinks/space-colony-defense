Contents Menu Expand Light mode Dark mode Auto light/dark, in light mode Auto light/dark, in dark mode
Hide navigation sidebar
Hide table of contents sidebar
Skip to content
Back to top
Toggle Light / Dark / Auto color theme
Toggle table of contents sidebar
# How to write and report assertions in tests¶
## Asserting with the `assert` statement¶
`pytest` allows you to use the standard Python `assert` for verifying expectations and values in Python tests. For example, you can write the following:
```
# content of test_assert1.py
def f():
  return 3

def test_function():
  assert f() == 4

```

to assert that your function returns a certain value. If this assertion fails you will see the return value of the function call:
```
$ pytest test_assert1.py
=========================== test session starts ============================
platform linux -- Python 3.x.y, pytest-8.x.y, pluggy-1.x.y
rootdir: /home/sweet/project
collected 1 item
test_assert1.py F                          [100%]
================================= FAILURES =================================
______________________________ test_function _______________________________
  def test_function():
>    assert f() == 4
E    assert 3 == 4
E    + where 3 = f()
test_assert1.py:6: AssertionError
========================= short test summary info ==========================
FAILED test_assert1.py::test_function - assert 3 == 4
============================ 1 failed in 0.12s =============================

```

`pytest` has support for showing the values of the most common subexpressions including calls, attributes, comparisons, and binary and unary operators. (See Demo of Python failure reports with pytest). This allows you to use the idiomatic python constructs without boilerplate code while not losing introspection information.
If a message is specified with the assertion like this:
```
assert a % 2 == 0, "value was odd, should be even"

```

it is printed alongside the assertion introspection in the traceback.
See Assertion introspection details for more information on assertion introspection.
## Assertions about expected exceptions¶
In order to write assertions about raised exceptions, you can use `pytest.raises()` as a context manager like this:
```
import pytest

def test_zero_division():
  with pytest.raises(ZeroDivisionError):
    1 / 0

```

and if you need to have access to the actual exception info you may use:
```
def test_recursion_depth():
  with pytest.raises(RuntimeError) as excinfo:
    def f():
      f()
    f()
  assert "maximum recursion" in str(excinfo.value)

```

`excinfo` is an `ExceptionInfo` instance, which is a wrapper around the actual exception raised. The main attributes of interest are `.type`, `.value` and `.traceback`.
Note that `pytest.raises` will match the exception type or any subclasses (like the standard `except` statement). If you want to check if a block of code is raising an exact exception type, you need to check that explicitly:
```
def test_foo_not_implemented():
  def foo():
    raise NotImplementedError
  with pytest.raises(RuntimeError) as excinfo:
    foo()
  assert excinfo.type is RuntimeError

```

The `pytest.raises()` call will succeed, even though the function raises `NotImplementedError`, because `NotImplementedError` is a subclass of `RuntimeError`; however the following `assert` statement will catch the problem.
### Matching exception messages¶
You can pass a `match` keyword parameter to the context-manager to test that a regular expression matches on the string representation of an exception (similar to the `TestCase.assertRaisesRegex` method from `unittest`):
```
import pytest

def myfunc():
  raise ValueError("Exception 123 raised")

def test_match():
  with pytest.raises(ValueError, match=r".* 123 .*"):
    myfunc()

```

Notes:
  * The `match` parameter is matched with the `re.search()` function, so in the above example `match='123'` would have worked as well.
  * The `match` parameter also matches against PEP-678 `__notes__`.


### Matching exception groups¶
You can also use the `excinfo.group_contains()` method to test for exceptions returned as part of an `ExceptionGroup`:
```
def test_exception_in_group():
  with pytest.raises(ExceptionGroup) as excinfo:
    raise ExceptionGroup(
      "Group message",
      [
        RuntimeError("Exception 123 raised"),
      ],
    )
  assert excinfo.group_contains(RuntimeError, match=r".* 123 .*")
  assert not excinfo.group_contains(TypeError)

```

The optional `match` keyword parameter works the same way as for `pytest.raises()`.
By default `group_contains()` will recursively search for a matching exception at any level of nested `ExceptionGroup` instances. You can specify a `depth` keyword parameter if you only want to match an exception at a specific level; exceptions contained directly in the top `ExceptionGroup` would match `depth=1`.
```
def test_exception_in_group_at_given_depth():
  with pytest.raises(ExceptionGroup) as excinfo:
    raise ExceptionGroup(
      "Group message",
      [
        RuntimeError(),
        ExceptionGroup(
          "Nested group",
          [
            TypeError(),
          ],
        ),
      ],
    )
  assert excinfo.group_contains(RuntimeError, depth=1)
  assert excinfo.group_contains(TypeError, depth=2)
  assert not excinfo.group_contains(RuntimeError, depth=2)
  assert not excinfo.group_contains(TypeError, depth=1)

```

### Alternate form (legacy)¶
There is an alternate form where you pass a function that will be executed, along `*args` and `**kwargs`, and `pytest.raises()` will execute the function with the arguments and assert that the given exception is raised:
```
def func(x):
  if x <= 0:
    raise ValueError("x needs to be larger than zero")

pytest.raises(ValueError, func, x=-1)

```

The reporter will provide you with helpful output in case of failures such as _no exception_ or _wrong exception_.
This form was the original `pytest.raises()` API, developed before the `with` statement was added to the Python language. Nowadays, this form is rarely used, with the context-manager form (using `with`) being considered more readable. Nonetheless, this form is fully supported and not deprecated in any way.
### xfail mark and pytest.raises¶
It is also possible to specify a `raises` argument to pytest.mark.xfail, which checks that the test is failing in a more specific way than just having any exception raised:
```
def f():
  raise IndexError()

@pytest.mark.xfail(raises=IndexError)
def test_f():
  f()

```

This will only “xfail” if the test fails by raising `IndexError` or subclasses.
  * Using pytest.mark.xfail with the `raises` parameter is probably better for something like documenting unfixed bugs (where the test describes what “should” happen) or bugs in dependencies.
  * Using `pytest.raises()` is likely to be better for cases where you are testing exceptions your own code is deliberately raising, which is the majority of cases.


## Assertions about expected warnings¶
You can check that code raises a particular warning using pytest.warns.
## Making use of context-sensitive comparisons¶
`pytest` has rich support for providing context-sensitive information when it encounters comparisons. For example:
```
# content of test_assert2.py
def test_set_comparison():
  set1 = set("1308")
  set2 = set("8035")
  assert set1 == set2

```

if you run this module:
```
$ pytest test_assert2.py
=========================== test session starts ============================
platform linux -- Python 3.x.y, pytest-8.x.y, pluggy-1.x.y
rootdir: /home/sweet/project
collected 1 item
test_assert2.py F                          [100%]
================================= FAILURES =================================
___________________________ test_set_comparison ____________________________
  def test_set_comparison():
    set1 = set("1308")
    set2 = set("8035")
>    assert set1 == set2
E    AssertionError: assert {'0', '1', '3', '8'} == {'0', '3', '5', '8'}
E
E     Extra items in the left set:
E     '1'
E     Extra items in the right set:
E     '5'
E     Use -v to get more diff
test_assert2.py:4: AssertionError
========================= short test summary info ==========================
FAILED test_assert2.py::test_set_comparison - AssertionError: assert {'0'...
============================ 1 failed in 0.12s =============================

```

Special comparisons are done for a number of cases:
  * comparing long strings: a context diff is shown
  * comparing long sequences: first failing indices
  * comparing dicts: different entries


See the reporting demo for many more examples.
## Defining your own explanation for failed assertions¶
It is possible to add your own detailed explanations by implementing the `pytest_assertrepr_compare` hook.
pytest_assertrepr_compare(_config_ , _op_ , _left_ , _right_)[source]
    
Return explanation for comparisons in failing assert expressions.
Return None for no custom explanation, otherwise return a list of strings. The strings will be joined by newlines but any newlines _in_ a string will be escaped. Note that all but the first line will be indented slightly, the intention is for the first line to be a summary.
Parameters:
    
  * **config** (_Config_) – The pytest config object.
  * **op** (_str_) – The operator, e.g. `"=="`, `"!="`, `"not in"`.
  * **left** (_object_) – The left operand.
  * **right** (_object_) – The right operand.


### Use in conftest plugins¶
Any conftest file can implement this hook. For a given item, only conftest files in the item’s directory and its parent directories are consulted.
As an example consider adding the following hook in a conftest.py file which provides an alternative explanation for `Foo` objects:
```
# content of conftest.py
from test_foocompare import Foo

def pytest_assertrepr_compare(op, left, right):
  if isinstance(left, Foo) and isinstance(right, Foo) and op == "==":
    return [
      "Comparing Foo instances:",
      f"  vals: {left.val} != {right.val}",
    ]

```

now, given this test module:
```
# content of test_foocompare.py
class Foo:
  def __init__(self, val):
    self.val = val
  def __eq__(self, other):
    return self.val == other.val

def test_compare():
  f1 = Foo(1)
  f2 = Foo(2)
  assert f1 == f2

```

you can run the test module and get the custom output defined in the conftest file:
```
$ pytest -q test_foocompare.py
F                                  [100%]
================================= FAILURES =================================
_______________________________ test_compare _______________________________
  def test_compare():
    f1 = Foo(1)
    f2 = Foo(2)
>    assert f1 == f2
E    assert Comparing Foo instances:
E      vals: 1 != 2
test_foocompare.py:12: AssertionError
========================= short test summary info ==========================
FAILED test_foocompare.py::test_compare - assert Comparing Foo instances:
1 failed in 0.12s

```

## Assertion introspection details¶
Reporting details about a failing assertion is achieved by rewriting assert statements before they are run. Rewritten assert statements put introspection information into the assertion failure message. `pytest` only rewrites test modules directly discovered by its test collection process, so **asserts in supporting modules which are not themselves test modules will not be rewritten**.
You can manually enable assertion rewriting for an imported module by calling register_assert_rewrite before you import it (a good place to do that is in your root `conftest.py`).
For further information, Benjamin Peterson wrote up Behind the scenes of pytest’s new assertion rewriting.
### Assertion rewriting caches files on disk¶
`pytest` will write back the rewritten modules to disk for caching. You can disable this behavior (for example to avoid leaving stale `.pyc` files around in projects that move files around a lot) by adding this to the top of your `conftest.py` file:
```
import sys
sys.dont_write_bytecode = True

```

Note that you still get the benefits of assertion introspection, the only change is that the `.pyc` files won’t be cached on disk.
Additionally, rewriting will silently skip caching if it cannot write new `.pyc` files, i.e. in a read-only filesystem or a zipfile.
### Disabling assert rewriting¶
`pytest` rewrites test modules on import by using an import hook to write new `pyc` files. Most of the time this works transparently. However, if you are working with the import machinery yourself, the import hook may interfere.
If this is the case you have two options:
  * Disable rewriting for a specific module by adding the string `PYTEST_DONT_REWRITE` to its docstring.
  * Disable rewriting for all modules by using `--assert=plain`.


