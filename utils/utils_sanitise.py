import json
import random
import string


def sanitise_wildcards(input_dict):
    ### takes dictionary object and replaces Route53 wildcard string with random value
    ### used by scan Lambda function

    # escape the intended double backslash with two extra backslashes
    route53_wildcard = "\\\\052"

    # generate 10 character random string
    prefix = "".join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(10))

    # identify as a wildcard
    prefix = f"{prefix}-wildcard"

    # convert dictionary object to string
    input_string = json.dumps(input_dict)

    # replace Route53 wildcard sequence with random string
    output_string = input_string.replace(route53_wildcard, prefix)

    # convert string back to dictionary object
    output_dict = json.loads(output_string)

    return output_dict


def restore_wildcard(domain):
    ### restores domain of format uf7gh39shs-wildcard.example.com to *.example.com

    subdomains = domain.split(".", 1)

    if len(subdomains[0]) == 19 and "-wildcard" in subdomains[0]:

        updated_subdomains = ["*", subdomains[1]]

        wildcard_domain = ".".join(updated_subdomains)

        return wildcard_domain

    return domain


def sanitise_domain(domain):
    ### takes domain and replaces a wildcard with random value
    ### used by update Lambda function

    # generate 10 character random string
    prefix = "".join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(10))

    # identify as a wildcard
    prefix = f"{prefix}-wildcard"

    # replace wildcard with prefix
    domain = domain.replace("*", prefix)

    return domain
