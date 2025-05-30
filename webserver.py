import os
import time
from subprocess import run
from threading import Thread

import requests
from flask import Flask, request

app = Flask(__name__)

def run_experiment(url):
  print("waiting for trigger")
  wait_for_trigger(url)
  run(["chaos", "run", "experiment.yaml"])


def wait_for_trigger(test_uuid, check_interval=0.1):
  while True:
    host = os.getenv("EXPERIMENT_EXECUTOR_URL")
    try:
      response = requests.get(f"{host}/trigger/{test_uuid}")
      if response.status_code == 200 and response.text.strip().lower() == "true":
        break
    except requests.RequestException as e:
      print(f"Error checking HTTP trigger: {e}")
    time.sleep(check_interval)

@app.route('/start-experiment', methods=['POST'])
def start_experiment():
  test_uuid = request.args.get("testUUID")
  with open("experiment.yaml", "w") as file:
    file.write(request.data.decode("utf-8"))
    Thread(target=run_experiment, args=(test_uuid,)).start()

  return {"status": "Experiment started"}, 200

if __name__ == "__main__":
  port = int(os.environ.get("LISTENER_PORT", 8890))
  app.run(host="0.0.0.0", port=port)