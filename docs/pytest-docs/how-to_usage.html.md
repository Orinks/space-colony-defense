Contents Menu Expand Light mode Dark mode Auto light/dark, in light mode Auto light/dark, in dark mode
Hide navigation sidebar
Hide table of contents sidebar
Skip to content
Back to top
Toggle Light / Dark / Auto color theme
Toggle table of contents sidebar
# How to invoke pytest¶
See also
Complete pytest command-line flag reference
In general, pytest is invoked with the command `pytest` (see below for other ways to invoke pytest). This will execute all tests in all files whose names follow the form `test_*.py` or `\*_test.py` in the current directory and its subdirectories. More generally, pytest follows standard test discovery rules.
## Specifying which tests to run¶
Pytest supports several ways to run and select tests from the command-line or from a file (see below for reading arguments from file).
**Run tests in a module**
```
pytesttest_mod.py

```

**Run tests in a directory**
```
pytesttesting/

```

**Run tests by keyword expressions**
```
pytest-k'MyClass and not method'

```

This will run tests which contain names that match the given _string expression_ (case-insensitive), which can include Python operators that use filenames, class names and function names as variables. The example above will run `TestMyClass.test_something` but not `TestMyClass.test_method_simple`. Use `""` instead of `''` in expression when running this on Windows
**Run tests by collection arguments**
Pass the module filename relative to the working directory, followed by specifiers like the class name and function name separated by `::` characters, and parameters from parameterization enclosed in `[]`.
To run a specific test within a module:
```
pytesttests/test_mod.py::test_func

```

To run all tests in a class:
```
pytesttests/test_mod.py::TestClass

```

Specifying a specific test method:
```
pytesttests/test_mod.py::TestClass::test_method

```

Specifying a specific parametrization of a test:
```
pytesttests/test_mod.py::test_func[x1,y2]

```

**Run tests by marker expressions**
To run all tests which are decorated with the `@pytest.mark.slow` decorator:
```
pytest-mslow

```

To run all tests which are decorated with the annotated `@pytest.mark.slow(phase=1)` decorator, with the `phase` keyword argument set to `1`:
```
pytest-m"slow(phase=1)"

```

For more information see marks.
**Run tests from packages**
```
pytest--pyargspkg.testing

```

This will import `pkg.testing` and use its filesystem location to find and run tests from.
**Read arguments from file**
Added in version 8.2.
All of the above can be read from a file using the `@` prefix:
```
pytest@tests_to_run.txt

```

where `tests_to_run.txt` contains an entry per line, e.g.:
```
tests/test_file.py
tests/test_mod.py::test_func[x1,y2]
tests/test_mod.py::TestClass
-m slow

```

This file can also be generated using `pytest --collect-only -q` and modified as needed.
## Getting help on version, option names, environment variables¶
```
pytest--version# shows where pytest was imported from
pytest--fixtures# show available builtin function arguments
pytest-h|--help# show help on command line and config file options

```

## Profiling test execution duration¶
Changed in version 6.0.
To get a list of the slowest 10 test durations over 1.0s long:
```
pytest--durations=10--durations-min=1.0

```

By default, pytest will not show test durations that are too small (<0.005s) unless `-vv` is passed on the command-line.
## Managing loading of plugins¶
### Early loading plugins¶
You can early-load plugins (internal and external) explicitly in the command-line with the `-p` option:
```
pytest -p mypluginmodule

```

The option receives a `name` parameter, which can be:
  * A full module dotted name, for example `myproject.plugins`. This dotted name must be importable.
  * The entry-point name of a plugin. This is the name passed to `importlib` when the plugin is registered. For example to early-load the pytest-cov plugin you can use:
```
pytest -p pytest_cov

```



### Disabling plugins¶
To disable loading specific plugins at invocation time, use the `-p` option together with the prefix `no:`.
Example: to disable loading the plugin `doctest`, which is responsible for executing doctest tests from text files, invoke pytest like this:
```
pytest-pno:doctest

```

## Other ways of calling pytest¶
### Calling pytest through `python -m pytest`¶
You can invoke testing through the Python interpreter from the command line:
```
python -m pytest [...]

```

This is almost equivalent to invoking the command line script `pytest [...]` directly, except that calling via `python` will also add the current directory to `sys.path`.
### Calling pytest from Python code¶
You can invoke `pytest` from Python code directly:
```
retcode = pytest.main()

```

this acts as if you would call “pytest” from the command line. It will not raise `SystemExit` but return the exit code instead. If you don’t pass it any arguments, `main` reads the arguments from the command line arguments of the process (`sys.argv`), which may be undesirable. You can pass in options and arguments explicitly:
```
retcode = pytest.main(["-x", "mytestdir"])

```

You can specify additional plugins to `pytest.main`:
```
# content of myinvoke.py
import sys
import pytest

class MyPlugin:
  def pytest_sessionfinish(self):
    print("*** test run reporting finishing")

if __name__ == "__main__":
  sys.exit(pytest.main(["-qq"], plugins=[MyPlugin()]))

```

Running it will show that `MyPlugin` was added and its hook was invoked:
```
$ python myinvoke.py
*** test run reporting finishing

```

Note
Calling `pytest.main()` will result in importing your tests and any modules that they import. Due to the caching mechanism of python’s import system, making subsequent calls to `pytest.main()` from the same process will not reflect changes to those files between the calls. For this reason, making multiple calls to `pytest.main()` from the same process (in order to re-run tests, for example) is not recommended.
