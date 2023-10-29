# Kubernetes Python Client for Cluster Health Check

This repository contains Python code developed using the Kubernetes Python client library for the purpose of performing a simple cluster health check. The script allows you to check the health of your Kubernetes cluster.

## Usage

You can run the Python script as follows:

```shell
python hc8.py

By default, the script will look for the default kubeconfig file. Optionally, you can specify a different kubeconfig file using the -c or --config option.

## Options

-h, --help: Show the help message and exit.
-c KCONFIG, --config KCONFIG: Specify the path to the kubeconfig file.

## Example

To run the script with a custom kubeconfig file, use the following command:
```shell
python hc8.py -c /path/to/custom-kubeconfig.yaml
