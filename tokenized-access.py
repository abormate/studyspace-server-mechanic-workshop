# eks_auth.py
import boto3
import subprocess
import json
import base64
import tempfile
import os
from kubernetes import client
from kubernetes.client.rest import ApiException

# --- Configuration ---
# Replace with your EKS cluster name and AWS region
EKS_CLUSTER_NAME = "your-cluster-name"
AWS_REGION = "us-east-1"

def get_eks_token(cluster_name: str, region: str) -> str:
    """
    Generates a token for EKS authentication using 'aws eks get-token'.
    
    This is the standard and recommended way to get a temporary token based on
    your AWS IAM identity. It requires the AWS CLI to be installed and configured.

    Args:
        cluster_name: The name of the EKS cluster.
        region: The AWS region where the cluster is located.

    Returns:
        The authentication token string.
    
    Raises:
        RuntimeError: If the aws-cli command fails.
    """
    print("Getting EKS token...")
    try:
        command = [
            "aws", "eks", "get-token",
            "--cluster-name", cluster_name,
            "--region", region
        ]
        result = subprocess.run(
            command, capture_output=True, text=True, check=True, encoding='utf-8'
        )
        token_data = json.loads(result.stdout)
        print("Successfully retrieved EKS token.")
        return token_data["status"]["token"]
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError) as e:
        error_message = "Error getting EKS token"
        if isinstance(e, subprocess.CalledProcessError):
            error_message += f": {e.stderr}"
        elif isinstance(e, FileNotFoundError):
            error_message = "Error: 'aws' command not found. Is the AWS CLI installed and in your PATH?"
        else:
            error_message += f": {e}"
            
        print(error_message)
        raise RuntimeError("Failed to get EKS token.") from e

def get_eks_cluster_details(cluster_name: str, region: str) -> dict:
    """
    Retrieves EKS cluster details like endpoint and CA certificate using boto3.

    Args:
        cluster_name: The name of the EKS cluster.
        region: The AWS region of the cluster.

    Returns:
        A dictionary containing 'endpoint' and 'ca_cert'.
    """
    print(f"Fetching details for EKS cluster '{cluster_name}'...")
    try:
        eks_client = boto3.client("eks", region_name=region)
        response = eks_client.describe_cluster(name=cluster_name)
        cluster_info = response["cluster"]
        
        endpoint = cluster_info["endpoint"]
        ca_cert = cluster_info["certificateAuthority"]["data"]
        
        print("Successfully fetched cluster details.")
        return {"endpoint": endpoint, "ca_cert": ca_cert}
    except Exception as e:
        print(f"Error fetching cluster details: {e}")
        raise

def main():
    """
    Main function to authenticate with EKS and list pods.
    """
    if EKS_CLUSTER_NAME == "your-cluster-name":
        print("Please update EKS_CLUSTER_NAME and AWS_REGION at the top of the script.")
        return

    ca_cert_path = None
    try:
        # 1. Get EKS cluster details (API endpoint and CA cert)
        cluster_details = get_eks_cluster_details(EKS_CLUSTER_NAME, AWS_REGION)
        api_endpoint = cluster_details["endpoint"]
        ca_cert_data = cluster_details["ca_cert"]

        # 2. Get the authentication token from AWS STS via the AWS CLI
        token = get_eks_token(EKS_CLUSTER_NAME, AWS_REGION)

        # 3. Configure the Kubernetes client
        print("Configuring Kubernetes client...")
        
        # Create a temporary file for the CA certificate
        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix=".crt") as ca_cert_file:
            # The CA data is base64 encoded, so we must decode it first
            ca_cert_file.write(base64.b64decode(ca_cert_data).decode('utf-8'))
            ca_cert_path = ca_cert_file.name
        
        print(f"CA certificate written to temporary file: {ca_cert_path}")

        # Set up the configuration object for the Kubernetes client
        configuration = client.Configuration()
        configuration.host = api_endpoint
        configuration.ssl_ca_cert = ca_cert_path
        # The token needs to be passed in the Authorization header as a Bearer token
        configuration.api_key['authorization'] = "Bearer " + token
        
        # Create the API client
        api_client = client.ApiClient(configuration)
        
        # 4. Use the client to interact with the cluster
        print("\nSuccessfully authenticated. Making an API call to the cluster...")
        core_v1_api = client.CoreV1Api(api_client)
        
        print("Listing pods in all namespaces:")
        pod_list = core_v1_api.list_pod_for_all_namespaces(watch=False)
        
        if not pod_list.items:
            print("No pods found in the cluster.")
        else:
            for pod in pod_list.items:
                print(f"- Namespace: {pod.metadata.namespace}, Pod: {pod.metadata.name}, Status: {pod.status.phase}")

    except ApiException as e:
        print(f"\nKubernetes API Error: {e.status}")
        print(f"Reason: {e.reason}")
        # The body often contains a more detailed message from the server
        if e.body:
            body = json.loads(e.body)
            print(f"Message: {body.get('message')}")
        print("\nThis might be an authorization issue. Please ensure:")
        print("1. Your AWS IAM identity has permissions to access the EKS cluster.")
        print("2. The IAM identity is correctly mapped in the 'aws-auth' ConfigMap in the 'kube-system' namespace of your cluster.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
    finally:
        # 5. Clean up the temporary CA cert file
        if ca_cert_path and os.path.exists(ca_cert_path):
            print(f"\nCleaning up temporary file: {ca_cert_path}")
            os.remove(ca_cert_path)

if __name__ == "__main__":
    main()
