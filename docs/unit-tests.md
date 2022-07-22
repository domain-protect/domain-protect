# Unit Tests

## Overview

Domain protect uses `pytest` to run unit tests against the code, and will fail the build if any tests fail.  All unit tests live under the `unittest` folder in the root of the solution.

## Running tests locally

See [Automated Tests](automated-tests.md) for details on how to set up the tests locally.

## Creating new unit tests

* Unit tests should each only test one thing, and mock out any dependencies (including other internal functions that are being called) to keep them isolated.  Prefer multiple tests over fewer, larger tests
* Use the `patch` attribute from `unittest.mock` to inject dependencies into your tests
* Where required use the built-in unittest.mock assertions to validate calls - i.e. `mock_object.assert_called_once_with(arg)`


[back to Automated Tests](automated-tests.md)  
[back to README](../README.md)