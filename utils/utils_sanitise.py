import json
import random
import string


def sanitise_wildcards(input_dict):
    ### takes a dictionary object and replaces a wildcard string with a random value

    # escape the intended double backslash with two extra backslashes
    route53_wildcard = "\\\\052"

    # generate 10 character random string
    prefix = "".join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(10))

    # identity as a wildcard
    prefix = f"{prefix}-wildcard"

    # convert dictionary object to string
    input_string = json.dumps(input_dict)

    # replace Route53 wildcard sequence with random string
    output_string = input_string.replace(route53_wildcard, prefix)

    # convert string back to dictionary object
    output_dict = json.loads(output_string)

    return output_dict
