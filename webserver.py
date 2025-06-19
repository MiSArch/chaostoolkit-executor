import os
import time
import subprocess
from threading import Thread, Event
import requests
from flask import Flask, request

app = Flask(__name__)

experiment_threads = {}
stop_events = {}

def run_experiment(test_uuid, test_version):
  stop_event = stop_events[f"{test_uuid}:{test_version}"]
  triggered = wait_for_trigger(test_uuid, test_version, stop_event)
  if not triggered:
    print(f"Trigger has not been set for {test_uuid}, aborting experiment.")
    return
  if not stop_event.is_set():
    process = subprocess.Popen(["chaos", "run", "experiment.json"])
    while process.poll() is None:
      if stop_event.is_set():
        process.kill()
        process.terminate()
        return
      time.sleep(0.1)

def wait_for_trigger(test_uuid, test_version, stop_event, check_interval=0.1, max_retries=6000):
  host = os.getenv("EXPERIMENT_EXECUTOR_URL")
  try:
    requests.post(f"{host}/trigger/{test_uuid}/{test_version}?client=chaostoolkit")
  except requests.RequestException as e:
    print(f"Error registering trigger: {e}")

  retries = 0
  while not stop_event.is_set() and retries < max_retries:
    try:
      response = requests.get(f"{host}/trigger/{test_uuid}/{test_version}")
      if response.status_code == 200 and response.text.strip().lower() == "true":
        return True
    except requests.RequestException as e:
      print(f"Error checking HTTP trigger: {e}")
    time.sleep(check_interval)
    retries += 1
  return False

@app.route('/start-experiment', methods=['POST'])
def start_experiment():
  test_uuid = request.args.get("testUUID")
  test_version = request.args.get("testVersion")
  test_id = f"{test_uuid}:{test_version}"
  with open("experiment.json", "w") as file:
    file.write(request.data.decode("utf-8"))

  stop_event = Event()
  stop_events[test_id] = stop_event
  thread = Thread(target=run_experiment, args=(test_uuid, test_version))
  experiment_threads[test_id] = thread
  thread.start()
  return {"status": "Experiment started"}, 200

@app.route('/stop-experiment', methods=['POST'])
def stop_experiment():
  test_uuid = request.args.get("testUUID")
  test_version = request.args.get("testVersion")
  test_id = f"{test_uuid}:{test_version}"
  if test_id in stop_events:
    stop_events[test_id].set()
    experiment_threads[test_id].join()
    del stop_events[test_id]
    del experiment_threads[test_id]
    return {"status": "Experiment stopped"}, 200
  else:
    return {"error": "Experiment not found"}, 404

if __name__ == "__main__":
  port = int(os.environ.get("LISTENER_PORT", 8890))
  app.run(host="0.0.0.0", port=port)