import time
import docker
from typing import List

def are_containers_running(names: List[str]) -> bool:
    client = docker.from_env()
    try:
        for name in names:
            container = client.containers.get(name)
            if container.status != "running":
                return False
        return True
    except docker.errors.NotFound:
        return False

def kill_containers(names: List[str]):
    client = docker.from_env()
    for name in names:
        try:
            container = client.containers.get(name)
            container.kill()
        except docker.errors.NotFound:
            print(f"Container {name} not found.")

def start_containers(names: List[str]):
    client = docker.from_env()
    for name in names:
        try:
            container = client.containers.get(name)
            container.start()
        except docker.errors.NotFound:
            print(f"Container {name} not found.")

def wait_for_trigger(env_var_name, check_interval=0.1):
    """
    Waits for an environment variable to be set to proceed.

    :param env_var_name: Name of the environment variable to check.
    :param check_interval: Time in seconds to wait between checks.
    """
    while not os.getenv(env_var_name):
        time.sleep(check_interval)