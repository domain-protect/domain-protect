import os
import logging
import ipaddress
from botocore import exceptions
from utils.utils_aws import assume_role
from utils.utils_db_ips import db_check_ip

allowed_regions = os.environ["ALLOWED_REGIONS"][1:][:-1]
allowed_regions = allowed_regions.replace(" ", "")
allowed_regions = allowed_regions.replace("'", "")
allowed_regions = allowed_regions.split(",")
ip_time_limit = os.environ["IP_TIME_LIMIT"]


def get_all_regions(account_id, account_name):
    # get regions within each account in case extra regions are enabled

    try:
        boto3_session = assume_role(account_id)

        try:
            ec2 = boto3_session.client("ec2")

            response = ec2.describe_regions()
            return [region["RegionName"] for region in response["Regions"]]

        except exceptions.ClientError as e:
            print(e.response["Error"]["Code"])
            logging.error(
                "ERROR: Lambda execution role requires ec2:DescribeRegions permission in %a account",
                account_name,
            )

    except exceptions.ClientError as e:
        print(e.response["Error"]["Code"])
        logging.error("ERROR: unable to assume role in %a account %s", account_name, account_id)

    return []


def get_regions(account_id, account_name):

    if allowed_regions != ["all"]:
        regions = allowed_regions

    else:
        regions = get_all_regions(account_id, account_name)

    return regions


def get_eip_addresses(account_id, account_name, region):
    # get EC2 elastic IP addresses

    ec2_elastic_ips = []

    try:
        boto3_session = assume_role(account_id, region)
        ec2 = boto3_session.client("ec2")

        try:
            response = ec2.describe_addresses()
            addresses = response["Addresses"]

            for address in addresses:
                try:
                    ec2_elastic_ip = address["PublicIp"]
                    ec2_elastic_ips.append(ec2_elastic_ip)

                except KeyError:
                    pass

        except exceptions.ClientError as e:
            print(e.response["Error"]["Code"])
            logging.error(
                "ERROR: Lambda role requires ec2:DescribeAddresses permission in %r for %a account",
                region,
                account_name,
            )

    except (AttributeError, Exception):
        logging.error("ERROR: unable to assume role in %r for %a account", region, account_name)

    return ec2_elastic_ips


def get_ec2_addresses(account_id, account_name, region):

    try:
        boto3_session = assume_role(account_id, region)
        ec2 = boto3_session.client("ec2")

        public_ip_list = []

        try:
            paginator_reservations = ec2.get_paginator("describe_instances")
            pages_reservations = paginator_reservations.paginate()
            for page_reservations in pages_reservations:
                for reservation in page_reservations["Reservations"]:
                    instances = [i for i in reservation["Instances"] if "PublicIpAddress" in i]
                    for instance in instances:
                        public_ip = instance["PublicIpAddress"]
                        public_ip_list.append(public_ip)

            return public_ip_list

        except Exception:
            logging.error(
                "ERROR: Lambda execution role requires ec2:DescribeInstances permission in %a account", account_name
            )

    except (AttributeError, Exception):
        logging.error("ERROR: unable to assume role in %a account %s", account_name, account_id)

    return []


def get_accelerator_addresses(account_id, account_name):

    try:
        boto3_session = assume_role(account_id, "us-west-2")  # Oregon region required for Global Accelerator
        globalaccelerator = boto3_session.client("globalaccelerator")

        accelerator_ip_list = []

        try:
            accelerators = globalaccelerator.list_accelerators()
            for accelerator in accelerators["Accelerators"]:
                ip_sets = accelerator["IpSets"]
                for ip_set in ip_sets:
                    ip_addresses = ip_set["IpAddresses"]
                    for ip_address in ip_addresses:
                        accelerator_ip_list.append(ip_address)

            return accelerator_ip_list

        except Exception:
            logging.error(
                "ERROR: Lambda execution role requires globalaccelerator:ListAccelerators permission in %a account for us-west-2 region",
                account_name,
            )

    except (AttributeError, Exception):
        logging.error("ERROR: unable to assume role in %a account %s", account_name, account_id)

    return []


def list_ecs_clusters(account_id, account_name, region):

    try:
        boto3_session = assume_role(account_id, region)
        ecs = boto3_session.client("ecs")

        cluster_list = []

        try:
            paginator = ecs.get_paginator("list_clusters")
            pages = paginator.paginate()
            for page in pages:
                for cluster in page["clusterArns"]:
                    cluster_list.append(cluster)

            return cluster_list

        except Exception:
            logging.error(
                "ERROR: Lambda execution role requires ecs:ListClusters permission in %a account", account_name
            )

    except (AttributeError, Exception):
        logging.error("ERROR: unable to assume role in %a account %s", account_name, account_id)

    return []


def list_ecs_cluster_tasks(account_id, account_name, region, cluster):

    try:
        boto3_session = assume_role(account_id, region)
        ecs = boto3_session.client("ecs")

        task_list = []

        try:
            paginator = ecs.get_paginator("list_tasks")
            pages = paginator.paginate(cluster=cluster)
            for page in pages:
                for task in page["taskArns"]:
                    task_list.append(task)

            return task_list

        except Exception:
            logging.error("ERROR: Lambda execution role requires ecs:ListTasks permission in %a account", account_name)

    except (AttributeError, Exception):
        logging.error("ERROR: unable to assume role in %a account %s", account_name, account_id)

    return []


def get_ecs_task_enis(task_json):

    enis = []

    attachments = task_json["attachments"]

    if len(attachments) > 0:
        for attachment in attachments:

            details = attachment["details"]

            if len(details) > 0:

                for detail in details:
                    if "eni-" in detail["value"]:

                        enis.append(detail["value"])

        return enis

    return []


def get_ecs_enis(account_id, account_name, region, cluster, task):

    enis = []

    try:
        boto3_session = assume_role(account_id, region)
        ecs = boto3_session.client("ecs")

        try:
            tasks = ecs.describe_tasks(cluster=cluster, tasks=[task])["tasks"]

            for task_json in tasks:

                task_enis = get_ecs_task_enis(task_json)

                for task_eni in task_enis:
                    enis.append(task_eni)

            return enis

        except Exception:
            logging.error(
                "ERROR: Lambda execution role requires ecs:DescribeTasks permission in %a account", account_name
            )

    except (AttributeError, Exception):
        logging.error("ERROR: unable to assume role in %a account %s", account_name, account_id)

    return []


def get_eni_public_ips(account_id, account_name, region, eni):

    public_ips = []

    try:
        boto3_session = assume_role(account_id, region)
        ec2 = boto3_session.client("ec2")

        try:

            network_interfaces = ec2.describe_network_interfaces(NetworkInterfaceIds=[eni])

            for network_interface in network_interfaces["NetworkInterfaces"]:
                try:
                    public_ip = network_interface["Association"]["PublicIp"]
                    public_ips.append(public_ip)

                except KeyError:
                    pass

            return public_ips

        except Exception:
            logging.error(
                "ERROR: Lambda execution role requires ec2:DescribeNetworkInterfaces permission in %a account",
                account_name,
            )

    except (AttributeError, Exception):
        logging.error("ERROR: unable to assume role in %a account %s", account_name, account_id)

    return []


def list_ecs_task_ips(account_id, account_name, region, cluster, task):

    ecs_task_ips = []

    enis = get_ecs_enis(account_id, account_name, region, cluster, task)

    for eni in enis:
        public_ips = get_eni_public_ips(account_id, account_name, region, eni)

        for public_ip in public_ips:

            ecs_task_ips.append(public_ip)

        return ecs_task_ips

    return []


def get_ecs_addresses(account_id, account_name, region):

    ecs_ips = []

    clusters = list_ecs_clusters(account_id, account_name, region)
    if len(clusters) > 0:
        for cluster in clusters:
            tasks = list_ecs_cluster_tasks(account_id, account_name, region, cluster)

            if len(tasks) > 0:
                for task in tasks:
                    public_ips = list_ecs_task_ips(account_id, account_name, region, cluster, task)

                    for public_ip in public_ips:
                        ecs_ips.append(public_ip)

        return ecs_ips

    return []


def vulnerable_aws_a_record(ip_prefixes, ip_address, ip_time_limit):

    if ipaddress.ip_address(ip_address).is_private:
        return False

    if db_check_ip(ip_address, int(ip_time_limit)):  # check if IP address is in database and seen in last 48 hours
        return False

    for ip_prefix in ip_prefixes:
        if ipaddress.ip_address(ip_address) in ipaddress.ip_network(ip_prefix):
            return True

    return False
