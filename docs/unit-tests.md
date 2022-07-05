# Unit Tests

## Overview

Domain protect uses `pytest` to run unit tests against the code, and will fail the build if any tests fail.  All unit tests live under the `unittest` folder in the root of the solution.

## Creating new tests

* All new code should have unit tests - if possible follow test driven development (TDD) methodologies to ensure high test coverage
* New unit tests must be created under the unittests folder at the root of the solution
* The folder structure under the unitetests folder must follow the folder structure of the solution (i.e. tests for a file under utils must live in unittests/utils)
* Test files must be named `test_[name_of_file_under_test]` - i.e. a test for the `utils_dates.py` file lives in `test_utils_dates.py`
* Each test must be a new function, no test classes
* Test functions names must follow the pattern `test_[function_under_test]_[description_of_assertion]` - e.g. `test_generate_role_arn_puts_role_at_the_end`
* Tests must follow the Arrange - Act - Assert pattern
* Unit tests should each only test one thing, and mock out any dependencies to keep them isolated.  Prefer multiple tests over fewer, larger tests
* Use the `patch` attribute from `unittest.mock` to inject dependencies into your tests
* Where required use the built-in unittest.mock assertions to validate calls - i.e. `mock_object.assert_called_once_with(arg)`
* Prefer black box testing over white/grey box testing where possible.  This will lead to developing smaller pure functions which are easier to test, grok, have no side effects, and the tests will be less brittle
* Assertions must use the assertpy library
* Unit test files must follow the same formatting and coding standards as code files

[back to README](../README.md)