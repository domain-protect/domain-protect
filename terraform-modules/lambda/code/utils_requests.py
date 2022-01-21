import requests


def vulnerable_storage(domain_name, https=True, http=True, https_timeout=1, http_timeout=1):

    if https:
        try:
            response = requests.get("https://" + domain_name, timeout=https_timeout)
            if "NoSuchBucket" in response.text:
                return True

        except (
            requests.exceptions.SSLError,
            requests.exceptions.ConnectionError,
            requests.exceptions.ReadTimeout,
            requests.exceptions.TooManyRedirects,
        ):
            pass

    if http:
        try:
            response = requests.get("http://" + domain_name, timeout=http_timeout)
            if "NoSuchBucket" in response.text:
                return True

        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.ReadTimeout,
            requests.exceptions.TooManyRedirects,
        ):
            pass

    return False
