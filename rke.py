#!/usr/bin/env python

import configparser
import requests
import sys
from argparse import ArgumentParser
from chopt import chopt
from pathlib import Path
from urllib3.exceptions import InsecureRequestWarning

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


def get_args():
    parser = ArgumentParser(
        description=("Get information back from the Rancher API."),
    )
    parser.add_argument(
        "cluster_names",
        nargs="*",
        default=[],
        help="Names of your Rancher clusters, "
        + "if none are specified you will be presented with a list"
        + " of available clusters and asked to choose.",
    )
    parser.add_argument(
        "-t",
        "--templates",
        action="store_true",
        help="show linode template users",
    )
    parser.add_argument(
        "-n",
        "--nodes",
        action="store_true",
        help="show cluster's nodes information.",
    )
    parser.add_argument(
        "-k",
        "--kubeconfig",
        action="store_true",
        help="write kubeconfig to a local file",
    )
    parser.add_argument(
        "-d",
        "--destination",
        default=f"{Path.home()}/.kube",
        help="directory to store kubeconfig (default: %(default)s)",
    )
    parser.add_argument(
        "-c",
        "--config",
        default=f"{Path.home()}/.rancher.ini",
        help="ini file for RKE configuration " + "(default: %(default)s)",
    )
    return parser.parse_args()


def get_all_nodetemplates():
    try:
        response = requests.get(
            f"{endpoint}/nodetemplates",
            auth=auth,
            verify=False,
        )
        if "data" in response.json():
            return response.json()["data"]
    except Exception as error:
        raise error


def get_linode_users(nodetemplates):
    for template in nodetemplates:
        if (
            "linodeConfig" in template
            and "authorizedUsers" in template["linodeConfig"]
            and template["linodeConfig"]["authorizedUsers"] != ""
        ):
            users = template["linodeConfig"]["authorizedUsers"].split(",")
            print(f"\n{template['name']} users:")
            print("\n".join(users))


def get_all_clusters():
    try:
        response = requests.get(
            f"{endpoint}/clusters",
            auth=auth,
            verify=False,
        )
        if "data" in response.json():
            return response.json()["data"]
    except Exception as error:
        raise error


def get_cluster_names(clusters):
    return [
        c["appliedSpec"]["displayName"]
        for c in clusters
        if (
            "appliedSpec" in c
            and "displayName" in c["appliedSpec"]
            and c["appliedSpec"]["displayName"] != ""
        )
    ]


def get_rke_config(configpath):
    config = configparser.ConfigParser()
    config.read(configpath)
    endpoint = config["url"]["endpoint"]
    access_key = config["keys"]["access"]
    secret_key = config["keys"]["secret"]
    auth = requests.auth.HTTPBasicAuth(access_key, secret_key)

    return endpoint, auth


def get_cluster(cluster_name):
    try:
        return requests.get(
            f"{endpoint}/clusters?name={cluster_name}",
            auth=auth,
            verify=False,
        ).json()["data"][0]
    except IndexError:
        print(f"Can't find a cluster called {cluster_name} at {endpoint}")
        sys.exit(1)


def get_cluster_nodes(cluster):
    if "rancherKubernetesEngineConfig" in cluster["appliedSpec"]:
        return cluster["appliedSpec"]["rancherKubernetesEngineConfig"]["nodes"]


def get_kubeconfig(cluster):
    generate_kubeconfig_url = cluster["actions"]["generateKubeconfig"]

    return requests.post(
        generate_kubeconfig_url,
        auth=auth,
        verify=False,
    ).json()["config"]


def write_kubeconfig(destination, cluster):
    kubeconfig_path = f"{destination}/{cluster_name}.yml"

    print(f"Writing {cluster_name} kubeconfig to {kubeconfig_path}\n")
    kubeconfig = get_kubeconfig(cluster)
    with open(kubeconfig_path, "w") as f:
        f.write(kubeconfig)


def get_node(node_id):
    return requests.get(
        f"{endpoint}/nodes?id={node_id}", auth=auth, verify=False
    ).json()["data"][0]


def get_node_template(node_template_id):
    try:
        response = requests.get(
            f"{endpoint}/nodetemplates?id={node_template_id}",
            auth=auth,
            verify=False,
        )
        if "data" in response.json():
            return response.json()["data"][0]
    except Exception as error:
        raise error


if __name__ == "__main__":
    args = get_args()
    cluster_names = args.cluster_names
    destination = args.destination
    endpoint, auth = get_rke_config(args.config)

    if args.templates:
        get_linode_users(get_all_nodetemplates())
        sys.exit(0)

    if len(cluster_names) < 1:
        cluster_names = chopt(get_cluster_names(get_all_clusters()))

    for cluster_name in cluster_names:
        cluster = get_cluster(cluster_name)
        print(f"\n{cluster_name} API Endpoint: {cluster['apiEndpoint']}")

        if args.kubeconfig:
            write_kubeconfig(destination, cluster)

        if args.nodes:
            nodes = get_cluster_nodes(cluster)
            for n in nodes:
                node = get_node(n["nodeId"])
                node_template = get_node_template(node["nodeTemplateId"])
                print(
                    f"HOSTNAME: {node['hostname']}\n"
                    + f"EXTERNAL IP: {node['externalIpAddress']}\n"
                    + f"INTERNAL IP: {node['ipAddress']}\n"
                    + f"OS: {node['info']['os']['operatingSystem']}\n"
                    + f"CONTROL PLANE: {node['controlPlane']}\n"
                    + f"ETCD: {node['etcd']}\n"
                    + f"WORKER: {node['worker']}\n"
                    + f"TEMPLATE: {node_template['name']}\n"
                    + f"TEMPLATE DRIVER: {node_template['driver']}\n"
                )
