# domain-protect Cloudflare manual scans
scans Cloudflare to detect:
* Subdomain NS delegations vulnerable to takeover
* Subdomains pointing to missing storage buckets
* Vulnerable CNAME records

## Python setup
* optionally create and activate a virtual environment
```
python -m venv .venv
source .venv/bin/activate
```
* install dependencies
```
pip install -r requirements.txt
```

## Set credentials
* In the Cloudflare console, My Profile, API Tokens, create an API Key
* Set as environment variables on your laptop
```
$ export CF_API_EMAIL='user@example.com'
$ export CF_API_KEY='00000000000000000000000000000000'
```

## subdomain NS delegations
```
python cf-ns-subdomain.py
```

## subdomains pointing to missing storage buckets
```
python cf-storage.py
```

## vulnerable CNAMEs
```
python cf-cname.py
```
