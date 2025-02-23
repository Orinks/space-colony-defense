Contents Menu Expand Light mode Dark mode Auto light/dark, in light mode Auto light/dark, in dark mode
Hide navigation sidebar
Hide table of contents sidebar
Skip to content
Back to top
Toggle Light / Dark / Auto color theme
Toggle table of contents sidebar
# Flaky tests¶
A “flaky” test is one that exhibits intermittent or sporadic failure, that seems to have non-deterministic behaviour. Sometimes it passes, sometimes it fails, and it’s not clear why. This page discusses pytest features that can help and other general strategies for identifying, fixing or mitigating them.
## Why flaky tests are a problem¶
Flaky tests are particularly troublesome when a continuous integration (CI) server is being used, so that all tests must pass before a new code change can be merged. If the test result is not a reliable signal – that a test failure means the code change broke the test – developers can become mistrustful of the test results, which can lead to overlooking genuine failures. It is also a source of wasted time as developers must re-run test suites and investigate spurious failures.
## Potential root causes¶
### System state¶
Broadly speaking, a flaky test indicates that the test relies on some system state that is not being appropriately controlled - the test environment is not sufficiently isolated. Higher level tests are more likely to be flaky as they rely on more state.
Flaky tests sometimes appear when a test suite is run in parallel (such as use of pytest-xdist). This can indicate a test is reliant on test ordering.
  * Perhaps a different test is failing to clean up after itself and leaving behind data which causes the flaky test to fail.
  * The flaky test is reliant on data from a previous test that doesn’t clean up after itself, and in parallel runs that previous test is not always present
  * Tests that modify global state typically cannot be run in parallel.


### Overly strict assertion¶
Overly strict assertions can cause problems with floating point comparison as well as timing issues. `pytest.approx()` is useful here.
### Thread safety¶
pytest is single-threaded, executing its tests always in the same thread, sequentially, never spawning any threads itself.
Even in case of plugins which run tests in parallel, for example pytest-xdist, usually work by spawning multiple _processes_ and running tests in batches, without using multiple threads.
It is of course possible (and common) for tests and fixtures to spawn threads themselves as part of their testing workflow (for example, a fixture that starts a server thread in the background, or a test which executes production code that spawns threads), but some care must be taken:
  * Make sure to eventually wait on any spawned threads – for example at the end of a test, or during the teardown of a fixture.
  * Avoid using primitives provided by pytest (`pytest.warns()`, `pytest.raises()`, etc) from multiple threads, as they are not thread-safe.


If your test suite uses threads and your are seeing flaky test results, do not discount the possibility that the test is implicitly using global state in pytest itself.
## Related features¶
### Xfail strict¶
pytest.mark.xfail with `strict=False` can be used to mark a test so that its failure does not cause the whole build to break. This could be considered like a manual quarantine, and is rather dangerous to use permanently.
### PYTEST_CURRENT_TEST¶
`PYTEST_CURRENT_TEST` may be useful for figuring out “which test got stuck”. See PYTEST_CURRENT_TEST environment variable for more details.
### Plugins¶
Rerunning any failed tests can mitigate the negative effects of flaky tests by giving them additional chances to pass, so that the overall build does not fail. Several pytest plugins support this:
  * pytest-rerunfailures
  * pytest-replay: This plugin helps to reproduce locally crashes or flaky tests observed during CI runs.
  * pytest-flakefinder - blog post


Plugins to deliberately randomize tests can help expose tests with state problems:
  * pytest-random-order
  * pytest-randomly


## Other general strategies¶
### Split up test suites¶
It can be common to split a single test suite into two, such as unit vs integration, and only use the unit test suite as a CI gate. This also helps keep build times manageable as high level tests tend to be slower. However, it means it does become possible for code that breaks the build to be merged, so extra vigilance is needed for monitoring the integration test results.
### Video/screenshot on failure¶
For UI tests these are important for understanding what the state of the UI was when the test failed. pytest-splinter can be used with plugins like pytest-bdd and can save a screenshot on test failure, which can help to isolate the cause.
### Delete or rewrite the test¶
If the functionality is covered by other tests, perhaps the test can be removed. If not, perhaps it can be rewritten at a lower level which will remove the flakiness or make its source more apparent.
### Quarantine¶
Mark Lapierre discusses the Pros and Cons of Quarantined Tests in a post from 2018.
### CI tools that rerun on failure¶
Azure Pipelines (the Azure cloud CI/CD tool, formerly Visual Studio Team Services or VSTS) has a feature to identify flaky tests and rerun failed tests.
## Research¶
This is a limited list, please submit an issue or pull request to expand it!
  * Gao, Zebao, Yalan Liang, Myra B. Cohen, Atif M. Memon, and Zhen Wang. “Making system user interactive tests repeatable: When and what should we control?.” In _Software Engineering (ICSE), 2015 IEEE/ACM 37th IEEE International Conference on_ , vol. 1, pp. 55-65. IEEE, 2015. PDF
  * Palomba, Fabio, and Andy Zaidman. “Does refactoring of test smells induce fixing flaky tests?.” In _Software Maintenance and Evolution (ICSME), 2017 IEEE International Conference on_ , pp. 1-12. IEEE, 2017. PDF in Google Drive
  * Bell, Jonathan, Owolabi Legunsen, Michael Hilton, Lamyaa Eloussi, Tifany Yung, and Darko Marinov. “DeFlaker: Automatically detecting flaky tests.” In _Proceedings of the 2018 International Conference on Software Engineering_. 2018. PDF
  * Dutta, Saikat and Shi, August and Choudhary, Rutvik and Zhang, Zhekun and Jain, Aryaman and Misailovic, Sasa. “Detecting flaky tests in probabilistic and machine learning applications.” In _Proceedings of the 29th ACM SIGSOFT International Symposium on Software Testing and Analysis (ISSTA)_ , pp. 211-224. ACM, 2020. PDF


## Resources¶
  * Eradicating Non-Determinism in Tests by Martin Fowler, 2011
  * No more flaky tests on the Go team by Pavan Sudarshan, 2012
  * The Build That Cried Broken: Building Trust in your Continuous Integration Tests talk (video) by Angie Jones at SeleniumConf Austin 2017
  * Test and Code Podcast: Flaky Tests and How to Deal with Them by Brian Okken and Anthony Shaw, 2018
  * Microsoft:
    * How we approach testing VSTS to enable continuous delivery by Brian Harry MS, 2017
    * Eliminating Flaky Tests blog and talk (video) by Munil Shah, 2017
  * Google:
    * Flaky Tests at Google and How We Mitigate Them by John Micco, 2016
    * Where do Google’s flaky tests come from? by Jeff Listfield, 2017


