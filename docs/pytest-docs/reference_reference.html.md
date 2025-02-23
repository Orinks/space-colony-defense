Contents Menu Expand Light mode Dark mode Auto light/dark, in light mode Auto light/dark, in dark mode
Hide navigation sidebar
Hide table of contents sidebar
Skip to content
Back to top
Toggle Light / Dark / Auto color theme
Toggle table of contents sidebar
# API Reference¶
This page contains the full reference to pytest’s API.
## Constants¶
### pytest.__version__¶
The current pytest version, as a string:
```
>>> import pytest
>>> pytest.__version__
'7.0.0'

```

### pytest.version_tuple¶
Added in version 7.0.
The current pytest version, as a tuple:
```
>>> import pytest
>>> pytest.version_tuple
(7, 0, 0)

```

For pre-releases, the last component will be a string with the prerelease version:
```
>>> import pytest
>>> pytest.version_tuple
(7, 0, '0rc1')

```

## Functions¶
### pytest.approx¶
approx(_expected_ , _rel =None_, _abs =None_, _nan_ok =False_)[source]¶
    
Assert that two numbers (or two ordered sequences of numbers) are equal to each other within some tolerance.
Due to the Floating-Point Arithmetic: Issues and Limitations, numbers that we would intuitively expect to be equal are not always so:
```
>>> 0.1 + 0.2 == 0.3
False

```

This problem is commonly encountered when writing tests, e.g. when making sure that floating-point values are what you expect them to be. One way to deal with this problem is to assert that two floating-point numbers are equal to within some appropriate tolerance:
```
>>> abs((0.1 + 0.2) - 0.3) < 1e-6
True

```

However, comparisons like this are tedious to write and difficult to understand. Furthermore, absolute comparisons like the one above are usually discouraged because there’s no tolerance that works well for all situations. `1e-6` is good for numbers around `1`, but too small for very big numbers and too big for very small ones. It’s better to express the tolerance as a fraction of the expected value, but relative comparisons like that are even more difficult to write correctly and concisely.
The `approx` class performs floating-point comparisons using a syntax that’s as intuitive as possible:
```
>>> from pytest import approx
>>> 0.1 + 0.2 == approx(0.3)
True

```

The same syntax also works for ordered sequences of numbers:
```
>>> (0.1 + 0.2, 0.2 + 0.4) == approx((0.3, 0.6))
True

```

`numpy` arrays:
```
>>> import numpy as np                             
>>> np.array([0.1, 0.2]) + np.array([0.2, 0.4]) == approx(np.array([0.3, 0.6])) 
True

```

And for a `numpy` array against a scalar:
```
>>> import numpy as np                     
>>> np.array([0.1, 0.2]) + np.array([0.2, 0.1]) == approx(0.3) 
True

```

Only ordered sequences are supported, because `approx` needs to infer the relative position of the sequences without ambiguity. This means `sets` and other unordered sequences are not supported.
Finally, dictionary _values_ can also be compared:
```
>>> {'a': 0.1 + 0.2, 'b': 0.2 + 0.4} == approx({'a': 0.3, 'b': 0.6})
True

```

The comparison will be true if both mappings have the same keys and their respective values match the expected tolerances.
**Tolerances**
By default, `approx` considers numbers within a relative tolerance of `1e-6` (i.e. one part in a million) of its expected value to be equal. This treatment would lead to surprising results if the expected value was `0.0`, because nothing but `0.0` itself is relatively close to `0.0`. To handle this case less surprisingly, `approx` also considers numbers within an absolute tolerance of `1e-12` of its expected value to be equal. Infinity and NaN are special cases. Infinity is only considered equal to itself, regardless of the relative tolerance. NaN is not considered equal to anything by default, but you can make it be equal to itself by setting the `nan_ok` argument to True. (This is meant to facilitate comparing arrays that use NaN to mean “no data”.)
Both the relative and absolute tolerances can be changed by passing arguments to the `approx` constructor:
```
>>> 1.0001 == approx(1)
False
>>> 1.0001 == approx(1, rel=1e-3)
True
>>> 1.0001 == approx(1, abs=1e-3)
True

```

If you specify `abs` but not `rel`, the comparison will not consider the relative tolerance at all. In other words, two numbers that are within the default relative tolerance of `1e-6` will still be considered unequal if they exceed the specified absolute tolerance. If you specify both `abs` and `rel`, the numbers will be considered equal if either tolerance is met:
```
>>> 1 + 1e-8 == approx(1)
True
>>> 1 + 1e-8 == approx(1, abs=1e-12)
False
>>> 1 + 1e-8 == approx(1, rel=1e-6, abs=1e-12)
True

```

You can also use `approx` to compare nonnumeric types, or dicts and sequences containing nonnumeric types, in which case it falls back to strict equality. This can be useful for comparing dicts and sequences that can contain optional values:
```
>>> {"required": 1.0000005, "optional": None} == approx({"required": 1, "optional": None})
True
>>> [None, 1.0000005] == approx([None,1])
True
>>> ["foo", 1.0000005] == approx([None,1])
False

```

If you’re thinking about using `approx`, then you might want to know how it compares to other good ways of comparing floating-point numbers. All of these algorithms are based on relative and absolute tolerances and should agree for the most part, but they do have meaningful differences:
  * `math.isclose(a, b, rel_tol=1e-9, abs_tol=0.0)`: True if the relative tolerance is met w.r.t. either `a` or `b` or if the absolute tolerance is met. Because the relative tolerance is calculated w.r.t. both `a` and `b`, this test is symmetric (i.e. neither `a` nor `b` is a “reference value”). You have to specify an absolute tolerance if you want to compare to `0.0` because there is no tolerance by default. More information: `math.isclose()`.
  * `numpy.isclose(a, b, rtol=1e-5, atol=1e-8)`: True if the difference between `a` and `b` is less that the sum of the relative tolerance w.r.t. `b` and the absolute tolerance. Because the relative tolerance is only calculated w.r.t. `b`, this test is asymmetric and you can think of `b` as the reference value. Support for comparing sequences is provided by `numpy.allclose()`. More information: numpy.isclose.
  * `unittest.TestCase.assertAlmostEqual(a, b)`: True if `a` and `b` are within an absolute tolerance of `1e-7`. No relative tolerance is considered , so this function is not appropriate for very large or very small numbers. Also, it’s only available in subclasses of `unittest.TestCase` and it’s ugly because it doesn’t follow PEP8. More information: `unittest.TestCase.assertAlmostEqual()`.
  * `a == pytest.approx(b, rel=1e-6, abs=1e-12)`: True if the relative tolerance is met w.r.t. `b` or if the absolute tolerance is met. Because the relative tolerance is only calculated w.r.t. `b`, this test is asymmetric and you can think of `b` as the reference value. In the special case that you explicitly specify an absolute tolerance but not a relative tolerance, only the absolute tolerance is considered.


Note
`approx` can handle numpy arrays, but we recommend the specialised test helpers in Test support (numpy.testing) if you need support for comparisons, NaNs, or ULP-based tolerances.
To match strings using regex, you can use Matches from the re_assert package.
Warning
Changed in version 3.2.
In order to avoid inconsistent behavior, `TypeError` is raised for `>`, `>=`, `<` and `<=` comparisons. The example below illustrates the problem:
```
assert approx(0.1) > 0.1 + 1e-10 # calls approx(0.1).__gt__(0.1 + 1e-10)
assert 0.1 + 1e-10 > approx(0.1) # calls approx(0.1).__lt__(0.1 + 1e-10)

```

In the second example one expects `approx(0.1).__le__(0.1 + 1e-10)` to be called. But instead, `approx(0.1).__lt__(0.1 + 1e-10)` is used to comparison. This is because the call hierarchy of rich comparisons follows a fixed behavior. More information: `object.__ge__()`
Changed in version 3.7.1: `approx` raises `TypeError` when it encounters a dict value or sequence element of nonnumeric type.
Changed in version 6.1.0: `approx` falls back to strict equality for nonnumeric types instead of raising `TypeError`.
### pytest.fail¶
**Tutorial** : How to use skip and xfail to deal with tests that cannot succeed
fail(_reason_[, _pytrace=True_])[source]¶
    
Explicitly fail an executing test with the given message.
Parameters:
    
  * **reason** (_str_) – The message to show the user as reason for the failure.
  * **pytrace** (_bool_) – If False, msg represents the full failure information and no python traceback will be reported.


Raises:
    
**pytest.fail.Exception** – The exception that is raised.
_class_ pytest.fail.Exception¶
    
The exception raised by `pytest.fail()`.
### pytest.skip¶
skip(_reason_[, _allow_module_level=False_])[source]¶
    
Skip an executing test with the given message.
This function should be called only during testing (setup, call or teardown) or during collection by using the `allow_module_level` flag. This function can be called in doctests as well.
Parameters:
    
  * **reason** (_str_) – The message to show the user as reason for the skip.
  * **allow_module_level** (_bool_) – 
Allows this function to be called at module level. Raising the skip exception at module level will stop the execution of the module and prevent the collection of all tests in the module, even those defined before the `skip` call.
Defaults to False.


Raises:
    
**pytest.skip.Exception** – The exception that is raised.
Note
It is better to use the pytest.mark.skipif marker when possible to declare a test to be skipped under certain conditions like mismatching platforms or dependencies. Similarly, use the `# doctest: +SKIP` directive (see `doctest.SKIP`) to skip a doctest statically.
_class_ pytest.skip.Exception¶
    
The exception raised by `pytest.skip()`.
### pytest.importorskip¶
importorskip(_modname_ , _minversion =None_, _reason =None_, _*_ , _exc_type =None_)[source]¶
    
Import and return the requested module `modname`, or skip the current test if the module cannot be imported.
Parameters:
    
  * **modname** (_str_) – The name of the module to import.
  * **minversion** (_str_ _|__None_) – If given, the imported module’s `__version__` attribute must be at least this minimal version, otherwise the test is still skipped.
  * **reason** (_str_ _|__None_) – If given, this reason is shown as the message when the module cannot be imported.
  * **exc_type** (_type_ _[__ImportError_ _]__|__None_) – 
The exception that should be captured in order to skip modules. Must be `ImportError` or a subclass.
If the module can be imported but raises `ImportError`, pytest will issue a warning to the user, as often users expect the module not to be found (which would raise `ModuleNotFoundError` instead).
This warning can be suppressed by passing `exc_type=ImportError` explicitly.
See pytest.importorskip default behavior regarding ImportError for details.


Returns:
    
The imported module. This should be assigned to its canonical name.
Raises:
    
**pytest.skip.Exception** – If the module cannot be imported.
Return type:
    
_Any_
Example:
```
docutils = pytest.importorskip("docutils")

```

Added in version 8.2: The `exc_type` parameter.
### pytest.xfail¶
xfail(_reason =''_)[source]¶
    
Imperatively xfail an executing test or setup function with the given reason.
This function should be called only during testing (setup, call or teardown).
No other code is executed after using `xfail()` (it is implemented internally by raising an exception).
Parameters:
    
**reason** (_str_) – The message to show the user as reason for the xfail.
Note
It is better to use the pytest.mark.xfail marker when possible to declare a test to be xfailed under certain conditions like known bugs or missing features.
Raises:
    
**pytest.xfail.Exception** – The exception that is raised.
_class_ pytest.xfail.Exception¶
    
The exception raised by `pytest.xfail()`.
### pytest.exit¶
exit(_reason_[, _returncode=None_])[source]¶
    
Exit testing process.
Parameters:
    
  * **reason** (_str_) – The message to show as the reason for exiting pytest. reason has a default value only because `msg` is deprecated.
  * **returncode** (_int_ _|__None_) – Return code to be used when exiting pytest. None means the same as `0` (no error), same as `sys.exit()`.


Raises:
    
**pytest.exit.Exception** – The exception that is raised.
_class_ pytest.exit.Exception¶
    
The exception raised by `pytest.exit()`.
### pytest.main¶
**Tutorial** : Calling pytest from Python code
main(_args =None_, _plugins =None_)[source]¶
    
Perform an in-process test run.
Parameters:
    
  * **args** (_list_ _[__str_ _]__|__PathLike_ _[__str_ _]__|__None_) – List of command line arguments. If `None` or not given, defaults to reading arguments directly from the process command line (`sys.argv`).
  * **plugins** (_Sequence_ _[__str_ _|__object_ _]__|__None_) – List of plugin objects to be auto-registered during initialization.


Returns:
    
An exit code.
Return type:
    
int | _ExitCode_
### pytest.param¶
param(_*values_[, _id_][, _marks_])[source]¶
    
Specify a parameter in pytest.mark.parametrize calls or parametrized fixtures.
```
@pytest.mark.parametrize(
  "test_input,expected",
  [
    ("3+5", 8),
    pytest.param("6*9", 42, marks=pytest.mark.xfail),
  ],
)
def test_eval(test_input, expected):
  assert eval(test_input) == expected

```

Parameters:
    
  * **values** (_object_) – Variable args of the values of the parameter set, in order.
  * **marks** (_MarkDecorator_ _|__Collection_ _[__MarkDecorator_ _|__Mark_ _]_) – A single mark or a list of marks to be applied to this parameter set.
  * **id** (_str_ _|__None_) – The id to attribute to this parameter set.


### pytest.raises¶
**Tutorial** : Assertions about expected exceptions
_with _raises(_expected_exception :type[E]|tuple[type[E],...]_, _*_ , _match :str|Pattern[str]|None=..._) → RaisesContext[E]_as excinfo_[source]¶
_with _raises(_expected_exception :type[E]|tuple[type[E],...]_, _func :Callable[[...],Any]_, _* args:Any_, _** kwargs:Any_) → ExceptionInfo[E]_as excinfo_
    
Assert that a code block/function call raises an exception type, or one of its subclasses.
Parameters:
    
  * **expected_exception** – The expected exception type, or a tuple if one of multiple possible exception types are expected. Note that subclasses of the passed exceptions will also match.
  * **match** (_str_ _|__re.Pattern_ _[__str_ _]__|__None_) – 
If specified, a string containing a regular expression, or a regular expression object, that is tested against the string representation of the exception and its **PEP 678** `__notes__` using `re.search()`.
To match a literal string that may contain special characters, the pattern can first be escaped with `re.escape()`.
(This is only used when `pytest.raises` is used as a context manager, and passed through to the function otherwise. When using `pytest.raises` as a function, you can use: `pytest.raises(Exc, func, match="passed on").match("my pattern")`.)


Use `pytest.raises` as a context manager, which will capture the exception of the given type, or any of its subclasses:
```
>>> import pytest
>>> with pytest.raises(ZeroDivisionError):
...   1/0

```

If the code block does not raise the expected exception (`ZeroDivisionError` in the example above), or no exception at all, the check will fail instead.
You can also use the keyword argument `match` to assert that the exception matches a text or regex:
```
>>> with pytest.raises(ValueError, match='must be 0 or None'):
...   raise ValueError("value must be 0 or None")
>>> with pytest.raises(ValueError, match=r'must be \d+$'):
...   raise ValueError("value must be 42")

```

The `match` argument searches the formatted exception string, which includes any PEP-678 `__notes__`:
```
>>> with pytest.raises(ValueError, match=r"had a note added"): 
...   e = ValueError("value must be 42")
...   e.add_note("had a note added")
...   raise e

```

The context manager produces an `ExceptionInfo` object which can be used to inspect the details of the captured exception:
```
>>> with pytest.raises(ValueError) as exc_info:
...   raise ValueError("value must be 42")
>>> assert exc_info.type is ValueError
>>> assert exc_info.value.args[0] == "value must be 42"

```

Warning
Given that `pytest.raises` matches subclasses, be wary of using it to match `Exception` like this:
```
with pytest.raises(Exception): # Careful, this will catch ANY exception raised.
  some_function()

```

Because `Exception` is the base class of almost all exceptions, it is easy for this to hide real bugs, where the user wrote this expecting a specific exception, but some other exception is being raised due to a bug introduced during a refactoring.
Avoid using `pytest.raises` to catch `Exception` unless certain that you really want to catch **any** exception raised.
Note
When using `pytest.raises` as a context manager, it’s worthwhile to note that normal context manager rules apply and that the exception raised _must_ be the final line in the scope of the context manager. Lines of code after that, within the scope of the context manager will not be executed. For example:
```
>>> value = 15
>>> with pytest.raises(ValueError) as exc_info:
...   if value > 10:
...     raise ValueError("value must be <= 10")
...   assert exc_info.type is ValueError # This will not execute.

```

Instead, the following approach must be taken (note the difference in scope):
```
>>> with pytest.raises(ValueError) as exc_info:
...   if value > 10:
...     raise ValueError("value must be <= 10")
...
>>> assert exc_info.type is ValueError

```

**Using with** `pytest.mark.parametrize`
When using pytest.mark.parametrize it is possible to parametrize tests such that some runs raise an exception and others do not.
See Parametrizing conditional raising for an example.
See also
Assertions about expected exceptions for more examples and detailed discussion.
**Legacy form**
It is possible to specify a callable by passing a to-be-called lambda:
```
>>> raises(ZeroDivisionError, lambda: 1/0)
<ExceptionInfo ...>

```

or you can specify an arbitrary callable with arguments:
```
>>> def f(x): return 1/x
...
>>> raises(ZeroDivisionError, f, 0)
<ExceptionInfo ...>
>>> raises(ZeroDivisionError, f, x=0)
<ExceptionInfo ...>

```

The form above is fully supported but discouraged for new code because the context manager form is regarded as more readable and less error-prone.
Note
Similar to caught exception objects in Python, explicitly clearing local references to returned `ExceptionInfo` objects can help the Python interpreter speed up its garbage collection.
Clearing those references breaks a reference cycle (`ExceptionInfo` –> caught exception –> frame stack raising the exception –> current frame stack –> local variables –> `ExceptionInfo`) which makes Python keep all objects referenced from that cycle (including all local variables in the current frame) alive until the next cyclic garbage collection run. More detailed information can be found in the official Python documentation for the try statement.
### pytest.deprecated_call¶
**Tutorial** : Ensuring code triggers a deprecation warning
_with _deprecated_call(_*_ , _match :str|Pattern[str]|None=..._) → WarningsRecorder[source]¶
_with _deprecated_call(_func :Callable[[...],T]_, _* args:Any_, _** kwargs:Any_) → T
    
Assert that code produces a `DeprecationWarning` or `PendingDeprecationWarning` or `FutureWarning`.
This function can be used as a context manager:
```
>>> import warnings
>>> def api_call_v2():
...   warnings.warn('use v3 of this api', DeprecationWarning)
...   return 200
>>> import pytest
>>> with pytest.deprecated_call():
...   assert api_call_v2() == 200

```

It can also be used by passing a function and `*args` and `**kwargs`, in which case it will ensure calling `func(*args, **kwargs)` produces one of the warnings types above. The return value is the return value of the function.
In the context manager form you may use the keyword argument `match` to assert that the warning matches a text or regex.
The context manager produces a list of `warnings.WarningMessage` objects, one for each warning raised.
### pytest.register_assert_rewrite¶
**Tutorial** : Assertion Rewriting
register_assert_rewrite(_* names_)[source]¶
    
Register one or more module names to be rewritten on import.
This function will make sure that this module or all modules inside the package will get their assert statements rewritten. Thus you should make sure to call this before the module is actually imported, usually in your __init__.py if you are a plugin using a package.
Parameters:
    
**names** (_str_) – The module names to register.
### pytest.warns¶
**Tutorial** : Asserting warnings with the warns function
_with _warns(_expected_warning: type[Warning] | tuple[type[Warning], ...] = <class 'Warning'>, *, match: str | ~typing.Pattern[str] | None = None_) → WarningsChecker[source]¶
_with _warns(_expected_warning :type[Warning]|tuple[type[Warning],...]_, _func :Callable[[...],T]_, _* args:Any_, _** kwargs:Any_) → T
    
Assert that code raises a particular class of warning.
Specifically, the parameter `expected_warning` can be a warning class or tuple of warning classes, and the code inside the `with` block must issue at least one warning of that class or classes.
This helper produces a list of `warnings.WarningMessage` objects, one for each warning emitted (regardless of whether it is an `expected_warning` or not). Since pytest 8.0, unmatched warnings are also re-emitted when the context closes.
This function can be used as a context manager:
```
>>> import pytest
>>> with pytest.warns(RuntimeWarning):
...   warnings.warn("my warning", RuntimeWarning)

```

In the context manager form you may use the keyword argument `match` to assert that the warning matches a text or regex:
```
>>> with pytest.warns(UserWarning, match='must be 0 or None'):
...   warnings.warn("value must be 0 or None", UserWarning)
>>> with pytest.warns(UserWarning, match=r'must be \d+$'):
...   warnings.warn("value must be 42", UserWarning)
>>> with pytest.warns(UserWarning): # catch re-emitted warning
...   with pytest.warns(UserWarning, match=r'must be \d+$'):
...     warnings.warn("this is not here", UserWarning)
Traceback (most recent call last):
...
Failed: DID NOT WARN. No warnings of type ...UserWarning... were emitted...

```

**Using with** `pytest.mark.parametrize`
When using pytest.mark.parametrize it is possible to parametrize tests such that some runs raise a warning and others do not.
This could be achieved in the same way as with exceptions, see Parametrizing conditional raising for an example.
### pytest.freeze_includes¶
**Tutorial** : Freezing pytest
freeze_includes()[source]¶
    
Return a list of module names used by pytest that should be included by cx_freeze.
## Marks¶
Marks can be used to apply metadata to _test functions_ (but not fixtures), which can then be accessed by fixtures or plugins.
### pytest.mark.filterwarnings¶
**Tutorial** : @pytest.mark.filterwarnings
Add warning filters to marked test items.
pytest.mark.filterwarnings(_filter_)¶
    
Parameters:
    
**filter** (_str_) – 
A _warning specification string_ , which is composed of contents of the tuple `(action, message, category, module, lineno)` as specified in The Warnings Filter section of the Python documentation, separated by `":"`. Optional fields can be omitted. Module names passed for filtering are not regex-escaped.
For example:
```
@pytest.mark.filterwarnings("ignore:.*usage will be deprecated.*:DeprecationWarning")
def test_foo(): ...

```

### pytest.mark.parametrize¶
**Tutorial** : How to parametrize fixtures and test functions
This mark has the same signature as `pytest.Metafunc.parametrize()`; see there.
### pytest.mark.skip¶
**Tutorial** : Skipping test functions
Unconditionally skip a test function.
pytest.mark.skip(_reason =None_)¶
    
Parameters:
    
**reason** (_str_) – Reason why the test function is being skipped.
### pytest.mark.skipif¶
**Tutorial** : Skipping test functions
Skip a test function if a condition is `True`.
pytest.mark.skipif(_condition_ , _*_ , _reason =None_)¶
    
Parameters:
    
  * **condition** (_bool_ _or_ _str_) – `True/False` if the condition should be skipped or a condition string.
  * **reason** (_str_) – Reason why the test function is being skipped.


### pytest.mark.usefixtures¶
**Tutorial** : Use fixtures in classes and modules with usefixtures
Mark a test function as using the given fixture names.
pytest.mark.usefixtures(_* names_)¶
    
Parameters:
    
**args** – The names of the fixture to use, as strings.
Note
When using `usefixtures` in hooks, it can only load fixtures when applied to a test function before test setup (for example in the `pytest_collection_modifyitems` hook).
Also note that this mark has no effect when applied to **fixtures**.
### pytest.mark.xfail¶
**Tutorial** : XFail: mark test functions as expected to fail
Marks a test function as _expected to fail_.
pytest.mark.xfail(_condition =False_, _*_ , _reason =None_, _raises =None_, _run =True_, _strict =xfail_strict_)¶
    
Parameters:
    
  * **condition** (_Union_ _[__bool_ _,__str_ _]_) – Condition for marking the test function as xfail (`True/False` or a condition string). If a `bool`, you also have to specify `reason` (see condition string).
  * **reason** (_str_) – Reason why the test function is marked as xfail.
  * **raises** (Type[`Exception`]) – Exception class (or tuple of classes) expected to be raised by the test function; other exceptions will fail the test. Note that subclasses of the classes passed will also result in a match (similar to how the `except` statement works).
  * **run** (_bool_) – Whether the test function should actually be executed. If `False`, the function will always xfail and will not be executed (useful if a function is segfaulting).
  * **strict** (_bool_) – 
    * If `False` the function will be shown in the terminal output as `xfailed` if it fails and as `xpass` if it passes. In both cases this will not cause the test suite to fail as a whole. This is particularly useful to mark _flaky_ tests (tests that fail at random) to be tackled later.
    * If `True`, the function will be shown in the terminal output as `xfailed` if it fails, but if it unexpectedly passes then it will **fail** the test suite. This is particularly useful to mark functions that are always failing and there should be a clear indication if they unexpectedly start to pass (for example a new release of a library fixes a known bug).
Defaults to `xfail_strict`, which is `False` by default.


### Custom marks¶
Marks are created dynamically using the factory object `pytest.mark` and applied as a decorator.
For example:
```
@pytest.mark.timeout(10, "slow", method="thread")
def test_function(): ...

```

Will create and attach a `Mark` object to the collected `Item`, which can then be accessed by fixtures or hooks with `Node.iter_markers`. The `mark` object will have the following attributes:
```
mark.args == (10, "slow")
mark.kwargs == {"method": "thread"}

```

Example for using multiple custom markers:
```
@pytest.mark.timeout(10, "slow", method="thread")
@pytest.mark.slow
def test_function(): ...

```

When `Node.iter_markers` or `Node.iter_markers_with_node` is used with multiple markers, the marker closest to the function will be iterated over first. The above example will result in `@pytest.mark.slow` followed by `@pytest.mark.timeout(...)`.
## Fixtures¶
**Tutorial** : Fixtures reference
Fixtures are requested by test functions or other fixtures by declaring them as argument names.
Example of a test requiring a fixture:
```
def test_output(capsys):
  print("hello")
  out, err = capsys.readouterr()
  assert out == "hello\n"

```

Example of a fixture requiring another fixture:
```
@pytest.fixture
def db_session(tmp_path):
  fn = tmp_path / "db.file"
  return connect(fn)

```

For more details, consult the full fixtures docs.
### @pytest.fixture¶
@fixture(_fixture_function :FixtureFunction_, _*_ , _scope :Literal['session','package','module','class','function']|Callable[[str,Config],Literal['session','package','module','class','function']]='function'_, _params :Iterable[object]|None=None_, _autouse :bool=False_, _ids :Sequence[object|None]|Callable[[Any],object|None]|None=None_, _name :str|None=None_) → FixtureFunction[source]¶
@fixture(_fixture_function :None=None_, _*_ , _scope :Literal['session','package','module','class','function']|Callable[[str,Config],Literal['session','package','module','class','function']]='function'_, _params :Iterable[object]|None=None_, _autouse :bool=False_, _ids :Sequence[object|None]|Callable[[Any],object|None]|None=None_, _name :str|None=None_) → FixtureFunctionMarker
    
Decorator to mark a fixture factory function.
This decorator can be used, with or without parameters, to define a fixture function.
The name of the fixture function can later be referenced to cause its invocation ahead of running tests: test modules or classes can use the `pytest.mark.usefixtures(fixturename)` marker.
Test functions can directly use fixture names as input arguments in which case the fixture instance returned from the fixture function will be injected.
Fixtures can provide their values to test functions using `return` or `yield` statements. When using `yield` the code block after the `yield` statement is executed as teardown code regardless of the test outcome, and must yield exactly once.
Parameters:
    
  * **scope** – 
The scope for which this fixture is shared; one of `"function"` (default), `"class"`, `"module"`, `"package"` or `"session"`.
This parameter may also be a callable which receives `(fixture_name, config)` as parameters, and must return a `str` with one of the values mentioned above.
See Dynamic scope in the docs for more information.
  * **params** – An optional list of parameters which will cause multiple invocations of the fixture function and all of the tests using it. The current parameter is available in `request.param`.
  * **autouse** – If True, the fixture func is activated for all tests that can see it. If False (the default), an explicit reference is needed to activate the fixture.
  * **ids** – Sequence of ids each corresponding to the params so that they are part of the test id. If no ids are provided they will be generated automatically from the params.
  * **name** – The name of the fixture. This defaults to the name of the decorated function. If a fixture is used in the same module in which it is defined, the function name of the fixture will be shadowed by the function arg that requests the fixture; one way to resolve this is to name the decorated function `fixture_<fixturename>` and then use `@pytest.fixture(name='<fixturename>')`.


### capfd¶
**Tutorial** : How to capture stdout/stderr output
capfd()[source]¶
    
Enable text capturing of writes to file descriptors `1` and `2`.
The captured output is made available via `capfd.readouterr()` method calls, which return a `(out, err)` namedtuple. `out` and `err` will be `text` objects.
Returns an instance of `CaptureFixture[str]`.
Example:
```
def test_system_echo(capfd):
  os.system('echo "hello"')
  captured = capfd.readouterr()
  assert captured.out == "hello\n"

```

### capfdbinary¶
**Tutorial** : How to capture stdout/stderr output
capfdbinary()[source]¶
    
Enable bytes capturing of writes to file descriptors `1` and `2`.
The captured output is made available via `capfd.readouterr()` method calls, which return a `(out, err)` namedtuple. `out` and `err` will be `byte` objects.
Returns an instance of `CaptureFixture[bytes]`.
Example:
```
def test_system_echo(capfdbinary):
  os.system('echo "hello"')
  captured = capfdbinary.readouterr()
  assert captured.out == b"hello\n"

```

### caplog¶
**Tutorial** : How to manage logging
caplog()[source]¶
    
Access and control log capturing.
Captured logs are available through the following properties/methods:
```
* caplog.messages    -> list of format-interpolated log messages
* caplog.text      -> string containing formatted log output
* caplog.records     -> list of logging.LogRecord instances
* caplog.record_tuples  -> list of (logger_name, level, message) tuples
* caplog.clear()     -> clear captured records and formatted log output string

```

Returns a `pytest.LogCaptureFixture` instance.
_final class_LogCaptureFixture[source]¶
    
Provides access and control of log capturing.
_property_ handler _: LogCaptureHandler_¶
    
Get the logging handler used by the fixture.
get_records(_when_)[source]¶
    
Get the logging records for one of the possible test phases.
Parameters:
    
**when** (_Literal_ _[__'setup'__,__'call'__,__'teardown'__]_) – Which test phase to obtain the records from. Valid values are: “setup”, “call” and “teardown”.
Returns:
    
The list of captured records at the given stage.
Return type:
    
list[_LogRecord_]
Added in version 3.4.
_property_ text _: str_¶
    
The formatted log text.
_property_ records _: list[LogRecord]_¶
    
The list of log records.
_property_ record_tuples _: list[tuple[str,int,str]]_¶
    
A list of a stripped down version of log records intended for use in assertion comparison.
The format of the tuple is:
> (logger_name, log_level, message)
_property_ messages _: list[str]_¶
    
A list of format-interpolated log messages.
Unlike ‘records’, which contains the format string and parameters for interpolation, log messages in this list are all interpolated.
Unlike ‘text’, which contains the output from the handler, log messages in this list are unadorned with levels, timestamps, etc, making exact comparisons more reliable.
Note that traceback or stack info (from `logging.exception()` or the `exc_info` or `stack_info` arguments to the logging functions) is not included, as this is added by the formatter in the handler.
Added in version 3.7.
clear()[source]¶
    
Reset the list of log records and the captured log text.
set_level(_level_ , _logger =None_)[source]¶
    
Set the threshold level of a logger for the duration of a test.
Logging messages which are less severe than this level will not be captured.
Changed in version 3.4: The levels of the loggers changed by this function will be restored to their initial values at the end of the test.
Will enable the requested logging level if it was disabled via `logging.disable()`.
Parameters:
    
  * **level** (_int_ _|__str_) – The level.
  * **logger** (_str_ _|__None_) – The logger to update. If not given, the root logger.


_with _at_level(_level_ , _logger =None_)[source]¶
    
Context manager that sets the level for capturing of logs. After the end of the ‘with’ statement the level is restored to its original value.
Will enable the requested logging level if it was disabled via `logging.disable()`.
Parameters:
    
  * **level** (_int_ _|__str_) – The level.
  * **logger** (_str_ _|__None_) – The logger to update. If not given, the root logger.


_with _filtering(_filter__)[source]¶
    
Context manager that temporarily adds the given filter to the caplog’s `handler()` for the ‘with’ statement block, and removes that filter at the end of the block.
Parameters:
    
**filter** – A custom `logging.Filter` object.
Added in version 7.5.
### capsys¶
**Tutorial** : How to capture stdout/stderr output
capsys()[source]¶
    
Enable text capturing of writes to `sys.stdout` and `sys.stderr`.
The captured output is made available via `capsys.readouterr()` method calls, which return a `(out, err)` namedtuple. `out` and `err` will be `text` objects.
Returns an instance of `CaptureFixture[str]`.
Example:
```
def test_output(capsys):
  print("hello")
  captured = capsys.readouterr()
  assert captured.out == "hello\n"

```

_class_ CaptureFixture[source]¶
    
Object returned by the `capsys`, `capsysbinary`, `capfd` and `capfdbinary` fixtures.
readouterr()[source]¶
    
Read and return the captured output so far, resetting the internal buffer.
Returns:
    
The captured content as a namedtuple with `out` and `err` string attributes.
Return type:
    
_CaptureResult_
_with _disabled()[source]¶
    
Temporarily disable capturing while inside the `with` block.
### capsysbinary¶
**Tutorial** : How to capture stdout/stderr output
capsysbinary()[source]¶
    
Enable bytes capturing of writes to `sys.stdout` and `sys.stderr`.
The captured output is made available via `capsysbinary.readouterr()` method calls, which return a `(out, err)` namedtuple. `out` and `err` will be `bytes` objects.
Returns an instance of `CaptureFixture[bytes]`.
Example:
```
def test_output(capsysbinary):
  print("hello")
  captured = capsysbinary.readouterr()
  assert captured.out == b"hello\n"

```

### config.cache¶
**Tutorial** : How to re-run failed tests and maintain state between test runs
The `config.cache` object allows other plugins and fixtures to store and retrieve values across test runs. To access it from fixtures request `pytestconfig` into your fixture and get it with `pytestconfig.cache`.
Under the hood, the cache plugin uses the simple `dumps`/`loads` API of the `json` stdlib module.
`config.cache` is an instance of `pytest.Cache`:
_final class_Cache[source]¶
    
Instance of the `cache` fixture.
mkdir(_name_)[source]¶
    
Return a directory path object with the given name.
If the directory does not yet exist, it will be created. You can use it to manage files to e.g. store/retrieve database dumps across test sessions.
Added in version 7.0.
Parameters:
    
**name** (_str_) – Must be a string not containing a `/` separator. Make sure the name contains your plugin or application identifiers to prevent clashes with other cache users.
get(_key_ , _default_)[source]¶
    
Return the cached value for the given key.
If no value was yet cached or the value cannot be read, the specified default is returned.
Parameters:
    
  * **key** (_str_) – Must be a `/` separated value. Usually the first name is the name of your plugin or your application.
  * **default** – The value to return in case of a cache-miss or invalid cache value.


set(_key_ , _value_)[source]¶
    
Save value for the given key.
Parameters:
    
  * **key** (_str_) – Must be a `/` separated value. Usually the first name is the name of your plugin or your application.
  * **value** (_object_) – Must be of any combination of basic python types, including nested types like lists of dictionaries.


### doctest_namespace¶
**Tutorial** : How to run doctests
doctest_namespace()[source]¶
    
Fixture that returns a `dict` that will be injected into the namespace of doctests.
Usually this fixture is used in conjunction with another `autouse` fixture:
```
@pytest.fixture(autouse=True)
def add_np(doctest_namespace):
  doctest_namespace["np"] = numpy

```

For more details: ‘doctest_namespace’ fixture.
### monkeypatch¶
**Tutorial** : How to monkeypatch/mock modules and environments
monkeypatch()[source]¶
    
A convenient fixture for monkey-patching.
The fixture provides these methods to modify objects, dictionaries, or `os.environ`:
  * `monkeypatch.setattr(obj, name, value, raising=True)`
  * `monkeypatch.delattr(obj, name, raising=True)`
  * `monkeypatch.setitem(mapping, name, value)`
  * `monkeypatch.delitem(obj, name, raising=True)`
  * `monkeypatch.setenv(name, value, prepend=None)`
  * `monkeypatch.delenv(name, raising=True)`
  * `monkeypatch.syspath_prepend(path)`
  * `monkeypatch.chdir(path)`
  * `monkeypatch.context()`


All modifications will be undone after the requesting test function or fixture has finished. The `raising` parameter determines if a `KeyError` or `AttributeError` will be raised if the set/deletion operation does not have the specified target.
To undo modifications done by the fixture in a contained scope, use `context()`.
Returns a `MonkeyPatch` instance.
_final class_MonkeyPatch[source]¶
    
Helper to conveniently monkeypatch attributes/items/environment variables/syspath.
Returned by the `monkeypatch` fixture.
Changed in version 6.2: Can now also be used directly as `pytest.MonkeyPatch()`, for when the fixture is not available. In this case, use `with MonkeyPatch.context() as mp:` or remember to call `undo()` explicitly.
_classmethod with _context()[source]¶
    
Context manager that returns a new `MonkeyPatch` object which undoes any patching done inside the `with` block upon exit.
Example:
```
import functools

def test_partial(monkeypatch):
  with monkeypatch.context() as m:
    m.setattr(functools, "partial", 3)

```

Useful in situations where it is desired to undo some patches before the test ends, such as mocking `stdlib` functions that might break pytest itself if mocked (for examples of this see #3290).
setattr(_target: str_, _name: object_, _value: ~_pytest.monkeypatch.Notset = <notset>_, _raising: bool = True_) → None[source]¶
setattr(_target :object_, _name :str_, _value :object_, _raising :bool=True_) → None
    
Set attribute value on target, memorizing the old value.
For example:
```
import os
monkeypatch.setattr(os, "getcwd", lambda: "/")

```

The code above replaces the `os.getcwd()` function by a `lambda` which always returns `"/"`.
For convenience, you can specify a string as `target` which will be interpreted as a dotted import path, with the last part being the attribute name:
```
monkeypatch.setattr("os.getcwd", lambda: "/")

```

Raises `AttributeError` if the attribute does not exist, unless `raising` is set to False.
**Where to patch**
`monkeypatch.setattr` works by (temporarily) changing the object that a name points to with another one. There can be many names pointing to any individual object, so for patching to work you must ensure that you patch the name used by the system under test.
See the section Where to patch in the `unittest.mock` docs for a complete explanation, which is meant for `unittest.mock.patch()` but applies to `monkeypatch.setattr` as well.
delattr(_target_ , _name= <notset>_, _raising=True_)[source]¶
    
Delete attribute `name` from `target`.
If no `name` is specified and `target` is a string it will be interpreted as a dotted import path with the last part being the attribute name.
Raises AttributeError it the attribute does not exist, unless `raising` is set to False.
setitem(_dic_ , _name_ , _value_)[source]¶
    
Set dictionary entry `name` to value.
delitem(_dic_ , _name_ , _raising =True_)[source]¶
    
Delete `name` from dict.
Raises `KeyError` if it doesn’t exist, unless `raising` is set to False.
setenv(_name_ , _value_ , _prepend =None_)[source]¶
    
Set environment variable `name` to `value`.
If `prepend` is a character, read the current environment variable value and prepend the `value` adjoined with the `prepend` character.
delenv(_name_ , _raising =True_)[source]¶
    
Delete `name` from the environment.
Raises `KeyError` if it does not exist, unless `raising` is set to False.
syspath_prepend(_path_)[source]¶
    
Prepend `path` to `sys.path` list of import locations.
chdir(_path_)[source]¶
    
Change the current working directory to the specified path.
Parameters:
    
**path** (_str_ _|__PathLike_ _[__str_ _]_) – The path to change into.
undo()[source]¶
    
Undo previous changes.
This call consumes the undo stack. Calling it a second time has no effect unless you do more monkeypatching after the undo call.
There is generally no need to call `undo()`, since it is called automatically during tear-down.
Note
The same `monkeypatch` fixture is used across a single test function invocation. If `monkeypatch` is used both by the test function itself and one of the test fixtures, calling `undo()` will undo all of the changes made in both functions.
Prefer to use `context()` instead.
### pytestconfig¶
pytestconfig()[source]¶
    
Session-scoped fixture that returns the session’s `pytest.Config` object.
Example:
```
def test_foo(pytestconfig):
  if pytestconfig.get_verbosity() > 0:
    ...

```

### pytester¶
Added in version 6.2.
Provides a `Pytester` instance that can be used to run and test pytest itself.
It provides an empty directory where pytest can be executed in isolation, and contains facilities to write tests, configuration files, and match against expected output.
To use it, include in your topmost `conftest.py` file:
```
pytest_plugins = "pytester"

```

_final class_Pytester[source]¶
    
Facilities to write tests/configuration files, execute pytest in isolation, and match against expected output, perfect for black-box testing of pytest plugins.
It attempts to isolate the test run from external factors as much as possible, modifying the current working directory to `path` and environment variables during initialization.
_exception_ TimeoutExpired[source]¶
plugins _: list[str|object]_¶
    
A list of plugins to use with `parseconfig()` and `runpytest()`. Initially this is an empty list but plugins can be added to the list. The type of items to add to the list depends on the method using them so refer to them for details.
_property_ path _: Path_¶
    
Temporary directory path used to create files/run tests from, etc.
make_hook_recorder(_pluginmanager_)[source]¶
    
Create a new `HookRecorder` for a `PytestPluginManager`.
chdir()[source]¶
    
Cd into the temporary directory.
This is done automatically upon instantiation.
makefile(_ext_ , _* args_, _** kwargs_)[source]¶
    
Create new text file(s) in the test directory.
Parameters:
    
  * **ext** (_str_) – The extension the file(s) should use, including the dot, e.g. `.py`.
  * **args** (_str_) – All args are treated as strings and joined using newlines. The result is written as contents to the file. The name of the file is based on the test function requesting this fixture.
  * **kwargs** (_str_) – Each keyword is the name of a file, while the value of it will be written as contents of the file.


Returns:
    
The first created file.
Return type:
    
_Path_
Examples:
```
pytester.makefile(".txt", "line1", "line2")
pytester.makefile(".ini", pytest="[pytest]\naddopts=-rs\n")

```

To create binary files, use `pathlib.Path.write_bytes()` directly:
```
filename = pytester.path.joinpath("foo.bin")
filename.write_bytes(b"...")

```

makeconftest(_source_)[source]¶
    
Write a conftest.py file.
Parameters:
    
**source** (_str_) – The contents.
Returns:
    
The conftest.py file.
Return type:
    
_Path_
makeini(_source_)[source]¶
    
Write a tox.ini file.
Parameters:
    
**source** (_str_) – The contents.
Returns:
    
The tox.ini file.
Return type:
    
_Path_
getinicfg(_source_)[source]¶
    
Return the pytest section from the tox.ini config file.
makepyprojecttoml(_source_)[source]¶
    
Write a pyproject.toml file.
Parameters:
    
**source** (_str_) – The contents.
Returns:
    
The pyproject.ini file.
Return type:
    
_Path_
Added in version 6.0.
makepyfile(_* args_, _** kwargs_)[source]¶
    
Shortcut for .makefile() with a .py extension.
Defaults to the test name with a ‘.py’ extension, e.g test_foobar.py, overwriting existing files.
Examples:
```
def test_something(pytester):
  # Initial file is created test_something.py.
  pytester.makepyfile("foobar")
  # To create multiple files, pass kwargs accordingly.
  pytester.makepyfile(custom="foobar")
  # At this point, both 'test_something.py' & 'custom.py' exist in the test directory.

```

maketxtfile(_* args_, _** kwargs_)[source]¶
    
Shortcut for .makefile() with a .txt extension.
Defaults to the test name with a ‘.txt’ extension, e.g test_foobar.txt, overwriting existing files.
Examples:
```
def test_something(pytester):
  # Initial file is created test_something.txt.
  pytester.maketxtfile("foobar")
  # To create multiple files, pass kwargs accordingly.
  pytester.maketxtfile(custom="foobar")
  # At this point, both 'test_something.txt' & 'custom.txt' exist in the test directory.

```

syspathinsert(_path =None_)[source]¶
    
Prepend a directory to sys.path, defaults to `path`.
This is undone automatically when this object dies at the end of each test.
Parameters:
    
**path** (_str_ _|__PathLike_ _[__str_ _]__|__None_) – The path.
mkdir(_name_)[source]¶
    
Create a new (sub)directory.
Parameters:
    
**name** (_str_ _|__PathLike_ _[__str_ _]_) – The name of the directory, relative to the pytester path.
Returns:
    
The created directory.
Return type:
    
pathlib.Path
mkpydir(_name_)[source]¶
    
Create a new python package.
This creates a (sub)directory with an empty `__init__.py` file so it gets recognised as a Python package.
copy_example(_name =None_)[source]¶
    
Copy file from project’s directory into the testdir.
Parameters:
    
**name** (_str_ _|__None_) – The name of the file to copy.
Returns:
    
Path to the copied directory (inside `self.path`).
Return type:
    
pathlib.Path
getnode(_config_ , _arg_)[source]¶
    
Get the collection node of a file.
Parameters:
    
  * **config** (_Config_) – A pytest config. See `parseconfig()` and `parseconfigure()` for creating it.
  * **arg** (_str_ _|__PathLike_ _[__str_ _]_) – Path to the file.


Returns:
    
The node.
Return type:
    
_Collector_ | _Item_
getpathnode(_path_)[source]¶
    
Return the collection node of a file.
This is like `getnode()` but uses `parseconfigure()` to create the (configured) pytest Config instance.
Parameters:
    
**path** (_str_ _|__PathLike_ _[__str_ _]_) – Path to the file.
Returns:
    
The node.
Return type:
    
_Collector_ | _Item_
genitems(_colitems_)[source]¶
    
Generate all test items from a collection node.
This recurses into the collection node and returns a list of all the test items contained within.
Parameters:
    
**colitems** (_Sequence_ _[__Item_ _|__Collector_ _]_) – The collection nodes.
Returns:
    
The collected items.
Return type:
    
list[_Item_]
runitem(_source_)[source]¶
    
Run the “test_func” Item.
The calling test instance (class containing the test method) must provide a `.getrunner()` method which should return a runner which can run the test protocol for a single item, e.g. `_pytest.runner.runtestprotocol`.
inline_runsource(_source_ , _* cmdlineargs_)[source]¶
    
Run a test module in process using `pytest.main()`.
This run writes “source” into a temporary file and runs `pytest.main()` on it, returning a `HookRecorder` instance for the result.
Parameters:
    
  * **source** (_str_) – The source code of the test module.
  * **cmdlineargs** – Any extra command line arguments to use.


inline_genitems(_* args_)[source]¶
    
Run `pytest.main(['--collect-only'])` in-process.
Runs the `pytest.main()` function to run all of pytest inside the test process itself like `inline_run()`, but returns a tuple of the collected items and a `HookRecorder` instance.
inline_run(_* args_, _plugins =()_, _no_reraise_ctrlc =False_)[source]¶
    
Run `pytest.main()` in-process, returning a HookRecorder.
Runs the `pytest.main()` function to run all of pytest inside the test process itself. This means it can return a `HookRecorder` instance which gives more detailed results from that run than can be done by matching stdout/stderr from `runpytest()`.
Parameters:
    
  * **args** (_str_ _|__PathLike_ _[__str_ _]_) – Command line arguments to pass to `pytest.main()`.
  * **plugins** – Extra plugin instances the `pytest.main()` instance should use.
  * **no_reraise_ctrlc** (_bool_) – Typically we reraise keyboard interrupts from the child run. If True, the KeyboardInterrupt exception is captured.


runpytest_inprocess(_* args_, _** kwargs_)[source]¶
    
Return result of running pytest in-process, providing a similar interface to what self.runpytest() provides.
runpytest(_* args_, _** kwargs_)[source]¶
    
Run pytest inline or in a subprocess, depending on the command line option “–runpytest” and return a `RunResult`.
parseconfig(_* args_)[source]¶
    
Return a new pytest `pytest.Config` instance from given commandline args.
This invokes the pytest bootstrapping code in _pytest.config to create a new `pytest.PytestPluginManager` and call the `pytest_cmdline_parse` hook to create a new `pytest.Config` instance.
If `plugins` has been populated they should be plugin modules to be registered with the plugin manager.
parseconfigure(_* args_)[source]¶
    
Return a new pytest configured Config instance.
Returns a new `pytest.Config` instance like `parseconfig()`, but also calls the `pytest_configure` hook.
getitem(_source_ , _funcname ='test_func'_)[source]¶
    
Return the test item for a test function.
Writes the source to a python file and runs pytest’s collection on the resulting module, returning the test item for the requested function name.
Parameters:
    
  * **source** (_str_ _|__PathLike_ _[__str_ _]_) – The module source.
  * **funcname** (_str_) – The name of the test function for which to return a test item.


Returns:
    
The test item.
Return type:
    
_Item_
getitems(_source_)[source]¶
    
Return all test items collected from the module.
Writes the source to a Python file and runs pytest’s collection on the resulting module, returning all test items contained within.
getmodulecol(_source_ , _configargs =()_, _*_ , _withinit =False_)[source]¶
    
Return the module collection node for `source`.
Writes `source` to a file using `makepyfile()` and then runs the pytest collection on it, returning the collection node for the test module.
Parameters:
    
  * **source** (_str_ _|__PathLike_ _[__str_ _]_) – The source code of the module to collect.
  * **configargs** – Any extra arguments to pass to `parseconfigure()`.
  * **withinit** (_bool_) – Whether to also write an `__init__.py` file to the same directory to ensure it is a package.


collect_by_name(_modcol_ , _name_)[source]¶
    
Return the collection node for name from the module collection.
Searches a module collection node for a collection node matching the given name.
Parameters:
    
  * **modcol** (_Collector_) – A module collection node; see `getmodulecol()`.
  * **name** (_str_) – The name of the node to return.


popen(_cmdargs_ , _stdout =-1_, _stderr =-1_, _stdin =NotSetType.token_, _** kw_)[source]¶
    
Invoke `subprocess.Popen`.
Calls `subprocess.Popen` making sure the current working directory is in `PYTHONPATH`.
You probably want to use `run()` instead.
run(_* cmdargs_, _timeout =None_, _stdin =NotSetType.token_)[source]¶
    
Run a command with arguments.
Run a process using `subprocess.Popen` saving the stdout and stderr.
Parameters:
    
  * **cmdargs** (_str_ _|__PathLike_ _[__str_ _]_) – The sequence of arguments to pass to `subprocess.Popen`, with path-like objects being converted to `str` automatically.
  * **timeout** (_float_ _|__None_) – The period in seconds after which to timeout and raise `Pytester.TimeoutExpired`.
  * **stdin** (__pytest.compat.NotSetType_ _|__bytes_ _|__IO_ _[__Any_ _]__|__int_) – 
Optional standard input.
    * If it is `CLOSE_STDIN` (Default), then this method calls `subprocess.Popen` with `stdin=subprocess.PIPE`, and the standard input is closed immediately after the new command is started.
    * If it is of type `bytes`, these bytes are sent to the standard input of the command.
    * Otherwise, it is passed through to `subprocess.Popen`. For further information in this case, consult the document of the `stdin` parameter in `subprocess.Popen`.


Returns:
    
The result.
Return type:
    
_RunResult_
runpython(_script_)[source]¶
    
Run a python script using sys.executable as interpreter.
runpython_c(_command_)[source]¶
    
Run `python -c "command"`.
runpytest_subprocess(_* args_, _timeout =None_)[source]¶
    
Run pytest as a subprocess with given arguments.
Any plugins added to the `plugins` list will be added using the `-p` command line option. Additionally `--basetemp` is used to put any temporary files and directories in a numbered directory prefixed with “runpytest-” to not conflict with the normal numbered pytest location for temporary files and directories.
Parameters:
    
  * **args** (_str_ _|__PathLike_ _[__str_ _]_) – The sequence of arguments to pass to the pytest subprocess.
  * **timeout** (_float_ _|__None_) – The period in seconds after which to timeout and raise `Pytester.TimeoutExpired`.


Returns:
    
The result.
Return type:
    
_RunResult_
spawn_pytest(_string_ , _expect_timeout =10.0_)[source]¶
    
Run pytest using pexpect.
This makes sure to use the right pytest and sets up the temporary directory locations.
The pexpect child is returned.
spawn(_cmd_ , _expect_timeout =10.0_)[source]¶
    
Run a command using pexpect.
The pexpect child is returned.
_final class_RunResult[source]¶
    
The result of running a command from `Pytester`.
ret _: int|ExitCode_¶
    
The return value.
outlines¶
    
List of lines captured from stdout.
errlines¶
    
List of lines captured from stderr.
stdout¶
    
`LineMatcher` of stdout.
Use e.g. `str(stdout)` to reconstruct stdout, or the commonly used `stdout.fnmatch_lines()` method.
stderr¶
    
`LineMatcher` of stderr.
duration¶
    
Duration in seconds.
parseoutcomes()[source]¶
    
Return a dictionary of outcome noun -> count from parsing the terminal output that the test process produced.
The returned nouns will always be in plural form:
```
======= 1 failed, 1 passed, 1 warning, 1 error in 0.13s ====

```

Will return `{"failed": 1, "passed": 1, "warnings": 1, "errors": 1}`.
_classmethod _parse_summary_nouns(_lines_)[source]¶
    
Extract the nouns from a pytest terminal summary line.
It always returns the plural noun for consistency:
```
======= 1 failed, 1 passed, 1 warning, 1 error in 0.13s ====

```

Will return `{"failed": 1, "passed": 1, "warnings": 1, "errors": 1}`.
assert_outcomes(_passed =0_, _skipped =0_, _failed =0_, _errors =0_, _xpassed =0_, _xfailed =0_, _warnings =None_, _deselected =None_)[source]¶
    
Assert that the specified outcomes appear with the respective numbers (0 means it didn’t occur) in the text output from a test run.
`warnings` and `deselected` are only checked if not None.
_class_ LineMatcher[source]¶
    
Flexible matching of text.
This is a convenience class to test large texts like the output of commands.
The constructor takes a list of lines without their trailing newlines, i.e. `text.splitlines()`.
__str__()[source]¶
    
Return the entire original text.
Added in version 6.2: You can use `str()` in older versions.
fnmatch_lines_random(_lines2_)[source]¶
    
Check lines exist in the output in any order (using `fnmatch.fnmatch()`).
re_match_lines_random(_lines2_)[source]¶
    
Check lines exist in the output in any order (using `re.match()`).
get_lines_after(_fnline_)[source]¶
    
Return all lines following the given line in the text.
The given line can contain glob wildcards.
fnmatch_lines(_lines2_ , _*_ , _consecutive =False_)[source]¶
    
Check lines exist in the output (using `fnmatch.fnmatch()`).
The argument is a list of lines which have to match and can use glob wildcards. If they do not match a pytest.fail() is called. The matches and non-matches are also shown as part of the error message.
Parameters:
    
  * **lines2** (_Sequence_ _[__str_ _]_) – String patterns to match.
  * **consecutive** (_bool_) – Match lines consecutively?


re_match_lines(_lines2_ , _*_ , _consecutive =False_)[source]¶
    
Check lines exist in the output (using `re.match()`).
The argument is a list of lines which have to match using `re.match`. If they do not match a pytest.fail() is called.
The matches and non-matches are also shown as part of the error message.
Parameters:
    
  * **lines2** (_Sequence_ _[__str_ _]_) – string patterns to match.
  * **consecutive** (_bool_) – match lines consecutively?


no_fnmatch_line(_pat_)[source]¶
    
Ensure captured lines do not match the given pattern, using `fnmatch.fnmatch`.
Parameters:
    
**pat** (_str_) – The pattern to match lines.
no_re_match_line(_pat_)[source]¶
    
Ensure captured lines do not match the given pattern, using `re.match`.
Parameters:
    
**pat** (_str_) – The regular expression to match lines.
str()[source]¶
    
Return the entire original text.
_final class_HookRecorder[source]¶
    
Record all hooks called in a plugin manager.
Hook recorders are created by `Pytester`.
This wraps all the hook calls in the plugin manager, recording each call before propagating the normal calls.
getcalls(_names_)[source]¶
    
Get all recorded calls to hooks with the given names (or name).
matchreport(_inamepart =''_, _names =('pytest_runtest_logreport', 'pytest_collectreport')_, _when =None_)[source]¶
    
Return a testreport whose dotted import path matches.
_final class_RecordedHookCall[source]¶
    
A recorded call to a hook.
The arguments to the hook call are set as attributes. For example:
```
calls = hook_recorder.getcalls("pytest_runtest_setup")
# Suppose pytest_runtest_setup was called once with `item=an_item`.
assert calls[0].item is an_item

```

### record_property¶
**Tutorial** : record_property
record_property()[source]¶
    
Add extra properties to the calling test.
User properties become part of the test report and are available to the configured reporters, like JUnit XML.
The fixture is callable with `name, value`. The value is automatically XML-encoded.
Example:
```
def test_function(record_property):
  record_property("example_key", 1)

```

### record_testsuite_property¶
**Tutorial** : record_testsuite_property
record_testsuite_property()[source]¶
    
Record a new `<property>` tag as child of the root `<testsuite>`.
This is suitable to writing global information regarding the entire test suite, and is compatible with `xunit2` JUnit family.
This is a `session`-scoped fixture which is called with `(name, value)`. Example:
```
def test_foo(record_testsuite_property):
  record_testsuite_property("ARCH", "PPC")
  record_testsuite_property("STORAGE_TYPE", "CEPH")

```

Parameters:
    
  * **name** – The property name.
  * **value** – The property value. Will be converted to a string.


Warning
Currently this fixture **does not work** with the pytest-xdist plugin. See #7767 for details.
### recwarn¶
**Tutorial** : Recording warnings
recwarn()[source]¶
    
Return a `WarningsRecorder` instance that records all warnings emitted by test functions.
See How to capture warnings for information on warning categories.
_class_ WarningsRecorder[source]¶
    
A context manager to record raised warnings.
Each recorded warning is an instance of `warnings.WarningMessage`.
Adapted from `warnings.catch_warnings`.
Note
`DeprecationWarning` and `PendingDeprecationWarning` are treated differently; see Ensuring code triggers a deprecation warning.
_property_ list _: list[WarningMessage]_¶
    
The list of recorded warnings.
__getitem__(_i_)[source]¶
    
Get a recorded warning by index.
__iter__()[source]¶
    
Iterate through the recorded warnings.
__len__()[source]¶
    
The number of recorded warnings.
pop(_cls= <class 'Warning'>_)[source]¶
    
Pop the first recorded warning which is an instance of `cls`, but not an instance of a child class of any other match. Raises `AssertionError` if there is no match.
clear()[source]¶
    
Clear the list of recorded warnings.
### request¶
**Example** : Pass different values to a test function, depending on command line options
The `request` fixture is a special fixture providing information of the requesting test function.
_class_ FixtureRequest[source]¶
    
The type of the `request` fixture.
A request object gives access to the requesting test context and has a `param` attribute in case the fixture is parametrized.
fixturename _: Final_¶
    
Fixture for which this request is being performed.
_property_ scope _: Literal['session','package','module','class','function']_¶
    
Scope string, one of “function”, “class”, “module”, “package”, “session”.
_property_ fixturenames _: list[str]_¶
    
Names of all active fixtures in this request.
_abstract property_node¶
    
Underlying collection node (depends on current request scope).
_property_ config _: Config_¶
    
The pytest config object associated with this request.
_property_ function¶
    
Test function object if the request has a per-function scope.
_property_ cls¶
    
Class (can be None) where the test function was collected.
_property_ instance¶
    
Instance (can be None) on which test function was collected.
_property_ module¶
    
Python module object where the test function was collected.
_property_ path _: Path_¶
    
Path where the test function was collected.
_property_ keywords _: MutableMapping[str,Any]_¶
    
Keywords/markers dictionary for the underlying node.
_property_ session _: Session_¶
    
Pytest session object.
_abstractmethod _addfinalizer(_finalizer_)[source]¶
    
Add finalizer/teardown function to be called without arguments after the last test within the requesting test context finished execution.
applymarker(_marker_)[source]¶
    
Apply a marker to a single test function invocation.
This method is useful if you don’t want to have a keyword/marker on all function invocations.
Parameters:
    
**marker** (_str_ _|__MarkDecorator_) – An object created by a call to `pytest.mark.NAME(...)`.
raiseerror(_msg_)[source]¶
    
Raise a FixtureLookupError exception.
Parameters:
    
**msg** (_str_ _|__None_) – An optional custom error message.
getfixturevalue(_argname_)[source]¶
    
Dynamically run a named fixture function.
Declaring fixtures via function argument is recommended where possible. But if you can only decide whether to use another fixture at test setup time, you may use this function to retrieve it inside a fixture or test function body.
This method can be used during the test setup phase or the test run phase, but during the test teardown phase a fixture’s value may not be available.
Parameters:
    
**argname** (_str_) – The fixture name.
Raises:
    
**pytest.FixtureLookupError** – If the given fixture could not be found.
### testdir¶
Identical to `pytester`, but provides an instance whose methods return legacy `py.path.local` objects instead when applicable.
New code should avoid using `testdir` in favor of `pytester`.
_final class_Testdir[source]
    
Similar to `Pytester`, but this class works with legacy legacy_path objects instead.
All methods just forward to an internal `Pytester` instance, converting results to `legacy_path` objects as necessary.
_exception_ TimeoutExpired
_property_ tmpdir _: LocalPath_
    
Temporary directory where tests are executed.
make_hook_recorder(_pluginmanager_)[source]
    
See `Pytester.make_hook_recorder()`.
chdir()[source]
    
See `Pytester.chdir()`.
makefile(_ext_ , _* args_, _** kwargs_)[source]
    
See `Pytester.makefile()`.
makeconftest(_source_)[source]
    
See `Pytester.makeconftest()`.
makeini(_source_)[source]
    
See `Pytester.makeini()`.
getinicfg(_source_)[source]
    
See `Pytester.getinicfg()`.
makepyprojecttoml(_source_)[source]
    
See `Pytester.makepyprojecttoml()`.
makepyfile(_* args_, _** kwargs_)[source]
    
See `Pytester.makepyfile()`.
maketxtfile(_* args_, _** kwargs_)[source]
    
See `Pytester.maketxtfile()`.
syspathinsert(_path =None_)[source]
    
See `Pytester.syspathinsert()`.
mkdir(_name_)[source]
    
See `Pytester.mkdir()`.
mkpydir(_name_)[source]
    
See `Pytester.mkpydir()`.
copy_example(_name =None_)[source]
    
See `Pytester.copy_example()`.
getnode(_config_ , _arg_)[source]
    
See `Pytester.getnode()`.
getpathnode(_path_)[source]
    
See `Pytester.getpathnode()`.
genitems(_colitems_)[source]
    
See `Pytester.genitems()`.
runitem(_source_)[source]
    
See `Pytester.runitem()`.
inline_runsource(_source_ , _* cmdlineargs_)[source]
    
See `Pytester.inline_runsource()`.
inline_genitems(_* args_)[source]
    
See `Pytester.inline_genitems()`.
inline_run(_* args_, _plugins =()_, _no_reraise_ctrlc =False_)[source]
    
See `Pytester.inline_run()`.
runpytest_inprocess(_* args_, _** kwargs_)[source]
    
See `Pytester.runpytest_inprocess()`.
runpytest(_* args_, _** kwargs_)[source]
    
See `Pytester.runpytest()`.
parseconfig(_* args_)[source]
    
See `Pytester.parseconfig()`.
parseconfigure(_* args_)[source]
    
See `Pytester.parseconfigure()`.
getitem(_source_ , _funcname ='test_func'_)[source]
    
See `Pytester.getitem()`.
getitems(_source_)[source]
    
See `Pytester.getitems()`.
getmodulecol(_source_ , _configargs =()_, _withinit =False_)[source]
    
See `Pytester.getmodulecol()`.
collect_by_name(_modcol_ , _name_)[source]
    
See `Pytester.collect_by_name()`.
popen(_cmdargs_ , _stdout =-1_, _stderr =-1_, _stdin =NotSetType.token_, _** kw_)[source]
    
See `Pytester.popen()`.
run(_* cmdargs_, _timeout =None_, _stdin =NotSetType.token_)[source]
    
See `Pytester.run()`.
runpython(_script_)[source]
    
See `Pytester.runpython()`.
runpython_c(_command_)[source]
    
See `Pytester.runpython_c()`.
runpytest_subprocess(_* args_, _timeout =None_)[source]
    
See `Pytester.runpytest_subprocess()`.
spawn_pytest(_string_ , _expect_timeout =10.0_)[source]
    
See `Pytester.spawn_pytest()`.
spawn(_cmd_ , _expect_timeout =10.0_)[source]
    
See `Pytester.spawn()`.
### tmp_path¶
**Tutorial** : How to use temporary directories and files in tests
tmp_path()[source]¶
    
Return a temporary directory (as `pathlib.Path` object) which is unique to each test function invocation. The temporary directory is created as a subdirectory of the base temporary directory, with configurable retention, as discussed in Temporary directory location and retention.
### tmp_path_factory¶
**Tutorial** : The tmp_path_factory fixture
`tmp_path_factory` is an instance of `TempPathFactory`:
_final class_TempPathFactory[source]¶
    
Factory for temporary directories under the common base temp directory, as discussed at Temporary directory location and retention.
mktemp(_basename_ , _numbered =True_)[source]¶
    
Create a new temporary directory managed by the factory.
Parameters:
    
  * **basename** (_str_) – Directory base name, must be a relative path.
  * **numbered** (_bool_) – If `True`, ensure the directory is unique by adding a numbered suffix greater than any existing one: `basename="foo-"` and `numbered=True` means that this function will create directories named `"foo-0"`, `"foo-1"`, `"foo-2"` and so on.


Returns:
    
The path to the new directory.
Return type:
    
_Path_
getbasetemp()[source]¶
    
Return the base temporary directory, creating it if needed.
Returns:
    
The base temporary directory.
Return type:
    
_Path_
### tmpdir¶
**Tutorial** : The tmpdir and tmpdir_factory fixtures
tmpdir()¶
    
Return a temporary directory (as legacy_path object) which is unique to each test function invocation. The temporary directory is created as a subdirectory of the base temporary directory, with configurable retention, as discussed in Temporary directory location and retention.
Note
These days, it is preferred to use `tmp_path`.
About the tmpdir and tmpdir_factory fixtures.
### tmpdir_factory¶
**Tutorial** : The tmpdir and tmpdir_factory fixtures
`tmpdir_factory` is an instance of `TempdirFactory`:
_final class_TempdirFactory[source]¶
    
Backward compatibility wrapper that implements `py.path.local` for `TempPathFactory`.
Note
These days, it is preferred to use `tmp_path_factory`.
About the tmpdir and tmpdir_factory fixtures.
mktemp(_basename_ , _numbered =True_)[source]¶
    
Same as `TempPathFactory.mktemp()`, but returns a `py.path.local` object.
getbasetemp()[source]¶
    
Same as `TempPathFactory.getbasetemp()`, but returns a `py.path.local` object.
## Hooks¶
**Tutorial** : Writing plugins
Reference to all hooks which can be implemented by conftest.py files and plugins.
### @pytest.hookimpl¶
@pytest.hookimpl¶
    
pytest’s decorator for marking functions as hook implementations.
See Writing hook functions and `pluggy.HookimplMarker()`.
### @pytest.hookspec¶
@pytest.hookspec¶
    
pytest’s decorator for marking functions as hook specifications.
See Declaring new hooks and `pluggy.HookspecMarker()`.
### Bootstrapping hooks¶
Bootstrapping hooks called for plugins registered early enough (internal and third-party plugins).
pytest_load_initial_conftests(_early_config_ , _parser_ , _args_)[source]¶
    
Called to implement the loading of initial conftest files ahead of command line option parsing.
Parameters:
    
  * **early_config** (_Config_) – The pytest config object.
  * **args** (_list_ _[__str_ _]_) – Arguments passed on the command line.
  * **parser** (_Parser_) – To add command line options.


#### Use in conftest plugins¶
This hook is not called for conftest files.
pytest_cmdline_parse(_pluginmanager_ , _args_)[source]¶
    
Return an initialized `Config`, parsing the specified args.
Stops at first non-None result, see firstresult: stop at first non-None result.
Note
This hook is only called for plugin classes passed to the `plugins` arg when using pytest.main to perform an in-process test run.
Parameters:
    
  * **pluginmanager** (_PytestPluginManager_) – The pytest plugin manager.
  * **args** (_list_ _[__str_ _]_) – List of arguments passed on the command line.


Returns:
    
A pytest config object.
Return type:
    
Config | None
#### Use in conftest plugins¶
This hook is not called for conftest files.
pytest_cmdline_main(_config_)[source]¶
    
Called for performing the main command line action.
The default implementation will invoke the configure hooks and `pytest_runtestloop`.
Stops at first non-None result, see firstresult: stop at first non-None result.
Parameters:
    
**config** (_Config_) – The pytest config object.
Returns:
    
The exit code.
Return type:
    
ExitCode | int | None
#### Use in conftest plugins¶
This hook is only called for initial conftests.
### Initialization hooks¶
Initialization hooks called for plugins and `conftest.py` files.
pytest_addoption(_parser_ , _pluginmanager_)[source]¶
    
Register argparse-style options and ini-style config values, called once at the beginning of a test run.
Parameters:
    
  * **parser** (_Parser_) – To add command line options, call `parser.addoption(...)`. To add ini-file values call `parser.addini(...)`.
  * **pluginmanager** (_PytestPluginManager_) – The pytest plugin manager, which can be used to install `hookspec()`’s or `hookimpl()`’s and allow one plugin to call another plugin’s hooks to change how command line options are added.


Options can later be accessed through the `config` object, respectively:
  * `config.getoption(name)` to retrieve the value of a command line option.
  * `config.getini(name)` to retrieve a value read from an ini-style file.


The config object is passed around on many internal objects via the `.config` attribute or can be retrieved as the `pytestconfig` fixture.
Note
This hook is incompatible with hook wrappers.
#### Use in conftest plugins¶
If a conftest plugin implements this hook, it will be called immediately when the conftest is registered.
This hook is only called for initial conftests.
pytest_addhooks(_pluginmanager_)[source]¶
    
Called at plugin registration time to allow adding new hooks via a call to `pluginmanager.add_hookspecs(module_or_class, prefix)`.
Parameters:
    
**pluginmanager** (_PytestPluginManager_) – The pytest plugin manager.
Note
This hook is incompatible with hook wrappers.
#### Use in conftest plugins¶
If a conftest plugin implements this hook, it will be called immediately when the conftest is registered.
pytest_configure(_config_)[source]¶
    
Allow plugins and conftest files to perform initial configuration.
Note
This hook is incompatible with hook wrappers.
Parameters:
    
**config** (_Config_) – The pytest config object.
#### Use in conftest plugins¶
This hook is called for every initial conftest file after command line options have been parsed. After that, the hook is called for other conftest files as they are registered.
pytest_unconfigure(_config_)[source]¶
    
Called before test process is exited.
Parameters:
    
**config** (_Config_) – The pytest config object.
#### Use in conftest plugins¶
Any conftest file can implement this hook.
pytest_sessionstart(_session_)[source]¶
    
Called after the `Session` object has been created and before performing collection and entering the run test loop.
Parameters:
    
**session** (_Session_) – The pytest session object.
#### Use in conftest plugins¶
This hook is only called for initial conftests.
pytest_sessionfinish(_session_ , _exitstatus_)[source]¶
    
Called after whole test run finished, right before returning the exit status to the system.
Parameters:
    
  * **session** (_Session_) – The pytest session object.
  * **exitstatus** (_int_ _|__ExitCode_) – The status which pytest will return to the system.


#### Use in conftest plugins¶
Any conftest file can implement this hook.
pytest_plugin_registered(_plugin_ , _plugin_name_ , _manager_)[source]¶
    
A new pytest plugin got registered.
Parameters:
    
  * **plugin** (__PluggyPlugin_) – The plugin module or instance.
  * **plugin_name** (_str_) – The name by which the plugin is registered.
  * **manager** (_PytestPluginManager_) – The pytest plugin manager.


Note
This hook is incompatible with hook wrappers.
#### Use in conftest plugins¶
If a conftest plugin implements this hook, it will be called immediately when the conftest is registered, once for each plugin registered thus far (including itself!), and for all plugins thereafter when they are registered.
### Collection hooks¶
`pytest` calls the following hooks for collecting files and directories:
pytest_collection(_session_)[source]¶
    
Perform the collection phase for the given session.
Stops at first non-None result, see firstresult: stop at first non-None result. The return value is not used, but only stops further processing.
The default collection phase is this (see individual hooks for full details):
  1. Starting from `session` as the initial collector:


>   1. `pytest_collectstart(collector)`
>   2. `report = pytest_make_collect_report(collector)`
>   3. `pytest_exception_interact(collector, call, report)` if an interactive exception occurred
>   4. For each collected node:
> 

>>   1. If an item, `pytest_itemcollected(item)`
>>   2. If a collector, recurse into it.
>> 

>   1. `pytest_collectreport(report)`
> 

  1. `pytest_collection_modifyitems(session, config, items)`


>   1. `pytest_deselected(items)` for any deselected items (may be called multiple times)
> 

  1. `pytest_collection_finish(session)`
  2. Set `session.items` to the list of collected items
  3. Set `session.testscollected` to the number of collected items


You can implement this hook to only perform some action before collection, for example the terminal plugin uses it to start displaying the collection counter (and returns `None`).
Parameters:
    
**session** (_Session_) – The pytest session object.
#### Use in conftest plugins¶
This hook is only called for initial conftests.
pytest_ignore_collect(_collection_path_ , _path_ , _config_)[source]¶
    
Return `True` to ignore this path for collection.
Return `None` to let other plugins ignore the path for collection.
Returning `False` will forcefully _not_ ignore this path for collection, without giving a chance for other plugins to ignore this path.
This hook is consulted for all files and directories prior to calling more specific hooks.
Stops at first non-None result, see firstresult: stop at first non-None result.
Parameters:
    
  * **collection_path** (_pathlib.Path_) – The path to analyze.
  * **path** (_LEGACY_PATH_) – The path to analyze (deprecated).
  * **config** (_Config_) – The pytest config object.


Changed in version 7.0.0: The `collection_path` parameter was added as a `pathlib.Path` equivalent of the `path` parameter. The `path` parameter has been deprecated.
#### Use in conftest plugins¶
Any conftest file can implement this hook. For a given collection path, only conftest files in parent directories of the collection path are consulted (if the path is a directory, its own conftest file is _not_ consulted - a directory cannot ignore itself!).
pytest_collect_directory(_path_ , _parent_)[source]¶
    
Create a `Collector` for the given directory, or None if not relevant.
Added in version 8.0.
For best results, the returned collector should be a subclass of `Directory`, but this is not required.
The new node needs to have the specified `parent` as a parent.
Stops at first non-None result, see firstresult: stop at first non-None result.
Parameters:
    
**path** (_pathlib.Path_) – The path to analyze.
See Using a custom directory collector for a simple example of use of this hook.
#### Use in conftest plugins¶
Any conftest file can implement this hook. For a given collection path, only conftest files in parent directories of the collection path are consulted (if the path is a directory, its own conftest file is _not_ consulted - a directory cannot collect itself!).
pytest_collect_file(_file_path_ , _path_ , _parent_)[source]¶
    
Create a `Collector` for the given path, or None if not relevant.
For best results, the returned collector should be a subclass of `File`, but this is not required.
The new node needs to have the specified `parent` as a parent.
Parameters:
    
  * **file_path** (_pathlib.Path_) – The path to analyze.
  * **path** (_LEGACY_PATH_) – The path to collect (deprecated).


Changed in version 7.0.0: The `file_path` parameter was added as a `pathlib.Path` equivalent of the `path` parameter. The `path` parameter has been deprecated.
#### Use in conftest plugins¶
Any conftest file can implement this hook. For a given file path, only conftest files in parent directories of the file path are consulted.
pytest_pycollect_makemodule(_module_path_ , _path_ , _parent_)[source]¶
    
Return a `pytest.Module` collector or None for the given path.
This hook will be called for each matching test module path. The `pytest_collect_file` hook needs to be used if you want to create test modules for files that do not match as a test module.
Stops at first non-None result, see firstresult: stop at first non-None result.
Parameters:
    
  * **module_path** (_pathlib.Path_) – The path of the module to collect.
  * **path** (_LEGACY_PATH_) – The path of the module to collect (deprecated).


Changed in version 7.0.0: The `module_path` parameter was added as a `pathlib.Path` equivalent of the `path` parameter.
The `path` parameter has been deprecated in favor of `fspath`.
#### Use in conftest plugins¶
Any conftest file can implement this hook. For a given parent collector, only conftest files in the collector’s directory and its parent directories are consulted.
For influencing the collection of objects in Python modules you can use the following hook:
pytest_pycollect_makeitem(_collector_ , _name_ , _obj_)[source]¶
    
Return a custom item/collector for a Python object in a module, or None.
Stops at first non-None result, see firstresult: stop at first non-None result.
Parameters:
    
  * **collector** (_Module_ _|__Class_) – The module/class collector.
  * **name** (_str_) – The name of the object in the module/class.
  * **obj** (_object_) – The object.


Returns:
    
The created items/collectors.
Return type:
    
None | Item | Collector | list[Item | Collector]
#### Use in conftest plugins¶
Any conftest file can implement this hook. For a given collector, only conftest files in the collector’s directory and its parent directories are consulted.
pytest_generate_tests(_metafunc_)[source]¶
    
Generate (multiple) parametrized calls to a test function.
Parameters:
    
**metafunc** (_Metafunc_) – The `Metafunc` helper for the test function.
#### Use in conftest plugins¶
Any conftest file can implement this hook. For a given function definition, only conftest files in the functions’s directory and its parent directories are consulted.
pytest_make_parametrize_id(_config_ , _val_ , _argname_)[source]¶
    
Return a user-friendly string representation of the given `val` that will be used by @pytest.mark.parametrize calls, or None if the hook doesn’t know about `val`.
The parameter name is available as `argname`, if required.
Stops at first non-None result, see firstresult: stop at first non-None result.
Parameters:
    
  * **config** (_Config_) – The pytest config object.
  * **val** (_object_) – The parametrized value.
  * **argname** (_str_) – The automatic parameter name produced by pytest.


#### Use in conftest plugins¶
Any conftest file can implement this hook.
Hooks for influencing test skipping:
pytest_markeval_namespace(_config_)[source]¶
    
Called when constructing the globals dictionary used for evaluating string conditions in xfail/skipif markers.
This is useful when the condition for a marker requires objects that are expensive or impossible to obtain during collection time, which is required by normal boolean conditions.
Added in version 6.2.
Parameters:
    
**config** (_Config_) – The pytest config object.
Returns:
    
A dictionary of additional globals to add.
Return type:
    
dict[str, Any]
#### Use in conftest plugins¶
Any conftest file can implement this hook. For a given item, only conftest files in parent directories of the item are consulted.
After collection is complete, you can modify the order of items, delete or otherwise amend the test items:
pytest_collection_modifyitems(_session_ , _config_ , _items_)[source]¶
    
Called after collection has been performed. May filter or re-order the items in-place.
When items are deselected (filtered out from `items`), the hook `pytest_deselected` must be called explicitly with the deselected items to properly notify other plugins, e.g. with `config.hook.pytest_deselected(deselected_items)`.
Parameters:
    
  * **session** (_Session_) – The pytest session object.
  * **config** (_Config_) – The pytest config object.
  * **items** (_list_ _[__Item_ _]_) – List of item objects.


#### Use in conftest plugins¶
Any conftest plugin can implement this hook.
Note
If this hook is implemented in `conftest.py` files, it always receives all collected items, not only those under the `conftest.py` where it is implemented.
pytest_collection_finish(_session_)[source]¶
    
Called after collection has been performed and modified.
Parameters:
    
**session** (_Session_) – The pytest session object.
#### Use in conftest plugins¶
Any conftest plugin can implement this hook.
### Test running (runtest) hooks¶
All runtest related hooks receive a `pytest.Item` object.
pytest_runtestloop(_session_)[source]¶
    
Perform the main runtest loop (after collection finished).
The default hook implementation performs the runtest protocol for all items collected in the session (`session.items`), unless the collection failed or the `collectonly` pytest option is set.
If at any point `pytest.exit()` is called, the loop is terminated immediately.
If at any point `session.shouldfail` or `session.shouldstop` are set, the loop is terminated after the runtest protocol for the current item is finished.
Parameters:
    
**session** (_Session_) – The pytest session object.
Stops at first non-None result, see firstresult: stop at first non-None result. The return value is not used, but only stops further processing.
#### Use in conftest plugins¶
Any conftest file can implement this hook.
pytest_runtest_protocol(_item_ , _nextitem_)[source]¶
    
Perform the runtest protocol for a single test item.
The default runtest protocol is this (see individual hooks for full details):
  * `pytest_runtest_logstart(nodeid, location)`
  * Setup phase:
    
    * `call = pytest_runtest_setup(item)` (wrapped in `CallInfo(when="setup")`)
    * `report = pytest_runtest_makereport(item, call)`
    * `pytest_runtest_logreport(report)`
    * `pytest_exception_interact(call, report)` if an interactive exception occurred
  * Call phase, if the setup passed and the `setuponly` pytest option is not set:
    
    * `call = pytest_runtest_call(item)` (wrapped in `CallInfo(when="call")`)
    * `report = pytest_runtest_makereport(item, call)`
    * `pytest_runtest_logreport(report)`
    * `pytest_exception_interact(call, report)` if an interactive exception occurred
  * Teardown phase:
    
    * `call = pytest_runtest_teardown(item, nextitem)` (wrapped in `CallInfo(when="teardown")`)
    * `report = pytest_runtest_makereport(item, call)`
    * `pytest_runtest_logreport(report)`
    * `pytest_exception_interact(call, report)` if an interactive exception occurred
  * `pytest_runtest_logfinish(nodeid, location)`


Parameters:
    
  * **item** (_Item_) – Test item for which the runtest protocol is performed.
  * **nextitem** (_Item_ _|__None_) – The scheduled-to-be-next test item (or None if this is the end my friend).


Stops at first non-None result, see firstresult: stop at first non-None result. The return value is not used, but only stops further processing.
#### Use in conftest plugins¶
Any conftest file can implement this hook.
pytest_runtest_logstart(_nodeid_ , _location_)[source]¶
    
Called at the start of running the runtest protocol for a single item.
See `pytest_runtest_protocol` for a description of the runtest protocol.
Parameters:
    
  * **nodeid** (_str_) – Full node ID of the item.
  * **location** (_tuple_ _[__str_ _,__int_ _|__None_ _,__str_ _]_) – A tuple of `(filename, lineno, testname)` where `filename` is a file path relative to `config.rootpath` and `lineno` is 0-based.


#### Use in conftest plugins¶
Any conftest file can implement this hook. For a given item, only conftest files in the item’s directory and its parent directories are consulted.
pytest_runtest_logfinish(_nodeid_ , _location_)[source]¶
    
Called at the end of running the runtest protocol for a single item.
See `pytest_runtest_protocol` for a description of the runtest protocol.
Parameters:
    
  * **nodeid** (_str_) – Full node ID of the item.
  * **location** (_tuple_ _[__str_ _,__int_ _|__None_ _,__str_ _]_) – A tuple of `(filename, lineno, testname)` where `filename` is a file path relative to `config.rootpath` and `lineno` is 0-based.


#### Use in conftest plugins¶
Any conftest file can implement this hook. For a given item, only conftest files in the item’s directory and its parent directories are consulted.
pytest_runtest_setup(_item_)[source]¶
    
Called to perform the setup phase for a test item.
The default implementation runs `setup()` on `item` and all of its parents (which haven’t been setup yet). This includes obtaining the values of fixtures required by the item (which haven’t been obtained yet).
Parameters:
    
**item** (_Item_) – The item.
#### Use in conftest plugins¶
Any conftest file can implement this hook. For a given item, only conftest files in the item’s directory and its parent directories are consulted.
pytest_runtest_call(_item_)[source]¶
    
Called to run the test for test item (the call phase).
The default implementation calls `item.runtest()`.
Parameters:
    
**item** (_Item_) – The item.
#### Use in conftest plugins¶
Any conftest file can implement this hook. For a given item, only conftest files in the item’s directory and its parent directories are consulted.
pytest_runtest_teardown(_item_ , _nextitem_)[source]¶
    
Called to perform the teardown phase for a test item.
The default implementation runs the finalizers and calls `teardown()` on `item` and all of its parents (which need to be torn down). This includes running the teardown phase of fixtures required by the item (if they go out of scope).
Parameters:
    
  * **item** (_Item_) – The item.
  * **nextitem** (_Item_ _|__None_) – The scheduled-to-be-next test item (None if no further test item is scheduled). This argument is used to perform exact teardowns, i.e. calling just enough finalizers so that nextitem only needs to call setup functions.


#### Use in conftest plugins¶
Any conftest file can implement this hook. For a given item, only conftest files in the item’s directory and its parent directories are consulted.
pytest_runtest_makereport(_item_ , _call_)[source]¶
    
Called to create a `TestReport` for each of the setup, call and teardown runtest phases of a test item.
See `pytest_runtest_protocol` for a description of the runtest protocol.
Parameters:
    
  * **item** (_Item_) – The item.
  * **call** (_CallInfo_ _[__None_ _]_) – The `CallInfo` for the phase.


Stops at first non-None result, see firstresult: stop at first non-None result.
#### Use in conftest plugins¶
Any conftest file can implement this hook. For a given item, only conftest files in the item’s directory and its parent directories are consulted.
For deeper understanding you may look at the default implementation of these hooks in `_pytest.runner` and maybe also in `_pytest.pdb` which interacts with `_pytest.capture` and its input/output capturing in order to immediately drop into interactive debugging when a test failure occurs.
pytest_pyfunc_call(_pyfuncitem_)[source]¶
    
Call underlying test function.
Stops at first non-None result, see firstresult: stop at first non-None result.
Parameters:
    
**pyfuncitem** (_Function_) – The function item.
#### Use in conftest plugins¶
Any conftest file can implement this hook. For a given item, only conftest files in the item’s directory and its parent directories are consulted.
### Reporting hooks¶
Session related reporting hooks:
pytest_collectstart(_collector_)[source]¶
    
Collector starts collecting.
Parameters:
    
**collector** (_Collector_) – The collector.
#### Use in conftest plugins¶
Any conftest file can implement this hook. For a given collector, only conftest files in the collector’s directory and its parent directories are consulted.
pytest_make_collect_report(_collector_)[source]¶
    
Perform `collector.collect()` and return a `CollectReport`.
Stops at first non-None result, see firstresult: stop at first non-None result.
Parameters:
    
**collector** (_Collector_) – The collector.
#### Use in conftest plugins¶
Any conftest file can implement this hook. For a given collector, only conftest files in the collector’s directory and its parent directories are consulted.
pytest_itemcollected(_item_)[source]¶
    
We just collected a test item.
Parameters:
    
**item** (_Item_) – The item.
#### Use in conftest plugins¶
Any conftest file can implement this hook. For a given item, only conftest files in the item’s directory and its parent directories are consulted.
pytest_collectreport(_report_)[source]¶
    
Collector finished collecting.
Parameters:
    
**report** (_CollectReport_) – The collect report.
#### Use in conftest plugins¶
Any conftest file can implement this hook. For a given collector, only conftest files in the collector’s directory and its parent directories are consulted.
pytest_deselected(_items_)[source]¶
    
Called for deselected test items, e.g. by keyword.
Note that this hook has two integration aspects for plugins:
  * it can be _implemented_ to be notified of deselected items
  * it must be _called_ from `pytest_collection_modifyitems` implementations when items are deselected (to properly notify other plugins).


May be called multiple times.
Parameters:
    
**items** (_Sequence_ _[__Item_ _]_) – The items.
#### Use in conftest plugins¶
Any conftest file can implement this hook.
pytest_report_header(_config_ , _start_path_ , _startdir_)[source]¶
    
Return a string or list of strings to be displayed as header info for terminal reporting.
Parameters:
    
  * **config** (_Config_) – The pytest config object.
  * **start_path** (_pathlib.Path_) – The starting dir.
  * **startdir** (_LEGACY_PATH_) – The starting dir (deprecated).


Note
Lines returned by a plugin are displayed before those of plugins which ran before it. If you want to have your line(s) displayed first, use trylast=True.
Changed in version 7.0.0: The `start_path` parameter was added as a `pathlib.Path` equivalent of the `startdir` parameter. The `startdir` parameter has been deprecated.
#### Use in conftest plugins¶
This hook is only called for initial conftests.
pytest_report_collectionfinish(_config_ , _start_path_ , _startdir_ , _items_)[source]¶
    
Return a string or list of strings to be displayed after collection has finished successfully.
These strings will be displayed after the standard “collected X items” message.
Added in version 3.2.
Parameters:
    
  * **config** (_Config_) – The pytest config object.
  * **start_path** (_pathlib.Path_) – The starting dir.
  * **startdir** (_LEGACY_PATH_) – The starting dir (deprecated).
  * **items** (_Sequence_ _[__Item_ _]_) – List of pytest items that are going to be executed; this list should not be modified.


Note
Lines returned by a plugin are displayed before those of plugins which ran before it. If you want to have your line(s) displayed first, use trylast=True.
Changed in version 7.0.0: The `start_path` parameter was added as a `pathlib.Path` equivalent of the `startdir` parameter. The `startdir` parameter has been deprecated.
#### Use in conftest plugins¶
Any conftest plugin can implement this hook.
pytest_report_teststatus(_report_ , _config_)[source]¶
    
Return result-category, shortletter and verbose word for status reporting.
The result-category is a category in which to count the result, for example “passed”, “skipped”, “error” or the empty string.
The shortletter is shown as testing progresses, for example “.”, “s”, “E” or the empty string.
The verbose word is shown as testing progresses in verbose mode, for example “PASSED”, “SKIPPED”, “ERROR” or the empty string.
pytest may style these implicitly according to the report outcome. To provide explicit styling, return a tuple for the verbose word, for example `"rerun", "R", ("RERUN", {"yellow": True})`.
Parameters:
    
  * **report** (_CollectReport_ _|__TestReport_) – The report object whose status is to be returned.
  * **config** (_Config_) – The pytest config object.


Returns:
    
The test status.
Return type:
    
TestShortLogReport | tuple[str, str, str | tuple[str, Mapping[str, bool]]]
Stops at first non-None result, see firstresult: stop at first non-None result.
#### Use in conftest plugins¶
Any conftest plugin can implement this hook.
pytest_report_to_serializable(_config_ , _report_)[source]¶
    
Serialize the given report object into a data structure suitable for sending over the wire, e.g. converted to JSON.
Parameters:
    
  * **config** (_Config_) – The pytest config object.
  * **report** (_CollectReport_ _|__TestReport_) – The report.


#### Use in conftest plugins¶
Any conftest file can implement this hook. The exact details may depend on the plugin which calls the hook.
pytest_report_from_serializable(_config_ , _data_)[source]¶
    
Restore a report object previously serialized with `pytest_report_to_serializable`.
Parameters:
    
**config** (_Config_) – The pytest config object.
#### Use in conftest plugins¶
Any conftest file can implement this hook. The exact details may depend on the plugin which calls the hook.
pytest_terminal_summary(_terminalreporter_ , _exitstatus_ , _config_)[source]¶
    
Add a section to terminal summary reporting.
Parameters:
    
  * **terminalreporter** (_TerminalReporter_) – The internal terminal reporter object.
  * **exitstatus** (_ExitCode_) – The exit status that will be reported back to the OS.
  * **config** (_Config_) – The pytest config object.


Added in version 4.2: The `config` parameter.
#### Use in conftest plugins¶
Any conftest plugin can implement this hook.
pytest_fixture_setup(_fixturedef_ , _request_)[source]¶
    
Perform fixture setup execution.
Parameters:
    
  * **fixturedef** (_FixtureDef_ _[__Any_ _]_) – The fixture definition object.
  * **request** (_SubRequest_) – The fixture request object.


Returns:
    
The return value of the call to the fixture function.
Return type:
    
object | None
Stops at first non-None result, see firstresult: stop at first non-None result.
Note
If the fixture function returns None, other implementations of this hook function will continue to be called, according to the behavior of the firstresult: stop at first non-None result option.
#### Use in conftest plugins¶
Any conftest file can implement this hook. For a given fixture, only conftest files in the fixture scope’s directory and its parent directories are consulted.
pytest_fixture_post_finalizer(_fixturedef_ , _request_)[source]¶
    
Called after fixture teardown, but before the cache is cleared, so the fixture result `fixturedef.cached_result` is still available (not `None`).
Parameters:
    
  * **fixturedef** (_FixtureDef_ _[__Any_ _]_) – The fixture definition object.
  * **request** (_SubRequest_) – The fixture request object.


#### Use in conftest plugins¶
Any conftest file can implement this hook. For a given fixture, only conftest files in the fixture scope’s directory and its parent directories are consulted.
pytest_warning_recorded(_warning_message_ , _when_ , _nodeid_ , _location_)[source]¶
    
Process a warning captured by the internal pytest warnings plugin.
Parameters:
    
  * **warning_message** (_warnings.WarningMessage_) – The captured warning. This is the same object produced by `warnings.catch_warnings`, and contains the same attributes as the parameters of `warnings.showwarning()`.
  * **when** (_Literal_ _[__'config'__,__'collect'__,__'runtest'__]_) – 
Indicates when the warning was captured. Possible values:
    * `"config"`: during pytest configuration/initialization stage.
    * `"collect"`: during test collection.
    * `"runtest"`: during test execution.
  * **nodeid** (_str_) – Full id of the item. Empty string for warnings that are not specific to a particular node.
  * **location** (_tuple_ _[__str_ _,__int_ _,__str_ _]__|__None_) – When available, holds information about the execution context of the captured warning (filename, linenumber, function). `function` evaluates to <module> when the execution context is at the module level.


Added in version 6.0.
#### Use in conftest plugins¶
Any conftest file can implement this hook. If the warning is specific to a particular node, only conftest files in parent directories of the node are consulted.
Central hook for reporting about test execution:
pytest_runtest_logreport(_report_)[source]¶
    
Process the `TestReport` produced for each of the setup, call and teardown runtest phases of an item.
See `pytest_runtest_protocol` for a description of the runtest protocol.
#### Use in conftest plugins¶
Any conftest file can implement this hook. For a given item, only conftest files in the item’s directory and its parent directories are consulted.
Assertion related hooks:
pytest_assertrepr_compare(_config_ , _op_ , _left_ , _right_)[source]¶
    
Return explanation for comparisons in failing assert expressions.
Return None for no custom explanation, otherwise return a list of strings. The strings will be joined by newlines but any newlines _in_ a string will be escaped. Note that all but the first line will be indented slightly, the intention is for the first line to be a summary.
Parameters:
    
  * **config** (_Config_) – The pytest config object.
  * **op** (_str_) – The operator, e.g. `"=="`, `"!="`, `"not in"`.
  * **left** (_object_) – The left operand.
  * **right** (_object_) – The right operand.


#### Use in conftest plugins¶
Any conftest file can implement this hook. For a given item, only conftest files in the item’s directory and its parent directories are consulted.
pytest_assertion_pass(_item_ , _lineno_ , _orig_ , _expl_)[source]¶
    
Called whenever an assertion passes.
Added in version 5.0.
Use this hook to do some processing after a passing assertion. The original assertion information is available in the `orig` string and the pytest introspected assertion information is available in the `expl` string.
This hook must be explicitly enabled by the `enable_assertion_pass_hook` ini-file option:
```
[pytest]
enable_assertion_pass_hook=true

```

You need to **clean the .pyc** files in your project directory and interpreter libraries when enabling this option, as assertions will require to be re-written.
Parameters:
    
  * **item** (_Item_) – pytest item object of current test.
  * **lineno** (_int_) – Line number of the assert statement.
  * **orig** (_str_) – String with the original assertion.
  * **expl** (_str_) – String with the assert explanation.


#### Use in conftest plugins¶
Any conftest file can implement this hook. For a given item, only conftest files in the item’s directory and its parent directories are consulted.
### Debugging/Interaction hooks¶
There are few hooks which can be used for special reporting or interaction with exceptions:
pytest_internalerror(_excrepr_ , _excinfo_)[source]¶
    
Called for internal errors.
Return True to suppress the fallback handling of printing an INTERNALERROR message directly to sys.stderr.
Parameters:
    
  * **excrepr** (_ExceptionRepr_) – The exception repr object.
  * **excinfo** (_ExceptionInfo_ _[__BaseException_ _]_) – The exception info.


#### Use in conftest plugins¶
Any conftest plugin can implement this hook.
pytest_keyboard_interrupt(_excinfo_)[source]¶
    
Called for keyboard interrupt.
Parameters:
    
**excinfo** (_ExceptionInfo_ _[__KeyboardInterrupt_ _|__Exit_ _]_) – The exception info.
#### Use in conftest plugins¶
Any conftest plugin can implement this hook.
pytest_exception_interact(_node_ , _call_ , _report_)[source]¶
    
Called when an exception was raised which can potentially be interactively handled.
May be called during collection (see `pytest_make_collect_report`), in which case `report` is a `CollectReport`.
May be called during runtest of an item (see `pytest_runtest_protocol`), in which case `report` is a `TestReport`.
This hook is not called if the exception that was raised is an internal exception like `skip.Exception`.
Parameters:
    
  * **node** (_Item_ _|__Collector_) – The item or collector.
  * **call** (_CallInfo_ _[__Any_ _]_) – The call information. Contains the exception.
  * **report** (_CollectReport_ _|__TestReport_) – The collection or test report.


#### Use in conftest plugins¶
Any conftest file can implement this hook. For a given node, only conftest files in parent directories of the node are consulted.
pytest_enter_pdb(_config_ , _pdb_)[source]¶
    
Called upon pdb.set_trace().
Can be used by plugins to take special action just before the python debugger enters interactive mode.
Parameters:
    
  * **config** (_Config_) – The pytest config object.
  * **pdb** (_pdb.Pdb_) – The Pdb instance.


#### Use in conftest plugins¶
Any conftest plugin can implement this hook.
pytest_leave_pdb(_config_ , _pdb_)[source]¶
    
Called when leaving pdb (e.g. with continue after pdb.set_trace()).
Can be used by plugins to take special action just after the python debugger leaves interactive mode.
Parameters:
    
  * **config** (_Config_) – The pytest config object.
  * **pdb** (_pdb.Pdb_) – The Pdb instance.


#### Use in conftest plugins¶
Any conftest plugin can implement this hook.
## Collection tree objects¶
These are the collector and item classes (collectively called “nodes”) which make up the collection tree.
### Node¶
_class_ Node[source]¶
    
Bases: `ABC`
Base class of `Collector` and `Item`, the components of the test collection tree.
`Collector`'s are the internal nodes of the tree, and `Item`'s are the leaf nodes.
fspath _: LEGACY_PATH_¶
    
A `LEGACY_PATH` copy of the `path` attribute. Intended for usage for methods not migrated to `pathlib.Path` yet, such as `Item.reportinfo`. Will be deprecated in a future release, prefer using `path` instead.
name _: str_¶
    
A unique name within the scope of the parent node.
parent¶
    
The parent collector node.
config _: Config_¶
    
The pytest config object.
session _: Session_¶
    
The pytest session this node is part of.
path _: pathlib.Path_¶
    
Filesystem path where this node was collected from (can be None).
keywords _: MutableMapping[str,Any]_¶
    
Keywords/markers collected from all scopes.
own_markers _: list[Mark]_¶
    
The marker objects belonging to this node.
extra_keyword_matches _: set[str]_¶
    
Allow adding of extra keywords to use for matching.
stash _: Stash_¶
    
A place where plugins can store information on the node for their own use.
_classmethod _from_parent(_parent_ , _** kw_)[source]¶
    
Public constructor for Nodes.
This indirection got introduced in order to enable removing the fragile logic from the node constructors.
Subclasses can use `super().from_parent(...)` when overriding the construction.
Parameters:
    
**parent** (_Node_) – The parent node of this Node.
_property_ ihook _: HookRelay_¶
    
fspath-sensitive hook proxy used to call pytest hooks.
warn(_warning_)[source]¶
    
Issue a warning for this Node.
Warnings will be displayed after the test session, unless explicitly suppressed.
Parameters:
    
**warning** (_Warning_) – The warning instance to issue.
Raises:
    
**ValueError** – If `warning` instance is not a subclass of Warning.
Example usage:
```
node.warn(PytestWarning("some message"))
node.warn(UserWarning("some message"))

```

Changed in version 6.2: Any subclass of `Warning` is now accepted, rather than only `PytestWarning` subclasses.
_property_ nodeid _: str_¶
    
A ::-separated string denoting its collection tree address.
_for ... in _iter_parents()[source]¶
    
Iterate over all parent collectors starting from and including self up to the root of the collection tree.
Added in version 8.1.
listchain()[source]¶
    
Return a list of all parent collectors starting from the root of the collection tree down to and including self.
add_marker(_marker_ , _append =True_)[source]¶
    
Dynamically add a marker object to the node.
Parameters:
    
  * **marker** (_str_ _|__MarkDecorator_) – The marker.
  * **append** (_bool_) – Whether to append the marker, or prepend it.


iter_markers(_name =None_)[source]¶
    
Iterate over all markers of the node.
Parameters:
    
**name** (_str_ _|__None_) – If given, filter the results by the name attribute.
Returns:
    
An iterator of the markers of the node.
Return type:
    
_Iterator_[_Mark_]
_for ... in _iter_markers_with_node(_name =None_)[source]¶
    
Iterate over all markers of the node.
Parameters:
    
**name** (_str_ _|__None_) – If given, filter the results by the name attribute.
Returns:
    
An iterator of (node, mark) tuples.
Return type:
    
_Iterator_[tuple[_Node_, _Mark_]]
get_closest_marker(_name :str_) → Mark|None[source]¶
get_closest_marker(_name :str_, _default :Mark_) → Mark
    
Return the first marker matching the name, from closest (for example function) to farther level (for example module level).
Parameters:
    
  * **default** – Fallback return value if no marker was found.
  * **name** – Name to filter by.


listextrakeywords()[source]¶
    
Return a set of all extra keywords in self and any parents.
addfinalizer(_fin_)[source]¶
    
Register a function to be called without arguments when this node is finalized.
This method can only be called when this node is active in a setup chain, for example during self.setup().
getparent(_cls_)[source]¶
    
Get the closest parent node (including self) which is an instance of the given class.
Parameters:
    
**cls** (_type_ _[___NodeType_ _]_) – The node class to search for.
Returns:
    
The node, if found.
Return type:
    
__NodeType_ | None
repr_failure(_excinfo_ , _style =None_)[source]¶
    
Return a representation of a collection or test failure.
See also
Working with non-python tests
Parameters:
    
**excinfo** (_ExceptionInfo_ _[__BaseException_ _]_) – Exception information for the failure.
### Collector¶
_class_ Collector[source]¶
    
Bases: `Node`, `ABC`
Base class of all collectors.
Collector create children through `collect()` and thus iteratively build the collection tree.
_exception_ CollectError[source]¶
    
Bases: `Exception`
An error during collection, contains a custom message.
_abstractmethod _collect()[source]¶
    
Collect children (items and collectors) for this collector.
repr_failure(_excinfo_)[source]¶
    
Return a representation of a collection failure.
Parameters:
    
**excinfo** (_ExceptionInfo_ _[__BaseException_ _]_) – Exception information for the failure.
name _: str_¶
    
A unique name within the scope of the parent node.
parent¶
    
The parent collector node.
config _: Config_¶
    
The pytest config object.
session _: Session_¶
    
The pytest session this node is part of.
path _: pathlib.Path_¶
    
Filesystem path where this node was collected from (can be None).
### Item¶
_class_ Item[source]¶
    
Bases: `Node`, `ABC`
Base class of all test invocation items.
Note that for a single function there might be multiple test invocation items.
user_properties _: list[tuple[str,object]]_¶
    
A list of tuples (name, value) that holds user defined properties for this test.
name _: str_¶
    
A unique name within the scope of the parent node.
parent¶
    
The parent collector node.
config _: Config_¶
    
The pytest config object.
session _: Session_¶
    
The pytest session this node is part of.
path _: pathlib.Path_¶
    
Filesystem path where this node was collected from (can be None).
_abstractmethod _runtest()[source]¶
    
Run the test case for this item.
Must be implemented by subclasses.
See also
Working with non-python tests
add_report_section(_when_ , _key_ , _content_)[source]¶
    
Add a new report section, similar to what’s done internally to add stdout and stderr captured output:
```
item.add_report_section("call", "stdout", "report section contents")

```

Parameters:
    
  * **when** (_str_) – One of the possible capture states, `"setup"`, `"call"`, `"teardown"`.
  * **key** (_str_) – Name of the section, can be customized at will. Pytest uses `"stdout"` and `"stderr"` internally.
  * **content** (_str_) – The full contents as a string.


reportinfo()[source]¶
    
Get location information for this item for test reports.
Returns a tuple with three elements:
  * The path of the test (default `self.path`)
  * The 0-based line number of the test (default `None`)
  * A name of the test to be shown (default `""`)


See also
Working with non-python tests
_property_ location _: tuple[str,int|None,str]_¶
    
Returns a tuple of `(relfspath, lineno, testname)` for this item where `relfspath` is file path relative to `config.rootpath` and lineno is a 0-based line number.
### File¶
_class_ File[source]¶
    
Bases: `FSCollector`, `ABC`
Base class for collecting tests from a file.
Working with non-python tests.
name _: str_¶
    
A unique name within the scope of the parent node.
parent¶
    
The parent collector node.
config _: Config_¶
    
The pytest config object.
session _: Session_¶
    
The pytest session this node is part of.
path _: pathlib.Path_¶
    
Filesystem path where this node was collected from (can be None).
### FSCollector¶
_class_ FSCollector[source]¶
    
Bases: `Collector`, `ABC`
Base class for filesystem collectors.
path _: pathlib.Path_¶
    
Filesystem path where this node was collected from (can be None).
_classmethod _from_parent(_parent_ , _*_ , _fspath =None_, _path =None_, _** kw_)[source]¶
    
The public constructor.
name _: str_¶
    
A unique name within the scope of the parent node.
parent¶
    
The parent collector node.
config _: Config_¶
    
The pytest config object.
session _: Session_¶
    
The pytest session this node is part of.
### Session¶
_final class_Session[source]¶
    
Bases: `Collector`
The root of the collection tree.
`Session` collects the initial paths given as arguments to pytest.
_exception_ Interrupted¶
    
Bases: `KeyboardInterrupt`
Signals that the test run was interrupted.
_exception_ Failed¶
    
Bases: `Exception`
Signals a stop as failed test run.
_property_ startpath _: Path_¶
    
The path from which pytest was invoked.
Added in version 7.0.0.
isinitpath(_path_ , _*_ , _with_parents =False_)[source]¶
    
Is path an initial path?
An initial path is a path explicitly given to pytest on the command line.
Parameters:
    
**with_parents** (_bool_) – If set, also return True if the path is a parent of an initial path.
Changed in version 8.0: Added the `with_parents` parameter.
perform_collect(_args :Sequence[str]|None=None_, _genitems :Literal[True]=True_) → Sequence[Item][source]¶
perform_collect(_args :Sequence[str]|None=None_, _genitems :bool=True_) → Sequence[Item|Collector]
    
Perform the collection phase for this session.
This is called by the default `pytest_collection` hook implementation; see the documentation of this hook for more details. For testing purposes, it may also be called directly on a fresh `Session`.
This function normally recursively expands any collectors collected from the session to their items, and only items are returned. For testing purposes, this may be suppressed by passing `genitems=False`, in which case the return value contains these collectors unexpanded, and `session.items` is empty.
_for ... in _collect()[source]¶
    
Collect children (items and collectors) for this collector.
name _: str_¶
    
A unique name within the scope of the parent node.
parent¶
    
The parent collector node.
config _: Config_¶
    
The pytest config object.
session _: Session_¶
    
The pytest session this node is part of.
path _: pathlib.Path_¶
    
Filesystem path where this node was collected from (can be None).
### Package¶
_class_ Package[source]¶
    
Bases: `Directory`
Collector for files and directories in a Python packages – directories with an `__init__.py` file.
Note
Directories without an `__init__.py` file are instead collected by `Dir` by default. Both are `Directory` collectors.
Changed in version 8.0: Now inherits from `Directory`.
_for ... in _collect()[source]¶
    
Collect children (items and collectors) for this collector.
name _: str_¶
    
A unique name within the scope of the parent node.
parent¶
    
The parent collector node.
config _: Config_¶
    
The pytest config object.
session _: Session_¶
    
The pytest session this node is part of.
path _: pathlib.Path_¶
    
Filesystem path where this node was collected from (can be None).
### Module¶
_class_ Module[source]¶
    
Bases: `File`, `PyCollector`
Collector for test classes and functions in a Python module.
collect()[source]¶
    
Collect children (items and collectors) for this collector.
name _: str_¶
    
A unique name within the scope of the parent node.
parent¶
    
The parent collector node.
config _: Config_¶
    
The pytest config object.
session _: Session_¶
    
The pytest session this node is part of.
path _: pathlib.Path_¶
    
Filesystem path where this node was collected from (can be None).
### Class¶
_class_ Class[source]¶
    
Bases: `PyCollector`
Collector for test methods (and nested classes) in a Python class.
_classmethod _from_parent(_parent_ , _*_ , _name_ , _obj =None_, _** kw_)[source]¶
    
The public constructor.
collect()[source]¶
    
Collect children (items and collectors) for this collector.
name _: str_¶
    
A unique name within the scope of the parent node.
parent¶
    
The parent collector node.
config _: Config_¶
    
The pytest config object.
session _: Session_¶
    
The pytest session this node is part of.
path _: pathlib.Path_¶
    
Filesystem path where this node was collected from (can be None).
### Function¶
_class_ Function[source]¶
    
Bases: `PyobjMixin`, `Item`
Item responsible for setting up and executing a Python test function.
Parameters:
    
  * **name** – The full function name, including any decorations like those added by parametrization (`my_func[my_param]`).
  * **parent** – The parent Node.
  * **config** – The pytest Config object.
  * **callspec** – If given, this function has been parametrized and the callspec contains meta information about the parametrization.
  * **callobj** – If given, the object which will be called when the Function is invoked, otherwise the callobj will be obtained from `parent` using `originalname`.
  * **keywords** – Keywords bound to the function object for “-k” matching.
  * **session** – The pytest Session object.
  * **fixtureinfo** – Fixture information already resolved at this fixture node..
  * **originalname** – The attribute name to use for accessing the underlying function object. Defaults to `name`. Set this if name is different from the original name, for example when it contains decorations like those added by parametrization (`my_func[my_param]`).


originalname¶
    
Original function name, without any decorations (for example parametrization adds a `"[...]"` suffix to function names), used to access the underlying function object from `parent` (in case `callobj` is not given explicitly).
Added in version 3.0.
_classmethod _from_parent(_parent_ , _** kw_)[source]¶
    
The public constructor.
_property_ function¶
    
Underlying python ‘function’ object.
_property_ instance¶
    
Python instance object the function is bound to.
Returns None if not a test method, e.g. for a standalone test function, a class or a module.
runtest()[source]¶
    
Execute the underlying test function.
repr_failure(_excinfo_)[source]¶
    
Return a representation of a collection or test failure.
See also
Working with non-python tests
Parameters:
    
**excinfo** (_ExceptionInfo_ _[__BaseException_ _]_) – Exception information for the failure.
name _: str_¶
    
A unique name within the scope of the parent node.
parent¶
    
The parent collector node.
config _: Config_¶
    
The pytest config object.
session _: Session_¶
    
The pytest session this node is part of.
path _: pathlib.Path_¶
    
Filesystem path where this node was collected from (can be None).
### FunctionDefinition¶
_class_ FunctionDefinition[source]¶
    
Bases: `Function`
This class is a stop gap solution until we evolve to have actual function definition nodes and manage to get rid of `metafunc`.
runtest()[source]¶
    
Execute the underlying test function.
name _: str_¶
    
A unique name within the scope of the parent node.
parent¶
    
The parent collector node.
config _: Config_¶
    
The pytest config object.
session _: Session_¶
    
The pytest session this node is part of.
path _: pathlib.Path_¶
    
Filesystem path where this node was collected from (can be None).
setup()¶
    
Execute the underlying test function.
## Objects¶
Objects accessible from fixtures or hooks or importable from `pytest`.
### CallInfo¶
_final class_CallInfo[source]¶
    
Result/Exception info of a function invocation.
excinfo _: ExceptionInfo[BaseException]|None_¶
    
The captured exception of the call, if it raised.
start _: float_¶
    
The system time when the call started, in seconds since the epoch.
stop _: float_¶
    
The system time when the call ended, in seconds since the epoch.
duration _: float_¶
    
The call duration, in seconds.
when _: Literal['collect','setup','call','teardown']_¶
    
The context of invocation: “collect”, “setup”, “call” or “teardown”.
_property_ result _: TResult_¶
    
The return value of the call, if it didn’t raise.
Can only be accessed if excinfo is None.
_classmethod _from_call(_func_ , _when_ , _reraise =None_)[source]¶
    
Call func, wrapping the result in a CallInfo.
Parameters:
    
  * **func** (_Callable_ _[__[__]__,___pytest.runner.TResult_ _]_) – The function to call. Called without arguments.
  * **when** (_Literal_ _[__'collect'__,__'setup'__,__'call'__,__'teardown'__]_) – The phase in which the function is called.
  * **reraise** (_type_ _[__BaseException_ _]__|__tuple_ _[__type_ _[__BaseException_ _]__,__...__]__|__None_) – Exception or exceptions that shall propagate if raised by the function, instead of being wrapped in the CallInfo.


### CollectReport¶
_final class_CollectReport[source]¶
    
Bases: `BaseReport`
Collection report object.
Reports can contain arbitrary extra attributes.
nodeid _: str_¶
    
Normalized collection nodeid.
outcome _: Literal['passed','failed','skipped']_¶
    
Test outcome, always one of “passed”, “failed”, “skipped”.
longrepr _: None|ExceptionInfo[BaseException]|tuple[str,int,str]|str|TerminalRepr_¶
    
None or a failure representation.
result¶
    
The collected items and collection nodes.
sections _: list[tuple[str,str]]_¶
    
Tuples of str `(heading, content)` with extra information for the test report. Used by pytest to add text captured from `stdout`, `stderr`, and intercepted logging events. May be used by other plugins to add arbitrary information to reports.
_property_ caplog _: str_¶
    
Return captured log lines, if log capturing is enabled.
Added in version 3.5.
_property_ capstderr _: str_¶
    
Return captured text from stderr, if capturing is enabled.
Added in version 3.0.
_property_ capstdout _: str_¶
    
Return captured text from stdout, if capturing is enabled.
Added in version 3.0.
_property_ count_towards_summary _: bool_¶
    
**Experimental** Whether this report should be counted towards the totals shown at the end of the test session: “1 passed, 1 failure, etc”.
Note
This function is considered **experimental** , so beware that it is subject to changes even in patch releases.
_property_ failed _: bool_¶
    
Whether the outcome is failed.
_property_ fspath _: str_¶
    
The path portion of the reported node, as a string.
_property_ head_line _: str|None_¶
    
**Experimental** The head line shown with longrepr output for this report, more commonly during traceback representation during failures:
```
________ Test.foo ________

```

In the example above, the head_line is “Test.foo”.
Note
This function is considered **experimental** , so beware that it is subject to changes even in patch releases.
_property_ longreprtext _: str_¶
    
Read-only property that returns the full string representation of `longrepr`.
Added in version 3.0.
_property_ passed _: bool_¶
    
Whether the outcome is passed.
_property_ skipped _: bool_¶
    
Whether the outcome is skipped.
### Config¶
_final class_Config[source]¶
    
Access to configuration values, pluginmanager and plugin hooks.
Parameters:
    
  * **pluginmanager** (_PytestPluginManager_) – A pytest PluginManager.
  * **invocation_params** (_InvocationParams_) – Object containing parameters regarding the `pytest.main()` invocation.


_final class_InvocationParams(_*_ , _args_ , _plugins_ , _dir_)[source]¶
    
Holds parameters passed during `pytest.main()`.
The object attributes are read-only.
Added in version 5.1.
Note
Note that the environment variable `PYTEST_ADDOPTS` and the `addopts` ini option are handled by pytest, not being included in the `args` attribute.
Plugins accessing `InvocationParams` must be aware of that.
args _: tuple[str,...]_¶
    
The command-line arguments as passed to `pytest.main()`.
plugins _: Sequence[str|object]|None_¶
    
Extra plugins, might be `None`.
dir _: Path_¶
    
The directory from which `pytest.main()` was invoked. :type: pathlib.Path
_class_ ArgsSource(_value_ , _names= <not given>_, _*values_ , _module=None_ , _qualname=None_ , _type=None_ , _start=1_ , _boundary=None_)[source]¶
    
Indicates the source of the test arguments.
Added in version 7.2.
ARGS _= 1_¶
    
Command line arguments.
INVOCATION_DIR _= 2_¶
    
Invocation directory.
TESTPATHS _= 3_¶
    
‘testpaths’ configuration value.
option¶
    
Access to command line option as attributes.
Type:
    
argparse.Namespace
invocation_params¶
    
The parameters with which pytest was invoked.
Type:
    
InvocationParams
pluginmanager¶
    
The plugin manager handles plugin registration and hook invocation.
Type:
    
PytestPluginManager
stash¶
    
A place where plugins can store information on the config for their own use.
Type:
    
Stash
_property_ rootpath _: Path_¶
    
The path to the rootdir.
Type:
    
pathlib.Path
Added in version 6.1.
_property_ inipath _: Path|None_¶
    
The path to the configfile.
Added in version 6.1.
add_cleanup(_func_)[source]¶
    
Add a function to be called when the config object gets out of use (usually coinciding with pytest_unconfigure).
_classmethod _fromdictargs(_option_dict_ , _args_)[source]¶
    
Constructor usable for subprocesses.
issue_config_time_warning(_warning_ , _stacklevel_)[source]¶
    
Issue and handle a warning during the “configure” stage.
During `pytest_configure` we can’t capture warnings using the `catch_warnings_for_item` function because it is not possible to have hook wrappers around `pytest_configure`.
This function is mainly intended for plugins that need to issue warnings during `pytest_configure` (or similar stages).
Parameters:
    
  * **warning** (_Warning_) – The warning instance.
  * **stacklevel** (_int_) – stacklevel forwarded to warnings.warn.


addinivalue_line(_name_ , _line_)[source]¶
    
Add a line to an ini-file option. The option must have been declared but might not yet be set in which case the line becomes the first line in its value.
getini(_name_)[source]¶
    
Return configuration value from an ini file.
If a configuration value is not defined in an ini file, then the `default` value provided while registering the configuration through `parser.addini` will be returned. Please note that you can even provide `None` as a valid default value.
If `default` is not provided while registering using `parser.addini`, then a default value based on the `type` parameter passed to `parser.addini` will be returned. The default values based on `type` are: `paths`, `pathlist`, `args` and `linelist` : empty list `[]` `bool` : `False` `string` : empty string `""`
If neither the `default` nor the `type` parameter is passed while registering the configuration through `parser.addini`, then the configuration is treated as a string and a default empty string ‘’ is returned.
If the specified name hasn’t been registered through a prior `parser.addini` call (usually from a plugin), a ValueError is raised.
getoption(_name_ , _default= <NOTSET>_, _skip=False_)[source]¶
    
Return command line option value.
Parameters:
    
  * **name** (_str_) – Name of the option. You may also specify the literal `--OPT` option instead of the “dest” option name.
  * **default** – Fallback value if no option of that name is **declared** via `pytest_addoption`. Note this parameter will be ignored when the option is **declared** even if the option’s value is `None`.
  * **skip** (_bool_) – If `True`, raise `pytest.skip()` if option is undeclared or has a `None` value. Note that even if `True`, if a default was specified it will be returned instead of a skip.


getvalue(_name_ , _path =None_)[source]¶
    
Deprecated, use getoption() instead.
getvalueorskip(_name_ , _path =None_)[source]¶
    
Deprecated, use getoption(skip=True) instead.
VERBOSITY_ASSERTIONS _: Final_ _= 'assertions'_¶
    
Verbosity type for failed assertions (see `verbosity_assertions`).
VERBOSITY_TEST_CASES _: Final_ _= 'test_cases'_¶
    
Verbosity type for test case execution (see `verbosity_test_cases`).
get_verbosity(_verbosity_type =None_)[source]¶
    
Retrieve the verbosity level for a fine-grained verbosity type.
Parameters:
    
**verbosity_type** (_str_ _|__None_) – Verbosity type to get level for. If a level is configured for the given type, that value will be returned. If the given type is not a known verbosity type, the global verbosity level will be returned. If the given type is None (default), the global verbosity level will be returned.
To configure a level for a fine-grained verbosity type, the configuration file should have a setting for the configuration name and a numeric value for the verbosity level. A special value of “auto” can be used to explicitly use the global verbosity level.
Example:
```
# content of pytest.ini
[pytest]
verbosity_assertions=2

```

```
pytest -v

```

```
print(config.get_verbosity()) # 1
print(config.get_verbosity(Config.VERBOSITY_ASSERTIONS)) # 2

```

### Dir¶
_final class_Dir[source]¶
    
Collector of files in a file system directory.
Added in version 8.0.
Note
Python directories with an `__init__.py` file are instead collected by `Package` by default. Both are `Directory` collectors.
_classmethod _from_parent(_parent_ , _*_ , _path_)[source]¶
    
The public constructor.
Parameters:
    
  * **parent** (_nodes.Collector_) – The parent collector of this Dir.
  * **path** (_pathlib.Path_) – The directory’s path.


_for ... in _collect()[source]¶
    
Collect children (items and collectors) for this collector.
name _: str_¶
    
A unique name within the scope of the parent node.
parent¶
    
The parent collector node.
config _: Config_¶
    
The pytest config object.
session _: Session_¶
    
The pytest session this node is part of.
path _: pathlib.Path_¶
    
Filesystem path where this node was collected from (can be None).
### Directory¶
_class_ Directory[source]¶
    
Base class for collecting files from a directory.
A basic directory collector does the following: goes over the files and sub-directories in the directory and creates collectors for them by calling the hooks `pytest_collect_directory` and `pytest_collect_file`, after checking that they are not ignored using `pytest_ignore_collect`.
The default directory collectors are `Dir` and `Package`.
Added in version 8.0.
Using a custom directory collector.
name _: str_¶
    
A unique name within the scope of the parent node.
parent¶
    
The parent collector node.
config _: Config_¶
    
The pytest config object.
session _: Session_¶
    
The pytest session this node is part of.
path _: pathlib.Path_¶
    
Filesystem path where this node was collected from (can be None).
### ExceptionInfo¶
_final class_ExceptionInfo[source]¶
    
Wraps sys.exc_info() objects and offers help for navigating the traceback.
_classmethod _from_exception(_exception_ , _exprinfo =None_)[source]¶
    
Return an ExceptionInfo for an existing exception.
The exception must have a non-`None` `__traceback__` attribute, otherwise this function fails with an assertion error. This means that the exception must have been raised, or added a traceback with the `with_traceback()` method.
Parameters:
    
**exprinfo** (_str_ _|__None_) – A text string helping to determine if we should strip `AssertionError` from the output. Defaults to the exception message/`__str__()`.
Added in version 7.4.
_classmethod _from_exc_info(_exc_info_ , _exprinfo =None_)[source]¶
    
Like `from_exception()`, but using old-style exc_info tuple.
_classmethod _from_current(_exprinfo =None_)[source]¶
    
Return an ExceptionInfo matching the current traceback.
Warning
Experimental API
Parameters:
    
**exprinfo** (_str_ _|__None_) – A text string helping to determine if we should strip `AssertionError` from the output. Defaults to the exception message/`__str__()`.
_classmethod _for_later()[source]¶
    
Return an unfilled ExceptionInfo.
fill_unfilled(_exc_info_)[source]¶
    
Fill an unfilled ExceptionInfo created with `for_later()`.
_property_ type _: type[E]_¶
    
The exception class.
_property_ value _: E_¶
    
The exception value.
_property_ tb _: TracebackType_¶
    
The exception raw traceback.
_property_ typename _: str_¶
    
The type name of the exception.
_property_ traceback _: Traceback_¶
    
The traceback.
exconly(_tryshort =False_)[source]¶
    
Return the exception as a string.
When ‘tryshort’ resolves to True, and the exception is an AssertionError, only the actual exception part of the exception representation is returned (so ‘AssertionError: ‘ is removed from the beginning).
errisinstance(_exc_)[source]¶
    
Return True if the exception is an instance of exc.
Consider using `isinstance(excinfo.value, exc)` instead.
getrepr(_showlocals =False_, _style ='long'_, _abspath =False_, _tbfilter =True_, _funcargs =False_, _truncate_locals =True_, _truncate_args =True_, _chain =True_)[source]¶
    
Return str()able representation of this exception info.
Parameters:
    
  * **showlocals** (_bool_) – Show locals per traceback entry. Ignored if `style=="native"`.
  * **style** (_str_) – long|short|line|no|native|value traceback style.
  * **abspath** (_bool_) – If paths should be changed to absolute or left unchanged.
  * **tbfilter** (_bool_ _|__Callable_ _[__[__ExceptionInfo_ _[__BaseException_ _]__]__,__Traceback_ _]_) – 
A filter for traceback entries.
    * If false, don’t hide any entries.
    * If true, hide internal entries and entries that contain a local variable `__tracebackhide__ = True`.
    * If a callable, delegates the filtering to the callable.
Ignored if `style` is `"native"`.
  * **funcargs** (_bool_) – Show fixtures (“funcargs” for legacy purposes) per traceback entry.
  * **truncate_locals** (_bool_) – With `showlocals==True`, make sure locals can be safely represented as strings.
  * **truncate_args** (_bool_) – With `showargs==True`, make sure args can be safely represented as strings.
  * **chain** (_bool_) – If chained exceptions in Python 3 should be shown.


Changed in version 3.9: Added the `chain` parameter.
match(_regexp_)[source]¶
    
Check whether the regular expression `regexp` matches the string representation of the exception using `re.search()`.
If it matches `True` is returned, otherwise an `AssertionError` is raised.
group_contains(_expected_exception_ , _*_ , _match =None_, _depth =None_)[source]¶
    
Check whether a captured exception group contains a matching exception.
Parameters:
    
  * **expected_exception** (_Type_ _[__BaseException_ _]__|__Tuple_ _[__Type_ _[__BaseException_ _]__]_) – The expected exception type, or a tuple if one of multiple possible exception types are expected.
  * **match** (_str_ _|__Pattern_ _[__str_ _]__|__None_) – 
If specified, a string containing a regular expression, or a regular expression object, that is tested against the string representation of the exception and its `PEP-678 <https://peps.python.org/pep-0678/>` `__notes__` using `re.search()`.
To match a literal string that may contain special characters, the pattern can first be escaped with `re.escape()`.
  * **depth** (_Optional_ _[__int_ _]_) – If `None`, will search for a matching exception at any nesting depth. If >= 1, will only match an exception if it’s at the specified depth (depth = 1 being the exceptions contained within the topmost exception group).


Added in version 8.0.
### ExitCode¶
_final class_ExitCode(_value_ , _names= <not given>_, _*values_ , _module=None_ , _qualname=None_ , _type=None_ , _start=1_ , _boundary=None_)[source]¶
    
Encodes the valid exit codes by pytest.
Currently users and plugins may supply other exit codes as well.
Added in version 5.0.
OK _= 0_¶
    
Tests passed.
TESTS_FAILED _= 1_¶
    
Tests failed.
INTERRUPTED _= 2_¶
    
pytest was interrupted.
INTERNAL_ERROR _= 3_¶
    
An internal error got in the way.
USAGE_ERROR _= 4_¶
    
pytest was misused.
NO_TESTS_COLLECTED _= 5_¶
    
pytest couldn’t find tests.
### FixtureDef¶
_final class_FixtureDef[source]¶
    
Bases: `Generic`[`FixtureValue`]
A container for a fixture definition.
Note: At this time, only explicitly documented fields and methods are considered public stable API.
_property_ scope _: Literal['session','package','module','class','function']_¶
    
Scope string, one of “function”, “class”, “module”, “package”, “session”.
execute(_request_)[source]¶
    
Return the value of this fixture, executing it if not cached.
### MarkDecorator¶
_class_ MarkDecorator[source]¶
    
A decorator for applying a mark on test functions and classes.
`MarkDecorators` are created with `pytest.mark`:
```
mark1 = pytest.mark.NAME # Simple MarkDecorator
mark2 = pytest.mark.NAME(name1=value) # Parametrized MarkDecorator

```

and can then be applied as decorators to test functions:
```
@mark2
def test_function():
  pass

```

When a `MarkDecorator` is called, it does the following:
  1. If called with a single class as its only positional argument and no additional keyword arguments, it attaches the mark to the class so it gets applied automatically to all test cases found in that class.
  2. If called with a single function as its only positional argument and no additional keyword arguments, it attaches the mark to the function, containing all the arguments already stored internally in the `MarkDecorator`.
  3. When called in any other case, it returns a new `MarkDecorator` instance with the original `MarkDecorator`’s content updated with the arguments passed to this call.


Note: The rules above prevent a `MarkDecorator` from storing only a single function or class reference as its positional argument with no additional keyword or positional arguments. You can work around this by using `with_args()`.
_property_ name _: str_¶
    
Alias for mark.name.
_property_ args _: tuple[Any,...]_¶
    
Alias for mark.args.
_property_ kwargs _: Mapping[str,Any]_¶
    
Alias for mark.kwargs.
with_args(_* args_, _** kwargs_)[source]¶
    
Return a MarkDecorator with extra arguments added.
Unlike calling the MarkDecorator, with_args() can be used even if the sole argument is a callable/class.
### MarkGenerator¶
_final class_MarkGenerator[source]¶
    
Factory for `MarkDecorator` objects - exposed as a `pytest.mark` singleton instance.
Example:
```
import pytest

@pytest.mark.slowtest
def test_function():
  pass

```

applies a ‘slowtest’ `Mark` on `test_function`.
### Mark¶
_final class_Mark[source]¶
    
A pytest mark.
name _: str_¶
    
Name of the mark.
args _: tuple[Any,...]_¶
    
Positional arguments of the mark decorator.
kwargs _: Mapping[str,Any]_¶
    
Keyword arguments of the mark decorator.
combined_with(_other_)[source]¶
    
Return a new Mark which is a combination of this Mark and another Mark.
Combines by appending args and merging kwargs.
Parameters:
    
**other** (_Mark_) – The mark to combine with.
Return type:
    
Mark
### Metafunc¶
_final class_Metafunc[source]¶
    
Objects passed to the `pytest_generate_tests` hook.
They help to inspect a test function and to generate tests according to test configuration or values specified in the class or module where a test function is defined.
definition¶
    
Access to the underlying `_pytest.python.FunctionDefinition`.
config¶
    
Access to the `pytest.Config` object for the test session.
module¶
    
The module object where the test function is defined in.
function¶
    
Underlying Python test function.
fixturenames¶
    
Set of fixture names required by the test function.
cls¶
    
Class object where the test function is defined in or `None`.
parametrize(_argnames_ , _argvalues_ , _indirect =False_, _ids =None_, _scope =None_, _*_ , __param_mark =None_)[source]¶
    
Add new invocations to the underlying test function using the list of argvalues for the given argnames. Parametrization is performed during the collection phase. If you need to setup expensive resources see about setting indirect to do it rather than at test setup time.
Can be called multiple times per test function (but only on different argument names), in which case each call parametrizes all previous parametrizations, e.g.
```
unparametrized:     t
parametrize ["x", "y"]: t[x], t[y]
parametrize [1, 2]:   t[x-1], t[x-2], t[y-1], t[y-2]

```

Parameters:
    
  * **argnames** (_str_ _|__Sequence_ _[__str_ _]_) – A comma-separated string denoting one or more argument names, or a list/tuple of argument strings.
  * **argvalues** (_Iterable_ _[___pytest.mark.structures.ParameterSet_ _|__Sequence_ _[__object_ _]__|__object_ _]_) – 
The list of argvalues determines how often a test is invoked with different argument values.
If only one argname was specified argvalues is a list of values. If N argnames were specified, argvalues must be a list of N-tuples, where each tuple-element specifies a value for its respective argname.
  * **indirect** (_bool_ _|__Sequence_ _[__str_ _]_) – A list of arguments’ names (subset of argnames) or a boolean. If True the list contains all names from the argnames. Each argvalue corresponding to an argname in this list will be passed as request.param to its respective argname fixture function so that it can perform more expensive setups during the setup phase of a test rather than at collection time.
  * **ids** (_Iterable_ _[__object_ _|__None_ _]__|__Callable_ _[__[__Any_ _]__,__object_ _|__None_ _]__|__None_) – 
Sequence of (or generator for) ids for `argvalues`, or a callable to return part of the id for each argvalue.
With sequences (and generators like `itertools.count()`) the returned ids should be of type `string`, `int`, `float`, `bool`, or `None`. They are mapped to the corresponding index in `argvalues`. `None` means to use the auto-generated id.
If it is a callable it will be called for each entry in `argvalues`, and the return value is used as part of the auto-generated id for the whole set (where parts are joined with dashes (“-“)). This is useful to provide more specific ids for certain items, e.g. dates. Returning `None` will use an auto-generated id.
If no ids are provided they will be generated automatically from the argvalues.
  * **scope** (_Literal_ _[__'session'__,__'package'__,__'module'__,__'class'__,__'function'__]__|__None_) – If specified it denotes the scope of the parameters. The scope is used for grouping tests by parameter instances. It will also override any fixture-function defined scope, allowing to set a dynamic scope using test context or configuration.


### Parser¶
_final class_Parser[source]¶
    
Parser for command line arguments and ini-file values.
Variables:
    
**extra_info** – Dict of generic param -> value to display in case there’s an error processing the command line arguments.
getgroup(_name_ , _description =''_, _after =None_)[source]¶
    
Get (or create) a named option Group.
Parameters:
    
  * **name** (_str_) – Name of the option group.
  * **description** (_str_) – Long description for –help output.
  * **after** (_str_ _|__None_) – Name of another group, used for ordering –help output.


Returns:
    
The option group.
Return type:
    
_OptionGroup_
The returned group object has an `addoption` method with the same signature as `parser.addoption` but will be shown in the respective group in the output of `pytest --help`.
addoption(_* opts_, _** attrs_)[source]¶
    
Register a command line option.
Parameters:
    
  * **opts** (_str_) – Option names, can be short or long options.
  * **attrs** (_Any_) – Same attributes as the argparse library’s `add_argument()` function accepts.


After command line parsing, options are available on the pytest config object via `config.option.NAME` where `NAME` is usually set by passing a `dest` attribute, for example `addoption("--long", dest="NAME", ...)`.
parse_known_args(_args_ , _namespace =None_)[source]¶
    
Parse the known arguments at this point.
Returns:
    
An argparse namespace object.
Return type:
    
_Namespace_
parse_known_and_unknown_args(_args_ , _namespace =None_)[source]¶
    
Parse the known arguments at this point, and also return the remaining unknown arguments.
Returns:
    
A tuple containing an argparse namespace object for the known arguments, and a list of the unknown arguments.
Return type:
    
tuple[_Namespace_, list[str]]
addini(_name_ , _help_ , _type=None_ , _default= <notset>_)[source]¶
    
Register an ini-file option.
Parameters:
    
  * **name** (_str_) – Name of the ini-variable.
  * **type** (_Literal_ _[__'string'__,__'paths'__,__'pathlist'__,__'args'__,__'linelist'__,__'bool'__]__|__None_) – 
Type of the variable. Can be:
>     * `string`: a string
>     * `bool`: a boolean
>     * `args`: a list of strings, separated as in a shell
>     * `linelist`: a list of strings, separated by line breaks
>     * `paths`: a list of `pathlib.Path`, separated as in a shell
>     * `pathlist`: a list of `py.path`, separated as in a shell
For `paths` and `pathlist` types, they are considered relative to the ini-file. In case the execution is happening without an ini-file defined, they will be considered relative to the current working directory (for example with `--override-ini`).
Added in version 7.0: The `paths` variable type.
Added in version 8.1: Use the current working directory to resolve `paths` and `pathlist` in the absence of an ini-file.
Defaults to `string` if `None` or not passed.
  * **default** (_Any_) – Default value if no ini-file option exists but is queried.


The value of ini-variables can be retrieved via a call to `config.getini(name)`.
### OptionGroup¶
_class_ OptionGroup[source]¶
    
A group of options shown in its own section.
addoption(_* opts_, _** attrs_)[source]¶
    
Add an option to this group.
If a shortened version of a long option is specified, it will be suppressed in the help. `addoption('--twowords', '--two-words')` results in help showing `--two-words` only, but `--twowords` gets accepted **and** the automatic destination is in `args.twowords`.
Parameters:
    
  * **opts** (_str_) – Option names, can be short or long options.
  * **attrs** (_Any_) – Same attributes as the argparse library’s `add_argument()` function accepts.


### PytestPluginManager¶
_final class_PytestPluginManager[source]¶
    
Bases: `PluginManager`
A `pluggy.PluginManager` with additional pytest-specific functionality:
  * Loading plugins from the command line, `PYTEST_PLUGINS` env variable and `pytest_plugins` global variables found in plugins being loaded.
  * `conftest.py` loading during start-up.


register(_plugin_ , _name =None_)[source]¶
    
Register a plugin and return its name.
Parameters:
    
**name** (_str_ _|__None_) – The name under which to register the plugin. If not specified, a name is generated using `get_canonical_name()`.
Returns:
    
The plugin name. If the name is blocked from registering, returns `None`.
Return type:
    
str | None
If the plugin is already registered, raises a `ValueError`.
getplugin(_name_)[source]¶
hasplugin(_name_)[source]¶
    
Return whether a plugin with the given name is registered.
import_plugin(_modname_ , _consider_entry_points =False_)[source]¶
    
Import a plugin with `modname`.
If `consider_entry_points` is True, entry point names are also considered to find a plugin.
add_hookcall_monitoring(_before_ , _after_)¶
    
Add before/after tracing functions for all hooks.
Returns an undo function which, when called, removes the added tracers.
`before(hook_name, hook_impls, kwargs)` will be called ahead of all hook calls and receive a hookcaller instance, a list of HookImpl instances and the keyword arguments for the hook call.
`after(outcome, hook_name, hook_impls, kwargs)` receives the same arguments as `before` but also a `Result` object which represents the result of the overall hook call.
add_hookspecs(_module_or_class_)¶
    
Add new hook specifications defined in the given `module_or_class`.
Functions are recognized as hook specifications if they have been decorated with a matching `HookspecMarker`.
check_pending()¶
    
Verify that all hooks which have not been verified against a hook specification are optional, otherwise raise `PluginValidationError`.
enable_tracing()¶
    
Enable tracing of hook calls.
Returns an undo function which, when called, removes the added tracing.
get_canonical_name(_plugin_)¶
    
Return a canonical name for a plugin object.
Note that a plugin may be registered under a different name specified by the caller of `register(plugin, name)`. To obtain the name of a registered plugin use `get_name(plugin)` instead.
get_hookcallers(_plugin_)¶
    
Get all hook callers for the specified plugin.
Returns:
    
The hook callers, or `None` if `plugin` is not registered in this plugin manager.
Return type:
    
list[_HookCaller_] | None
get_name(_plugin_)¶
    
Return the name the plugin is registered under, or `None` if is isn’t.
get_plugin(_name_)¶
    
Return the plugin registered under the given name, if any.
get_plugins()¶
    
Return a set of all registered plugin objects.
has_plugin(_name_)¶
    
Return whether a plugin with the given name is registered.
is_blocked(_name_)¶
    
Return whether the given plugin name is blocked.
is_registered(_plugin_)¶
    
Return whether the plugin is already registered.
list_name_plugin()¶
    
Return a list of (name, plugin) pairs for all registered plugins.
list_plugin_distinfo()¶
    
Return a list of (plugin, distinfo) pairs for all setuptools-registered plugins.
load_setuptools_entrypoints(_group_ , _name =None_)¶
    
Load modules from querying the specified setuptools `group`.
Parameters:
    
  * **group** (_str_) – Entry point group to load plugins.
  * **name** (_str_ _|__None_) – If given, loads only plugins with the given `name`.


Returns:
    
The number of plugins loaded by this call.
Return type:
    
int
set_blocked(_name_)¶
    
Block registrations of the given name, unregister if already registered.
subset_hook_caller(_name_ , _remove_plugins_)¶
    
Return a proxy `HookCaller` instance for the named method which manages calls to all registered plugins except the ones from remove_plugins.
unblock(_name_)¶
    
Unblocks a name.
Returns whether the name was actually blocked.
unregister(_plugin =None_, _name =None_)¶
    
Unregister a plugin and all of its hook implementations.
The plugin can be specified either by the plugin object or the plugin name. If both are specified, they must agree.
Returns the unregistered plugin, or `None` if not found.
project_name _: Final_¶
    
The project name.
hook _: Final_¶
    
The “hook relay”, used to call a hook on all registered plugins. See Calling hooks.
trace _: Final[_tracing.TagTracerSub]_¶
    
The tracing entry point. See Built-in tracing.
### TestReport¶
_final class_TestReport[source]¶
    
Bases: `BaseReport`
Basic test report object (also used for setup and teardown calls if they fail).
Reports can contain arbitrary extra attributes.
nodeid _: str_¶
    
Normalized collection nodeid.
location _: tuple[str,int|None,str]_¶
    
A (filesystempath, lineno, domaininfo) tuple indicating the actual location of a test item - it might be different from the collected one e.g. if a method is inherited from a different module. The filesystempath may be relative to `config.rootdir`. The line number is 0-based.
keywords _: Mapping[str,Any]_¶
    
A name -> value dictionary containing all keywords and markers associated with a test invocation.
outcome _: Literal['passed','failed','skipped']_¶
    
Test outcome, always one of “passed”, “failed”, “skipped”.
longrepr _: None|ExceptionInfo[BaseException]|tuple[str,int,str]|str|TerminalRepr_¶
    
None or a failure representation.
when _: str|None_¶
    
One of ‘setup’, ‘call’, ‘teardown’ to indicate runtest phase.
user_properties¶
    
User properties is a list of tuples (name, value) that holds user defined properties of the test.
sections _: list[tuple[str,str]]_¶
    
Tuples of str `(heading, content)` with extra information for the test report. Used by pytest to add text captured from `stdout`, `stderr`, and intercepted logging events. May be used by other plugins to add arbitrary information to reports.
duration _: float_¶
    
Time it took to run just the test.
start _: float_¶
    
The system time when the call started, in seconds since the epoch.
stop _: float_¶
    
The system time when the call ended, in seconds since the epoch.
_classmethod _from_item_and_call(_item_ , _call_)[source]¶
    
Create and fill a TestReport with standard item and call info.
Parameters:
    
  * **item** (_Item_) – The item.
  * **call** (_CallInfo_ _[__None_ _]_) – The call info.


_property_ caplog _: str_¶
    
Return captured log lines, if log capturing is enabled.
Added in version 3.5.
_property_ capstderr _: str_¶
    
Return captured text from stderr, if capturing is enabled.
Added in version 3.0.
_property_ capstdout _: str_¶
    
Return captured text from stdout, if capturing is enabled.
Added in version 3.0.
_property_ count_towards_summary _: bool_¶
    
**Experimental** Whether this report should be counted towards the totals shown at the end of the test session: “1 passed, 1 failure, etc”.
Note
This function is considered **experimental** , so beware that it is subject to changes even in patch releases.
_property_ failed _: bool_¶
    
Whether the outcome is failed.
_property_ fspath _: str_¶
    
The path portion of the reported node, as a string.
_property_ head_line _: str|None_¶
    
**Experimental** The head line shown with longrepr output for this report, more commonly during traceback representation during failures:
```
________ Test.foo ________

```

In the example above, the head_line is “Test.foo”.
Note
This function is considered **experimental** , so beware that it is subject to changes even in patch releases.
_property_ longreprtext _: str_¶
    
Read-only property that returns the full string representation of `longrepr`.
Added in version 3.0.
_property_ passed _: bool_¶
    
Whether the outcome is passed.
_property_ skipped _: bool_¶
    
Whether the outcome is skipped.
### TestShortLogReport¶
_class_ TestShortLogReport[source]¶
    
Used to store the test status result category, shortletter and verbose word. For example `"rerun", "R", ("RERUN", {"yellow": True})`.
Variables:
    
  * **category** – The class of result, for example `“passed”`, `“skipped”`, `“error”`, or the empty string.
  * **letter** – The short letter shown as testing progresses, for example `"."`, `"s"`, `"E"`, or the empty string.
  * **word** – Verbose word is shown as testing progresses in verbose mode, for example `"PASSED"`, `"SKIPPED"`, `"ERROR"`, or the empty string.


category _: str_¶
    
Alias for field number 0
letter _: str_¶
    
Alias for field number 1
word _: str|tuple[str,Mapping[str,bool]]_¶
    
Alias for field number 2
### Result¶
Result object used within hook wrappers, see `Result in the pluggy documentation` for more information.
### Stash¶
_class_ Stash[source]¶
    
`Stash` is a type-safe heterogeneous mutable mapping that allows keys and value types to be defined separately from where it (the `Stash`) is created.
Usually you will be given an object which has a `Stash`, for example `Config` or a `Node`:
```
stash: Stash = some_object.stash

```

If a module or plugin wants to store data in this `Stash`, it creates `StashKey`s for its keys (at the module level):
```
# At the top-level of the module
some_str_key = StashKey[str]()
some_bool_key = StashKey[bool]()

```

To store information:
```
# Value type must match the key.
stash[some_str_key] = "value"
stash[some_bool_key] = True

```

To retrieve the information:
```
# The static type of some_str is str.
some_str = stash[some_str_key]
# The static type of some_bool is bool.
some_bool = stash[some_bool_key]

```

Added in version 7.0.
__setitem__(_key_ , _value_)[source]¶
    
Set a value for key.
__getitem__(_key_)[source]¶
    
Get the value for key.
Raises `KeyError` if the key wasn’t set before.
get(_key_ , _default_)[source]¶
    
Get the value for key, or return default if the key wasn’t set before.
setdefault(_key_ , _default_)[source]¶
    
Return the value of key if already set, otherwise set the value of key to default and return default.
__delitem__(_key_)[source]¶
    
Delete the value for key.
Raises `KeyError` if the key wasn’t set before.
__contains__(_key_)[source]¶
    
Return whether key was set.
__len__()[source]¶
    
Return how many items exist in the stash.
_class_ StashKey[source]¶
    
Bases: `Generic`[`T`]
`StashKey` is an object used as a key to a `Stash`.
A `StashKey` is associated with the type `T` of the value of the key.
A `StashKey` is unique and cannot conflict with another key.
Added in version 7.0.
## Global Variables¶
pytest treats some global variables in a special manner when defined in a test module or `conftest.py` files.
collect_ignore¶
**Tutorial** : Customizing test collection
Can be declared in _conftest.py files_ to exclude test directories or modules. Needs to be a list of paths (`str`, `pathlib.Path` or any `os.PathLike`).
```
collect_ignore = ["setup.py"]

```

collect_ignore_glob¶
**Tutorial** : Customizing test collection
Can be declared in _conftest.py files_ to exclude test directories or modules with Unix shell-style wildcards. Needs to be `list[str]` where `str` can contain glob patterns.
```
collect_ignore_glob = ["*_ignore.py"]

```

pytest_plugins¶
**Tutorial** : Requiring/Loading plugins in a test module or conftest file
Can be declared at the **global** level in _test modules_ and _conftest.py files_ to register additional plugins. Can be either a `str` or `Sequence[str]`.
```
pytest_plugins = "myapp.testsupport.myplugin"

```

```
pytest_plugins = ("myapp.testsupport.tools", "myapp.testsupport.regression")

```

pytestmark¶
**Tutorial** : Marking whole classes or modules
Can be declared at the **global** level in _test modules_ to apply one or more marks to all test functions and methods. Can be either a single mark or a list of marks (applied in left-to-right order).
```
import pytest
pytestmark = pytest.mark.webtest

```

```
import pytest
pytestmark = [pytest.mark.integration, pytest.mark.slow]

```

## Environment Variables¶
Environment variables that can be used to change pytest’s behavior.
CI¶
When set (regardless of value), pytest acknowledges that is running in a CI process. Alternative to `BUILD_NUMBER` variable. See also CI Pipelines.
BUILD_NUMBER¶
When set (regardless of value), pytest acknowledges that is running in a CI process. Alternative to CI variable. See also CI Pipelines.
PYTEST_ADDOPTS¶
This contains a command-line (parsed by the py:mod:`shlex` module) that will be **prepended** to the command line given by the user, see Builtin configuration file options for more information.
PYTEST_VERSION¶
This environment variable is defined at the start of the pytest session and is undefined afterwards. It contains the value of `pytest.__version__`, and among other things can be used to easily check if a code is running from within a pytest run.
PYTEST_CURRENT_TEST¶
This is not meant to be set by users, but is set by pytest internally with the name of the current test so other processes can inspect it, see PYTEST_CURRENT_TEST environment variable for more information.
PYTEST_DEBUG¶
When set, pytest will print tracing and debug information.
PYTEST_DEBUG_TEMPROOT¶
Root for temporary directories produced by fixtures like `tmp_path` as discussed in Temporary directory location and retention.
PYTEST_DISABLE_PLUGIN_AUTOLOAD¶
When set, disables plugin auto-loading through entry point packaging metadata. Only explicitly specified plugins will be loaded.
PYTEST_PLUGINS¶
Contains comma-separated list of modules that should be loaded as plugins:
```
exportPYTEST_PLUGINS=mymodule.plugin,xdist

```

PYTEST_THEME¶
Sets a pygment style to use for the code output.
PYTEST_THEME_MODE¶
Sets the `PYTEST_THEME` to be either _dark_ or _light_.
PY_COLORS¶
When set to `1`, pytest will use color in terminal output. When set to `0`, pytest will not use color. `PY_COLORS` takes precedence over `NO_COLOR` and `FORCE_COLOR`.
NO_COLOR¶
When set to a non-empty string (regardless of value), pytest will not use color in terminal output. `PY_COLORS` takes precedence over `NO_COLOR`, which takes precedence over `FORCE_COLOR`. See no-color.org for other libraries supporting this community standard.
FORCE_COLOR¶
When set to a non-empty string (regardless of value), pytest will use color in terminal output. `PY_COLORS` and `NO_COLOR` take precedence over `FORCE_COLOR`.
## Exceptions¶
_final exception_UsageError[source]¶
    
Bases: `Exception`
Error in pytest usage or invocation.
_final exception_FixtureLookupError[source]¶
    
Bases: `LookupError`
Could not return a requested fixture (missing or invalid).
## Warnings¶
Custom warnings generated in some situations such as improper usage or deprecated features.
_class_ PytestWarning¶
    
Bases: `UserWarning`
Base class for all warnings emitted by pytest.
_class_ PytestAssertRewriteWarning¶
    
Bases: `PytestWarning`
Warning emitted by the pytest assert rewrite module.
_class_ PytestCacheWarning¶
    
Bases: `PytestWarning`
Warning emitted by the cache plugin in various situations.
_class_ PytestCollectionWarning¶
    
Bases: `PytestWarning`
Warning emitted when pytest is not able to collect a file or symbol in a module.
_class_ PytestConfigWarning¶
    
Bases: `PytestWarning`
Warning emitted for configuration issues.
_class_ PytestDeprecationWarning¶
    
Bases: `PytestWarning`, `DeprecationWarning`
Warning class for features that will be removed in a future version.
_class_ PytestExperimentalApiWarning¶
    
Bases: `PytestWarning`, `FutureWarning`
Warning category used to denote experiments in pytest.
Use sparingly as the API might change or even be removed completely in a future version.
_class_ PytestReturnNotNoneWarning¶
    
Bases: `PytestWarning`
Warning emitted when a test function is returning value other than None.
_class_ PytestRemovedIn9Warning¶
    
Bases: `PytestDeprecationWarning`
Warning class for features that will be removed in pytest 9.
_class_ PytestUnhandledCoroutineWarning¶
    
Bases: `PytestReturnNotNoneWarning`
Warning emitted for an unhandled coroutine.
A coroutine was encountered when collecting test functions, but was not handled by any async-aware plugin. Coroutine test functions are not natively supported.
_class_ PytestUnknownMarkWarning¶
    
Bases: `PytestWarning`
Warning emitted on use of unknown markers.
See How to mark test functions with attributes for details.
_class_ PytestUnraisableExceptionWarning¶
    
Bases: `PytestWarning`
An unraisable exception was reported.
Unraisable exceptions are exceptions raised in `__del__` implementations and similar situations when the exception cannot be raised as normal.
_class_ PytestUnhandledThreadExceptionWarning¶
    
Bases: `PytestWarning`
An unhandled exception occurred in a `Thread`.
Such exceptions don’t propagate normally.
Consult the Internal pytest warnings section in the documentation for more information.
## Configuration Options¶
Here is a list of builtin configuration options that may be written in a `pytest.ini` (or `.pytest.ini`), `pyproject.toml`, `tox.ini`, or `setup.cfg` file, usually located at the root of your repository.
To see each file format in details, see Configuration file formats.
Warning
Usage of `setup.cfg` is not recommended except for very simple use cases. `.cfg` files use a different parser than `pytest.ini` and `tox.ini` which might cause hard to track down problems. When possible, it is recommended to use the latter files, or `pyproject.toml`, to hold your pytest configuration.
Configuration options may be overwritten in the command-line by using `-o/--override-ini`, which can also be passed multiple times. The expected format is `name=value`. For example:
```
pytest -o console_output_style=classic -o cache_dir=/tmp/mycache

```

addopts¶
    
Add the specified `OPTS` to the set of command line arguments as if they had been specified by the user. Example: if you have this ini file content:
```
# content of pytest.ini
[pytest]
addopts=--maxfail=2 -rf# exit after 2 failures, report fail info

```

issuing `pytest test_hello.py` actually means:
```
pytest--maxfail=2-rftest_hello.py

```

Default is to add no options.
cache_dir¶
    
Sets the directory where the cache plugin’s content is stored. Default directory is `.pytest_cache` which is created in rootdir. Directory may be relative or absolute path. If setting relative path, then directory is created relative to rootdir. Additionally, a path may contain environment variables, that will be expanded. For more information about cache plugin please refer to How to re-run failed tests and maintain state between test runs.
consider_namespace_packages¶
    
Controls if pytest should attempt to identify namespace packages when collecting Python modules. Default is `False`.
Set to `True` if the package you are testing is part of a namespace package.
Only native namespace packages are supported, with no plans to support legacy namespace packages.
Added in version 8.1.
console_output_style¶
    
Sets the console output style while running tests:
  * `classic`: classic pytest output.
  * `progress`: like classic pytest output, but with a progress indicator.
  * `progress-even-when-capture-no`: allows the use of the progress indicator even when `capture=no`.
  * `count`: like progress, but shows progress as the number of tests completed instead of a percent.


The default is `progress`, but you can fallback to `classic` if you prefer or the new mode is causing unexpected problems:
```
# content of pytest.ini
[pytest]
console_output_style=classic

```

doctest_encoding¶
    
Default encoding to use to decode text files with docstrings. See how pytest handles doctests.
doctest_optionflags¶
    
One or more doctest flag names from the standard `doctest` module. See how pytest handles doctests.
empty_parameter_set_mark¶
    
Allows to pick the action for empty parametersets in parameterization
  * `skip` skips tests with an empty parameterset (default)
  * `xfail` marks tests with an empty parameterset as xfail(run=False)
  * `fail_at_collect` raises an exception if parametrize collects an empty parameter set


```
# content of pytest.ini
[pytest]
empty_parameter_set_mark=xfail

```

Note
The default value of this option is planned to change to `xfail` in future releases as this is considered less error prone, see #3155 for more details.
faulthandler_timeout¶
    
Dumps the tracebacks of all threads if a test takes longer than `X` seconds to run (including fixture setup and teardown). Implemented using the `faulthandler.dump_traceback_later()` function, so all caveats there apply.
```
# content of pytest.ini
[pytest]
faulthandler_timeout=5

```

For more information please refer to Fault Handler.
filterwarnings¶
    
Sets a list of filters and actions that should be taken for matched warnings. By default all warnings emitted during the test session will be displayed in a summary at the end of the test session.
```
# content of pytest.ini
[pytest]
filterwarnings=
error
ignore::DeprecationWarning

```

This tells pytest to ignore deprecation warnings and turn all other warnings into errors. For more information please refer to How to capture warnings.
junit_duration_report¶
    
Added in version 4.1.
Configures how durations are recorded into the JUnit XML report:
  * `total` (the default): duration times reported include setup, call, and teardown times.
  * `call`: duration times reported include only call times, excluding setup and teardown.


```
[pytest]
junit_duration_report=call

```

junit_family¶
    
Added in version 4.2.
Changed in version 6.1: Default changed to `xunit2`.
Configures the format of the generated JUnit XML file. The possible options are:
  * `xunit1` (or `legacy`): produces old style output, compatible with the xunit 1.0 format.
  * `xunit2`: produces xunit 2.0 style output, which should be more compatible with latest Jenkins versions. **This is the default**.


```
[pytest]
junit_family=xunit2

```

junit_logging¶
    
Added in version 3.5.
Changed in version 5.4: `log`, `all`, `out-err` options added.
Configures if captured output should be written to the JUnit XML file. Valid values are:
  * `log`: write only `logging` captured output.
  * `system-out`: write captured `stdout` contents.
  * `system-err`: write captured `stderr` contents.
  * `out-err`: write both captured `stdout` and `stderr` contents.
  * `all`: write captured `logging`, `stdout` and `stderr` contents.
  * `no` (the default): no captured output is written.


```
[pytest]
junit_logging=system-out

```

junit_log_passing_tests¶
    
Added in version 4.6.
If `junit_logging != "no"`, configures if the captured output should be written to the JUnit XML file for **passing** tests. Default is `True`.
```
[pytest]
junit_log_passing_tests=False

```

junit_suite_name¶
    
To set the name of the root test suite xml item, you can configure the `junit_suite_name` option in your config file:
```
[pytest]
junit_suite_name=my_suite

```

log_auto_indent¶
    
Allow selective auto-indentation of multiline log messages.
Supports command line option `--log-auto-indent [value]` and config option `log_auto_indent = [value]` to set the auto-indentation behavior for all logging.
`[value]` can be:
    
  * True or “On” - Dynamically auto-indent multiline log messages
  * False or “Off” or 0 - Do not auto-indent multiline log messages (the default behavior)
  * [positive integer] - auto-indent multiline log messages by [value] spaces


```
[pytest]
log_auto_indent=False

```

Supports passing kwarg `extra={"auto_indent": [value]}` to calls to `logging.log()` to specify auto-indentation behavior for a specific entry in the log. `extra` kwarg overrides the value specified on the command line or in the config.
log_cli¶
    
Enable log display during test run (also known as “live logging”). The default is `False`.
```
[pytest]
log_cli=True

```

log_cli_date_format¶
    
Sets a `time.strftime()`-compatible string that will be used when formatting dates for live logging.
```
[pytest]
log_cli_date_format=%Y-%m-%d %H:%M:%S

```

For more information, see Live Logs.
log_cli_format¶
    
Sets a `logging`-compatible string used to format live logging messages.
```
[pytest]
log_cli_format=%(asctime)s %(levelname)s %(message)s

```

For more information, see Live Logs.
log_cli_level¶
    
Sets the minimum log message level that should be captured for live logging. The integer value or the names of the levels can be used.
```
[pytest]
log_cli_level=INFO

```

For more information, see Live Logs.
log_date_format¶
    
Sets a `time.strftime()`-compatible string that will be used when formatting dates for logging capture.
```
[pytest]
log_date_format=%Y-%m-%d %H:%M:%S

```

For more information, see How to manage logging.
log_file¶
    
Sets a file name relative to the current working directory where log messages should be written to, in addition to the other logging facilities that are active.
```
[pytest]
log_file=logs/pytest-logs.txt

```

For more information, see How to manage logging.
log_file_date_format¶
    
Sets a `time.strftime()`-compatible string that will be used when formatting dates for the logging file.
```
[pytest]
log_file_date_format=%Y-%m-%d %H:%M:%S

```

For more information, see How to manage logging.
log_file_format¶
    
Sets a `logging`-compatible string used to format logging messages redirected to the logging file.
```
[pytest]
log_file_format=%(asctime)s %(levelname)s %(message)s

```

For more information, see How to manage logging.
log_file_level¶
    
Sets the minimum log message level that should be captured for the logging file. The integer value or the names of the levels can be used.
```
[pytest]
log_file_level=INFO

```

For more information, see How to manage logging.
log_format¶
    
Sets a `logging`-compatible string used to format captured logging messages.
```
[pytest]
log_format=%(asctime)s %(levelname)s %(message)s

```

For more information, see How to manage logging.
log_level¶
    
Sets the minimum log message level that should be captured for logging capture. The integer value or the names of the levels can be used.
```
[pytest]
log_level=INFO

```

For more information, see How to manage logging.
markers¶
    
When the `--strict-markers` or `--strict` command-line arguments are used, only known markers - defined in code by core pytest or some plugin - are allowed.
You can list additional markers in this setting to add them to the whitelist, in which case you probably want to add `--strict-markers` to `addopts` to avoid future regressions:
```
[pytest]
addopts=--strict-markers
markers=
slow
serial

```

Note
The use of `--strict-markers` is highly preferred. `--strict` was kept for backward compatibility only and may be confusing for others as it only applies to markers and not to other options.
minversion¶
    
Specifies a minimal pytest version required for running tests.
```
# content of pytest.ini
[pytest]
minversion=3.0# will fail if we run with pytest-2.8

```

norecursedirs¶
    
Set the directory basename patterns to avoid when recursing for test discovery. The individual (fnmatch-style) patterns are applied to the basename of a directory to decide if to recurse into it. Pattern matching characters:
```
*    matches everything
?    matches any single character
[seq]  matches any character in seq
[!seq] matches any char not in seq

```

Default patterns are `'*.egg'`, `'.*'`, `'_darcs'`, `'build'`, `'CVS'`, `'dist'`, `'node_modules'`, `'venv'`, `'{arch}'`. Setting a `norecursedirs` replaces the default. Here is an example of how to avoid certain directories:
```
[pytest]
norecursedirs=.svn _build tmp*

```

This would tell `pytest` to not look into typical subversion or sphinx-build directories or into any `tmp` prefixed directory.
Additionally, `pytest` will attempt to intelligently identify and ignore a virtualenv. Any directory deemed to be the root of a virtual environment will not be considered during test collection unless `--collect-in-virtualenv` is given. Note also that `norecursedirs` takes precedence over `--collect-in-virtualenv`; e.g. if you intend to run tests in a virtualenv with a base directory that matches `'.*'` you _must_ override `norecursedirs` in addition to using the `--collect-in-virtualenv` flag.
python_classes¶
    
One or more name prefixes or glob-style patterns determining which classes are considered for test collection. Search for multiple glob patterns by adding a space between patterns. By default, pytest will consider any class prefixed with `Test` as a test collection. Here is an example of how to collect tests from classes that end in `Suite`:
```
[pytest]
python_classes=*Suite

```

Note that `unittest.TestCase` derived classes are always collected regardless of this option, as `unittest`’s own collection framework is used to collect those tests.
python_files¶
    
One or more Glob-style file patterns determining which python files are considered as test modules. Search for multiple glob patterns by adding a space between patterns:
```
[pytest]
python_files=test_*.py check_*.py example_*.py

```

Or one per line:
```
[pytest]
python_files=
test_*.py
check_*.py
example_*.py

```

By default, files matching `test_*.py` and `*_test.py` will be considered test modules.
python_functions¶
    
One or more name prefixes or glob-patterns determining which test functions and methods are considered tests. Search for multiple glob patterns by adding a space between patterns. By default, pytest will consider any function prefixed with `test` as a test. Here is an example of how to collect test functions and methods that end in `_test`:
```
[pytest]
python_functions=*_test

```

Note that this has no effect on methods that live on a `unittest.TestCase` derived class, as `unittest`’s own collection framework is used to collect those tests.
See Changing naming conventions for more detailed examples.
pythonpath¶
    
Sets list of directories that should be added to the python search path. Directories will be added to the head of `sys.path`. Similar to the `PYTHONPATH` environment variable, the directories will be included in where Python will look for imported modules. Paths are relative to the rootdir directory. Directories remain in path for the duration of the test session.
```
[pytest]
pythonpath=src1 src2

```

Note
`pythonpath` does not affect some imports that happen very early, most notably plugins loaded using the `-p` command line option.
required_plugins¶
    
A space separated list of plugins that must be present for pytest to run. Plugins can be listed with or without version specifiers directly following their name. Whitespace between different version specifiers is not allowed. If any one of the plugins is not found, emit an error.
```
[pytest]
required_plugins=pytest-django>=3.0.0,<4.0.0 pytest-html pytest-xdist>=1.0.0

```

testpaths¶
    
Sets list of directories that should be searched for tests when no specific directories, files or test ids are given in the command line when executing pytest from the rootdir directory. File system paths may use shell-style wildcards, including the recursive `**` pattern.
Useful when all project tests are in a known location to speed up test collection and to avoid picking up undesired tests by accident.
```
[pytest]
testpaths=testing doc

```

This configuration means that executing:
```
pytest

```

has the same practical effects as executing:
```
pytest testing doc

```

tmp_path_retention_count¶
    
How many sessions should we keep the `tmp_path` directories, according to `tmp_path_retention_policy`.
```
[pytest]
tmp_path_retention_count=3

```

Default: `3`
tmp_path_retention_policy¶
    
Controls which directories created by the `tmp_path` fixture are kept around, based on test outcome.
>   * `all`: retains directories for all tests, regardless of the outcome.
>   * `failed`: retains directories only for tests with outcome `error` or `failed`.
>   * `none`: directories are always removed after each test ends, regardless of the outcome.
> 

```
[pytest]
tmp_path_retention_policy=all

```

Default: `all`
usefixtures¶
    
List of fixtures that will be applied to all test functions; this is semantically the same to apply the `@pytest.mark.usefixtures` marker to all test functions.
```
[pytest]
usefixtures=
clean_db

```

verbosity_assertions¶
    
Set a verbosity level specifically for assertion related output, overriding the application wide level.
```
[pytest]
verbosity_assertions=2

```

Defaults to application wide verbosity level (via the `-v` command-line option). A special value of “auto” can be used to explicitly use the global verbosity level.
verbosity_test_cases¶
    
Set a verbosity level specifically for test case execution related output, overriding the application wide level.
```
[pytest]
verbosity_test_cases=2

```

Defaults to application wide verbosity level (via the `-v` command-line option). A special value of “auto” can be used to explicitly use the global verbosity level.
xfail_strict¶
    
If set to `True`, tests marked with `@pytest.mark.xfail` that actually succeed will by default fail the test suite. For more information, see strict parameter.
```
[pytest]
xfail_strict=True

```

## Command-line Flags¶
All the command-line flags can be obtained by running `pytest --help`:
```
$ pytest --help
usage: pytest [options] [file_or_dir] [file_or_dir] [...]
positional arguments:
 file_or_dir
general:
 -k EXPRESSION     Only run tests which match the given substring
            expression. An expression is a Python evaluable
            expression where all names are substring-matched
            against test names and their parent classes.
            Example: -k 'test_method or test_other' matches all
            test functions and classes whose name contains
            'test_method' or 'test_other', while -k 'not
            test_method' matches those that don't contain
            'test_method' in their names. -k 'not test_method
            and not test_other' will eliminate the matches.
            Additionally keywords are matched to classes and
            functions containing extra names in their
            'extra_keyword_matches' set, as well as functions
            which have names assigned directly to them. The
            matching is case-insensitive.
 -m MARKEXPR      Only run tests matching given mark expression. For
            example: -m 'mark1 and not mark2'.
 --markers       show markers (builtin, plugin and per-project ones).
 -x, --exitfirst    Exit instantly on first error or failed test
 --fixtures, --funcargs
            Show available fixtures, sorted by plugin appearance
            (fixtures with leading '_' are only shown with '-v')
 --fixtures-per-test  Show fixtures per test
 --pdb         Start the interactive Python debugger on errors or
            KeyboardInterrupt
 --pdbcls=modulename:classname
            Specify a custom interactive Python debugger for use
            with --pdb.For example:
            --pdbcls=IPython.terminal.debugger:TerminalPdb
 --trace        Immediately break when running each test
 --capture=method   Per-test capturing method: one of fd|sys|no|tee-sys
 -s          Shortcut for --capture=no
 --runxfail      Report the results of xfail tests as if they were
            not marked
 --lf, --last-failed  Rerun only the tests that failed at the last run (or
            all if none failed)
 --ff, --failed-first Run all tests, but run the last failures first. This
            may re-order tests and thus lead to repeated fixture
            setup/teardown.
 --nf, --new-first   Run tests from new files first, then the rest of the
            tests sorted by file mtime
 --cache-show=[CACHESHOW]
            Show cache contents, don't perform collection or
            tests. Optional argument: glob (default: '*').
 --cache-clear     Remove all cache contents at start of test run
 --lfnf={all,none}, --last-failed-no-failures={all,none}
            With ``--lf``, determines whether to execute tests
            when there are no previously (known) failures or
            when no cached ``lastfailed`` data was found.
            ``all`` (the default) runs the full test suite
            again. ``none`` just emits a message about no known
            failures and exits successfully.
 --sw, --stepwise   Exit on test failure and continue from last failing
            test next time
 --sw-skip, --stepwise-skip
            Ignore the first failing test but stop on the next
            failing test. Implicitly enables --stepwise.
Reporting:
 --durations=N     Show N slowest setup/test durations (N=0 for all)
 --durations-min=N   Minimal duration in seconds for inclusion in slowest
            list. Default: 0.005.
 -v, --verbose     Increase verbosity
 --no-header      Disable header
 --no-summary     Disable summary
 --no-fold-skipped   Do not fold skipped tests in short summary.
 -q, --quiet      Decrease verbosity
 --verbosity=VERBOSE  Set verbosity. Default: 0.
 -r chars       Show extra test summary info as specified by chars:
            (f)ailed, (E)rror, (s)kipped, (x)failed, (X)passed,
            (p)assed, (P)assed with output, (a)ll except passed
            (p/P), or (A)ll. (w)arnings are enabled by default
            (see --disable-warnings), 'N' can be used to reset
            the list. (default: 'fE').
 --disable-warnings, --disable-pytest-warnings
            Disable warnings summary
 -l, --showlocals   Show locals in tracebacks (disabled by default)
 --no-showlocals    Hide locals in tracebacks (negate --showlocals
            passed through addopts)
 --tb=style      Traceback print mode
            (auto/long/short/line/native/no)
 --xfail-tb      Show tracebacks for xfail (as long as --tb != no)
 --show-capture={no,stdout,stderr,log,all}
            Controls how captured stdout/stderr/log is shown on
            failed tests. Default: all.
 --full-trace     Don't cut any tracebacks (default is to cut)
 --color=color     Color terminal output (yes/no/auto)
 --code-highlight={yes,no}
            Whether code should be highlighted (only if --color
            is also enabled). Default: yes.
 --pastebin=mode    Send failed|all info to bpaste.net pastebin service
 --junit-xml=path   Create junit-xml style report file at given path
 --junit-prefix=str  Prepend prefix to classnames in junit-xml output
pytest-warnings:
 -W PYTHONWARNINGS, --pythonwarnings=PYTHONWARNINGS
            Set which warnings to report, see -W option of
            Python itself
 --maxfail=num     Exit after first num failures or errors
 --strict-config    Any warnings encountered while parsing the `pytest`
            section of the configuration file raise errors
 --strict-markers   Markers not registered in the `markers` section of
            the configuration file raise errors
 --strict       (Deprecated) alias to --strict-markers
 -c FILE, --config-file=FILE
            Load configuration from `FILE` instead of trying to
            locate one of the implicit configuration files.
 --continue-on-collection-errors
            Force test execution even if collection errors occur
 --rootdir=ROOTDIR   Define root directory for tests. Can be relative
            path: 'root_dir', './root_dir',
            'root_dir/another_dir/'; absolute path:
            '/home/user/root_dir'; path with variables:
            '$HOME/root_dir'.
collection:
 --collect-only, --co Only collect tests, don't execute them
 --pyargs       Try to interpret all arguments as Python packages
 --ignore=path     Ignore path during collection (multi-allowed)
 --ignore-glob=path  Ignore path pattern during collection (multi-
            allowed)
 --deselect=nodeid_prefix
            Deselect item (via node id prefix) during collection
            (multi-allowed)
 --confcutdir=dir   Only load conftest.py's relative to specified dir
 --noconftest     Don't load any conftest.py files
 --keep-duplicates   Keep duplicate tests
 --collect-in-virtualenv
            Don't ignore tests in a local virtualenv directory
 --import-mode={prepend,append,importlib}
            Prepend/append to sys.path when importing test
            modules and conftest files. Default: prepend.
 --doctest-modules   Run doctests in all .py modules
 --doctest-report={none,cdiff,ndiff,udiff,only_first_failure}
            Choose another output format for diffs on doctest
            failure
 --doctest-glob=pat  Doctests file matching pattern, default: test*.txt
 --doctest-ignore-import-errors
            Ignore doctest collection errors
 --doctest-continue-on-failure
            For a given doctest, continue to run after the first
            failure
test session debugging and configuration:
 --basetemp=dir    Base temporary directory for this test run.
            (Warning: this directory is removed if it exists.)
 -V, --version     Display pytest version and information about
            plugins. When given twice, also display information
            about plugins.
 -h, --help      Show help message and configuration info
 -p name        Early-load given plugin module name or entry point
            (multi-allowed). To avoid loading of plugins, use
            the `no:` prefix, e.g. `no:doctest`.
 --trace-config    Trace considerations of conftest.py files
 --debug=[DEBUG_FILE_NAME]
            Store internal tracing debug information in this log
            file. This file is opened with 'w' and truncated as
            a result, care advised. Default: pytestdebug.log.
 -o OVERRIDE_INI, --override-ini=OVERRIDE_INI
            Override ini option with "option=value" style, e.g.
            `-o xfail_strict=True -o cache_dir=cache`.
 --assert=MODE     Control assertion debugging tools.
            'plain' performs no assertion debugging.
            'rewrite' (the default) rewrites assert statements
            in test modules on import to provide assert
            expression information.
 --setup-only     Only setup fixtures, do not execute tests
 --setup-show     Show setup of fixtures while executing tests
 --setup-plan     Show what fixtures and tests would be executed but
            don't execute anything
logging:
 --log-level=LEVEL   Level of messages to catch/display. Not set by
            default, so it depends on the root/parent log
            handler's effective level, where it is "WARNING" by
            default.
 --log-format=LOG_FORMAT
            Log format used by the logging module
 --log-date-format=LOG_DATE_FORMAT
            Log date format used by the logging module
 --log-cli-level=LOG_CLI_LEVEL
            CLI logging level
 --log-cli-format=LOG_CLI_FORMAT
            Log format used by the logging module
 --log-cli-date-format=LOG_CLI_DATE_FORMAT
            Log date format used by the logging module
 --log-file=LOG_FILE  Path to a file when logging will be written to
 --log-file-mode={w,a}
            Log file open mode
 --log-file-level=LOG_FILE_LEVEL
            Log file logging level
 --log-file-format=LOG_FILE_FORMAT
            Log format used by the logging module
 --log-file-date-format=LOG_FILE_DATE_FORMAT
            Log date format used by the logging module
 --log-auto-indent=LOG_AUTO_INDENT
            Auto-indent multiline messages passed to the logging
            module. Accepts true|on, false|off or an integer.
 --log-disable=LOGGER_DISABLE
            Disable a logger by name. Can be passed multiple
            times.
[pytest] ini-options in the first pytest.ini|tox.ini|setup.cfg|pyproject.toml file found:
 markers (linelist):  Register new markers for test functions
 empty_parameter_set_mark (string):
            Default marker for empty parametersets
 norecursedirs (args): Directory patterns to avoid for recursion
 testpaths (args):   Directories to search for tests when no files or
            directories are given on the command line
 filterwarnings (linelist):
            Each line specifies a pattern for
            warnings.filterwarnings. Processed after
            -W/--pythonwarnings.
 consider_namespace_packages (bool):
            Consider namespace packages when resolving module
            names during import
 usefixtures (args):  List of default fixtures to be used with this
            project
 python_files (args): Glob-style file patterns for Python test module
            discovery
 python_classes (args):
            Prefixes or glob names for Python test class
            discovery
 python_functions (args):
            Prefixes or glob names for Python test function and
            method discovery
 disable_test_id_escaping_and_forfeit_all_rights_to_community_support (bool):
            Disable string escape non-ASCII characters, might
            cause unwanted side effects(use at your own risk)
 console_output_style (string):
            Console output: "classic", or with additional
            progress information ("progress" (percentage) |
            "count" | "progress-even-when-capture-no" (forces
            progress even when capture=no)
 verbosity_test_cases (string):
            Specify a verbosity level for test case execution,
            overriding the main level. Higher levels will
            provide more detailed information about each test
            case executed.
 xfail_strict (bool): Default for the strict parameter of xfail markers
            when not given explicitly (default: False)
 tmp_path_retention_count (string):
            How many sessions should we keep the `tmp_path`
            directories, according to
            `tmp_path_retention_policy`.
 tmp_path_retention_policy (string):
            Controls which directories created by the `tmp_path`
            fixture are kept around, based on test outcome.
            (all/failed/none)
 enable_assertion_pass_hook (bool):
            Enables the pytest_assertion_pass hook. Make sure to
            delete any previously generated pyc cache files.
 verbosity_assertions (string):
            Specify a verbosity level for assertions, overriding
            the main level. Higher levels will provide more
            detailed explanation when an assertion fails.
 junit_suite_name (string):
            Test suite name for JUnit report
 junit_logging (string):
            Write captured log messages to JUnit report: one of
            no|log|system-out|system-err|out-err|all
 junit_log_passing_tests (bool):
            Capture log information for passing tests to JUnit
            report:
 junit_duration_report (string):
            Duration time to report: one of total|call
 junit_family (string):
            Emit XML for schema: one of legacy|xunit1|xunit2
 doctest_optionflags (args):
            Option flags for doctests
 doctest_encoding (string):
            Encoding used for doctest files
 cache_dir (string):  Cache directory path
 log_level (string):  Default value for --log-level
 log_format (string): Default value for --log-format
 log_date_format (string):
            Default value for --log-date-format
 log_cli (bool):    Enable log display during test run (also known as
            "live logging")
 log_cli_level (string):
            Default value for --log-cli-level
 log_cli_format (string):
            Default value for --log-cli-format
 log_cli_date_format (string):
            Default value for --log-cli-date-format
 log_file (string):  Default value for --log-file
 log_file_mode (string):
            Default value for --log-file-mode
 log_file_level (string):
            Default value for --log-file-level
 log_file_format (string):
            Default value for --log-file-format
 log_file_date_format (string):
            Default value for --log-file-date-format
 log_auto_indent (string):
            Default value for --log-auto-indent
 pythonpath (paths):  Add paths to sys.path
 faulthandler_timeout (string):
            Dump the traceback of all threads if a test takes
            more than TIMEOUT seconds to finish
 addopts (args):    Extra command line options
 minversion (string): Minimally required pytest version
 required_plugins (args):
            Plugins that must be present for pytest to run
Environment variables:
 CI            When set (regardless of value), pytest knows it is running in a CI process and does not truncate summary info
 BUILD_NUMBER       Equivalent to CI
 PYTEST_ADDOPTS      Extra command line options
 PYTEST_PLUGINS      Comma-separated plugins to load during startup
 PYTEST_DISABLE_PLUGIN_AUTOLOAD Set to disable plugin auto-loading
 PYTEST_DEBUG       Set to enable debug tracing of pytest's internals

to see available markers type: pytest --markers
to see available fixtures type: pytest --fixtures
(shown according to specified file_or_dir or current dir if not specified; fixtures with leading '_' are only shown with the '-v' option

```

