# Code Standards

[pre-commit](https://pre-commit.com) is used to ensure code standards are met, includes tests with automated fixes using:
```
bandit
black
checkov
prospector
terraform fmt
```
* run pre-commit locally:
```
pre-commit run --all-files
```
* if `Prospector` reports import errors, set your Python Path, e.g.
```
$ export PYTHONPATH="${PYTHONPATH}:/Users/paul/src/github.com/ovotech/domain-protect"
```
* pre-commit is also used by the GitHub Actions workflow
