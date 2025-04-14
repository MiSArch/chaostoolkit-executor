import time
import docker
import os
import requests
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

def wait_for_trigger(url, check_interval=0.1):
    while True:
        try:
            uuid = os.environ["TEST_UUID"]
            url = url.replace("{UUID}", uuid)
            response = requests.get(url)
            if response.status_code == 200 and response.text.strip().lower() == "true":
                break
        except requests.RequestException as e:
            print(f"Error checking HTTP trigger: {e}")
        time.sleep(check_interval)