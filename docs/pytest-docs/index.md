Contents Menu Expand Light mode Dark mode Auto light/dark, in light mode Auto light/dark, in dark mode
Hide navigation sidebar
Hide table of contents sidebar
Skip to content
Back to top
Toggle Light / Dark / Auto color theme
Toggle table of contents sidebar
# pytest: helps you write better programs¶
The `pytest` framework makes it easy to write small, readable tests, and can scale to support complex functional testing for applications and libraries.
`pytest` requires: Python 3.8+ or PyPy3.
**PyPI package name** : pytest
## A quick example¶
```
# content of test_sample.py
def inc(x):
  return x + 1

def test_answer():
  assert inc(3) == 5

```

To execute it:
```
$ pytest
=========================== test session starts ============================
platform linux -- Python 3.x.y, pytest-8.x.y, pluggy-1.x.y
rootdir: /home/sweet/project
collected 1 item
test_sample.py F                           [100%]
================================= FAILURES =================================
_______________________________ test_answer ________________________________
  def test_answer():
>    assert inc(3) == 5
E    assert 4 == 5
E    + where 4 = inc(3)
test_sample.py:6: AssertionError
========================= short test summary info ==========================
FAILED test_sample.py::test_answer - assert 4 == 5
============================ 1 failed in 0.12s =============================

```

Due to `pytest`’s detailed assertion introspection, only plain `assert` statements are used. See Get started for a basic introduction to using pytest.
## Features¶
  * Detailed info on failing assert statements (no need to remember `self.assert*` names)
  * Auto-discovery of test modules and functions
  * Modular fixtures for managing small or parametrized long-lived test resources
  * Can run unittest (including trial) test suites out of the box
  * Python 3.8+ or PyPy 3
  * Rich plugin architecture, with over 1300+ external plugins and thriving community


## Documentation¶
  * Get started - install pytest and grasp its basics in just twenty minutes
  * How-to guides - step-by-step guides, covering a vast range of use-cases and needs
  * Reference guides - includes the complete pytest API reference, lists of plugins and more
  * Explanation - background, discussion of key topics, answers to higher-level questions


## Bugs/Requests¶
Please use the GitHub issue tracker to submit bugs or request features.
## Support pytest¶
Open Collective is an online funding platform for open and transparent communities. It provides tools to raise money and share your finances in full transparency.
It is the platform of choice for individuals and companies that want to make one-time or monthly donations directly to the project.
See more details in the pytest collective.
## pytest for enterprise¶
Available as part of the Tidelift Subscription.
The maintainers of pytest and thousands of other packages are working with Tidelift to deliver commercial support and maintenance for the open source dependencies you use to build your applications. Save time, reduce risk, and improve code health, while paying the maintainers of the exact dependencies you use.
Learn more.
### Security¶
pytest has never been associated with a security vulnerability, but in any case, to report a security vulnerability please use the Tidelift security contact. Tidelift will coordinate the fix and disclosure.
