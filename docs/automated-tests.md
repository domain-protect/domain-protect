# Automated Tests

## Overview
Domain protect has 2 types of automated tests, unit tests and integration tests.  New features and enhancements must include both types of tests to ensure future changes do not break the functionality.

- Unit Tests - Test a single "unit" of code (i.e. a single function) and mock out all other functions it calls.  Ensures that unit works as expected in isolation.
- Integration Tests - Test a single flow through the application, involving multiple units interacting, mocking out external dependencies.  Ensures the units work together as expected

Domain protect uses `pytest` to run automated tests against the code, and will fail the build if any tests fail.

## Running tests locally

For running tests locally you have 2 options, via the command line or in vscode (there are other IDEs available however we won't document them here).

For both of these it's recommended you run them from within a virtual env by running the following:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

### Command line

With the above steps complete simply run the command `pytest unittest` from the root of the project to run the unit tests, `pytest integration_tests` to run the integration tests, or just `pytest` to run them both.

### VS Code

* Install the [python extension for vscode](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
* Set up vscode to use pytest
    * Either do this through the vscode settings UI
    * or paste the following JSON into `./vscode/settings.json`:
    ```
    {
        "python.testing.unittestEnabled": false,
        "python.testing.pytestEnabled": true,
    }
    ```
* Go to the testing tab on the left menu and from there you can run all the tests using the "Run Tests" button at the top

<kbd>
  <img src="images/test-view.png" width="600" alt="Current resources example">
</kbd>

## General Rules

* All new code should have tests - follow test driven development (TDD) methodologies to ensure high test coverage
* Coverage is monitored by the build pipeline. Should the overall coverage percent drop due to new code not being covered by tests then the build will fail and your changes will not be merged into the main branch.
* New unit tests must be created under the unittests folder at the root of the solution, integration tests under the integration_tests folder.
* The folder structure under the unittests/integration_tests folder must follow the folder structure of the solution (i.e. tests for a file under utils must live in unittests/utils)
* Test files must be named `test_[name_of_file_under_test]` - i.e. a test for the `aws-alias_s3.py` file lives in `test_aws-alias_s3.py`
* Each test must be a new function, no test classes
* Test functions names must follow the pattern `test_[function_under_test]_[description_of_assertion]` - e.g. `test_generate_role_arn_puts_role_at_the_end`
* Tests must follow the Arrange - Act - Assert pattern (also known as Given - When - Then)
* Prefer black box testing over white/grey box testing where possible.  This will lead to developing smaller pure functions which are easier to test, grok, have no side effects, and the tests will be less brittle
* Assertions must use the assertpy library
* Test files must follow the same formatting and coding standards as code files

## Unit Tests

For more info on unit tests see the [Unit Tests Documentation](unit-tests.md)

## Integration Tests

For more info on integration tests see the [Integration Tests Documentation](integration-tests.md)