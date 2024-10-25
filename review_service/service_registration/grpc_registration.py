import socket
import grpc
import os
from service_discovery_pb2 import ServiceInfo
from service_discovery_pb2_grpc import ServiceDiscoveryStub

# Load environment variables
SERVICE_DISCOVERY_HOST = os.getenv('SERVICE_DISCOVERY_HOST', 'localhost:50051')
SERVICE_TYPE = os.getenv('SERVICE_TYPE', 'django_service')  # Default service name
SERVICE_IP = socket.gethostbyname(socket.gethostname())  # This should be dynamically set

def register_service():
    # Connect to the service discovery server
    with grpc.insecure_channel(SERVICE_DISCOVERY_HOST) as channel:
        stub = ServiceDiscoveryStub(channel)
        service_info = ServiceInfo(service_name=SERVICE_TYPE, ip_address=SERVICE_IP)

        try:
            # Call the RegisterService method
            response = stub.RegisterService(service_info)
            if response.success:
                print(f"Service registered successfully: {response.message}")
            else:
                print(f"Failed to register service: {response.message}")
        except grpc.RpcError as e:
            print(f"gRPC error: {e.details()}")

if __name__ == '__main__':
    if SERVICE_IP:
        register_service()
    else:
        print("Service IP is not set. Registration failed.")
