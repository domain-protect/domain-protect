# Code Standards

* GitHub Actions pipeline includes tests using:
```
bandit
black
checkov
prospector
terraform fmt
```
* if testing with `Prospector` locally, set your Python Path, e.g.
```
$ export PYTHONPATH="${PYTHONPATH}:/Users/paul/src/github.com/ovotech/domain-protect"
```
* test Terraform locally using Checkov:
```
checkov --config-file .config/sast_terraform_checkov_cli.yml --directory .
```
