#########################################################################
# taeho.choi@optus.com.au
# checking overall kubernetes cluster health status with python client
# 28 Oct 2023                     
#########################################################################
import sys
import argparse
from kubernetes import client, config

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Helpers:
    @staticmethod
    def endpoint_ch(kconfig):
        config.load_kube_config(kconfig)
        api_instance = client.ApiClient()
        response = api_instance.call_api(resource_path="/healthz",
                                                            method="GET",
                                                            query_params={"verbose": "true"},
                                                            response_type=str)
        return  print(response[0])

    @staticmethod
    def total_dep(kconfig):
        config.load_kube_config(kconfig)
        # Create a Kubernetes API client
        api_instance = client.CoreV1Api()
        # List all namespaces in the cluster
        namespaces = api_instance.list_namespace()
        # Initialize a counter for deployments
        total_deployments = 0
        for namespace in namespaces.items:
            # List all deployments in the current namespace
            deployments = client.AppsV1Api().list_namespaced_deployment(namespace.metadata.name)
            # Add the count of deployments in this namespace to the total count
            total_deployments += len(deployments.items)
        print(f"Total number of deployments across all namespaces: {total_deployments}")
        return None
    
    @staticmethod
    def total_abnormal_pod(kconfig):
        # Load the Kubernetes configuration from the default location
        config.load_kube_config(kconfig)
        # Create a Kubernetes API client
        api_instance = client.CoreV1Api()
        # Define the pod status to exclude (e.g., "Running" or "Completed")
        excluded_statuses = ["Completed","Running","Succeeded"]
        # Initialize a counter for pods
        total_pods = 0
        response= api_instance.list_pod_for_all_namespaces()
        print(f"Total number of pod is: {len(response.items)}")
        filtered_pods = [pod for pod in response.items if pod.status.phase not in excluded_statuses]
        # Add the count of filtered pods in this namespace to the total count
        total_pods += len(filtered_pods)
        print(f"Total number of non-{', '.join(excluded_statuses)} pods across all namespaces: {total_pods}")
        if filtered_pods: 
            print([i.metadata.name for i in filtered_pods])
        return None
    
    @staticmethod
    def total_abnormal_node(kconfig):
        config.load_kube_config(kconfig)
        # Create a Kubernetes API client
        api_instance = client.CoreV1Api()
        # Define the node status to exclude (e.g., "Ready")
        excluded_statuses = ["Ready"]
        # Initialize a counter for nodes
        total_nodes = 0
        # List all nodes in the cluster
        response = api_instance.list_node()

        # Check for node ready status
        filtered_nodes = [node for node in response.items if node.status.conditions[4].type not in excluded_statuses]
        print(f"Total number of nodes is: {len(response.items)}")
        print(f"Total number of nodes not in {', '.join(excluded_statuses)} status: {len(filtered_nodes)}")
        if filtered_nodes: 
            print([i.metadata.name for i in filtered_nodes])
        
        # Check for node MemoryPressure status - status.conditions[1].status
        filtered_nodes = [node for node in response.items if node.status.conditions[1].status == True ]
        print(f"Total number of nodes in MemoryPressure status: {len(filtered_nodes)}")
        if filtered_nodes: 
            print([i.metadata.name for i in filtered_nodes])

        # Check for node DiskPressure status - status.conditions[2].status
        filtered_nodes = [node for node in response.items if node.status.conditions[2].status == True ]
        print(f"Total number of nodes in DiskPressure status: {len(filtered_nodes)}")
        if filtered_nodes: 
            print([i.metadata.name for i in filtered_nodes])

        # Check for node PIDPressure status - status.conditions[3].status
        filtered_nodes = [node for node in response.items if node.status.conditions[3].status == True ]
        print(f"Total number of nodes in PIDPressure status: {len(filtered_nodes)}")
        if filtered_nodes: 
            print([i.metadata.name for i in filtered_nodes])
        return None

    @staticmethod
    def total_svc(kconfig):
        # Load the Kubernetes configuration from the default location
        config.load_kube_config(kconfig)
        # Create a Kubernetes API client
        api_instance = client.CoreV1Api()
        # Define the pod status to exclude (e.g., "Running" or "Completed")
        # Initialize a counter for pods
        total_svc = 0
        response= api_instance.list_service_for_all_namespaces()
        print(f"Total number of svc is: {len(response.items)}")

        #Check for LB type svc
        filtered_svcs = [svc for svc in response.items if svc.spec.type == 'LoadBalancer']
        print(f"Total number of LB type svc is: {len(filtered_svcs)}")
        if filtered_svcs: 
            print(f"Here is svc:lb_ip mapping: ")
            print(list(zip([i.metadata.name for i in filtered_svcs],[i.status.load_balancer.ingress[0].ip for i in filtered_svcs])))
        return None
    
    @staticmethod
    def total_pvc(kconfig):
        config.load_kube_config(kconfig)
        # Create a Kubernetes API client
        api_instance = client.CoreV1Api()
        # Define the PVC status to exclude (e.g., "Bound")
        excluded_statuses = ["Bound"]
        # Initialize a counter for PVCs
        total_pvc = 0
        total_pvc_unbound = 0
        # List all PVCs in all namespaces
        namespaces = api_instance.list_namespace()
        for namespace in namespaces.items:
            pvc_list = api_instance.list_namespaced_persistent_volume_claim(namespace.metadata.name).items
            total_pvc += len(pvc_list)
            for pvc in pvc_list:
                # Check if the PVC is not in the excluded statuses
                if pvc.status.phase not in excluded_statuses:
                    total_pvc_unbound += 1
        print(f"Total number of PVCs is: {total_pvc}") 
        print(f"Total number of PVCs not in {', '.join(excluded_statuses)} status: {total_pvc_unbound}")  
        return None
        
    @staticmethod
    def total_pv(kconfig):
        config.load_kube_config(kconfig)
        # Create a Kubernetes API client
        api_instance = client.CoreV1Api()
        # Define the PV status to exclude (e.g., "Bound")
        excluded_statuses = ["Bound"]
        # Initialize a counter for PVs
        total_pv = 0
        # List all PVs in the cluster
        pv_list = api_instance.list_persistent_volume()

        filtered_pv = [pv for pv in pv_list.items if pv.status.phase not in excluded_statuses]
        print(f"Total number of pv is: {len(pv_list.items)}")
        print(f"Total number of pv not in {', '.join(excluded_statuses)} status: {len(filtered_pv)}")
        if filtered_pv: 
            print([i.metadata.name for i in filtered_pv])
        return None

    @staticmethod
    def total_resources(kconfig):
        # Load the Kubernetes configuration from the default location
        config.load_kube_config(kconfig)
        # Create a Kubernetes API client
        corev1 = client.CoreV1Api()
        """
        list_config_map_for_all_namespaces
        list_event_for_all_namespaces
        list_persistent_volume_claim_for_all_namespaces
        list_pod_for_all_namespaces
        list_resource_quota_for_all_namespaces
        list_secret_for_all_namespaces
        list_service_account_for_all_namespaces
        list_service_for_all_namespaces
        """

        appv1 = client.AppsV1Api()
        """
        list_daemon_set_for_all_namespaces
        list_deployment_for_all_namespaces
        list_replica_set_for_all_namespaces
        list_stateful_set_for_all_namespaces
        """

        netv1 = client.NetworkingV1Api()
        """
        list_ingress_for_all_namespaces
        list_network_policy_for_all_namespaces
        """

        stov1 = client.StorageV1Api()
        """
        list_storage_class
        list_csi_driver
        list_csi_node
        list_csi_storage_capacity_for_all_namespaces
        list_volume_attachment
        """

        autov1 = client.AutoscalingV1Api()
        """
        list_horizontal_pod_autoscaler_for_all_namespaces
        """

        batv1 = client.BatchV1Api()
        """
        list_cron_job_for_all_namespaces
        list_job_for_all_namespaces
        """
        # Resource counts
        deployments = len((appv1.list_deployment_for_all_namespaces()).items)
        services = len((corev1.list_service_for_all_namespaces()).items)
        ingresses = len((netv1.list_ingress_for_all_namespaces()).items)
        statefulset = len((appv1.list_stateful_set_for_all_namespaces()).items)
        pods = services = len((corev1.list_pod_for_all_namespaces()).items)
        daemonset = len((appv1.list_daemon_set_for_all_namespaces()).items)
        replicaset = len((appv1.list_replica_set_for_all_namespaces()).items)
        storageclass = len((stov1.list_storage_class()).items)
        csidriver = len((stov1.list_csi_driver()).items)
        csinode = len((stov1.list_csi_node()).items)
        cronjobs = len((batv1.list_cron_job_for_all_namespaces()).items)
        jobs = len((batv1.list_job_for_all_namespaces()).items)
        hpa = len((autov1.list_horizontal_pod_autoscaler_for_all_namespaces()).items)
        networkpolicy = len((netv1.list_network_policy_for_all_namespaces()).items)

        # Printing the results
        print(f"Deployments : {deployments}")
        print(f"Services : {services}")
        print(f"Ingresses : {ingresses}")
        print(f"Network Polices : {networkpolicy}")
        print(f"StatefulSets : {statefulset}")
        print(f"Pods : {pods}")
        print(f"DaemonSets : {daemonset}")
        print(f"ReplicaSets : {replicaset}")
        print(f"StorageClasses : {storageclass}")
        print(f"CSI Drivers : {csidriver}")
        print(f"CSI nodes : {csinode}")
        print(f"CronJobs : {cronjobs}")
        print(f"Jobs : {jobs}")
        print(f"HorizontalPodAutoscaler : {hpa}")

    @staticmethod
    def get_top_pods(kconfig):
        # Function to get top pods by CPU and Memory usage
        config.load_kube_config(kconfig)
        # Create a Kubernetes API client
        corev1 = client.CoreV1Api()

        allpods = corev1.list_pod_for_all_namespaces()
        allpods.items = [pod for pod in allpods.items if pod.spec.containers[0].resources.requests]
        cpupods = allpods.items.sort(key=lambda pod: pod.spec.containers[0].resources.requests['cpu'])
        #mempods = (allpods.items.sort(key=lambda pod: pod.spec.containers[0].resources.requests['memory']))
        mempods = allpods.items.sort(key=lambda pod: pod.spec.containers[0].resources.requests.get('memory',str(0)))
        print("after lambda")
        cpupods = cpupods.items[:5]
        mempods = mempods.items[:5]
        
        print("\nTop Pods 5 According to CPU usage:")
        for pod in cpupods:
            print(f"{pod.metadata.namespace}\t{pod.metadata.name}")

        print("\nTop Pods 5 According to MEM usage:")
        for pod in mempods:
            print(f"{pod.metadata.namespace}\t{pod.metadata.name}")
        return None


def main():
    parser = argparse.ArgumentParser(description='Checking k8s cluster platform health check')
    parser.add_argument('-c','--config',help='specify kubeconfig file path',type=str,default='~/.kube/config',required=True,dest='kconfig')
    args =parser.parse_args()

    try:
        print(Colors.OKBLUE +"\nCheck Health API Endpoint:"+Colors.ENDC)
        Helpers.endpoint_ch(args.kconfig)
        print(Colors.OKBLUE +"\nCheck Deployment:"+Colors.ENDC)
        Helpers.total_dep(args.kconfig)
        print(Colors.OKBLUE +"\nCheck Pod:"+Colors.ENDC)
        Helpers.total_abnormal_pod(args.kconfig)
        print(Colors.OKBLUE +"\nCheck Node:"+Colors.ENDC)
        Helpers.total_abnormal_node(args.kconfig)
        print(Colors.OKBLUE +"\nCheck Services:"+Colors.ENDC)
        Helpers.total_svc(args.kconfig)
        print(Colors.OKBLUE +"\nCheck Persistent Volumes and Claims:"+Colors.ENDC)
        Helpers.total_pvc(args.kconfig)
        Helpers.total_pv(args.kconfig)
        print(Colors.OKBLUE +"\nCheck Overall Cluster Resources:"+Colors.ENDC)
        Helpers.total_resources(args.kconfig)
        #Helpers.get_top_pods(args.kconfig)

    except Exception as err:
        print("Opps something went wrong")

if __name__ == "__main__":
    sys.exit(main())
