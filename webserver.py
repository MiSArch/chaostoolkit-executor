import os
import time
import subprocess
from threading import Thread, Event
import requests
from flask import Flask, request

app = Flask(__name__)

experiment_threads = {}
stop_events = {}

def run_experiment(test_uuid, url):
  stop_event = stop_events[test_uuid]
  wait_for_trigger(test_uuid, url, stop_event)
  if not stop_event.is_set():
    process = subprocess.Popen(["chaos", "run", "experiment.yaml"])
    while process.poll() is None:
      if stop_event.is_set():
        process.kill()
        process.terminate()
        return
      time.sleep(0.1)

def wait_for_trigger(test_uuid, url, stop_event, check_interval=0.1):
  while not stop_event.is_set():
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

  stop_event = Event()
  stop_events[test_uuid] = stop_event
  thread = Thread(target=run_experiment, args=(test_uuid, request.url))
  experiment_threads[test_uuid] = thread
  thread.start()
  return {"status": "Experiment started"}, 200

@app.route('/stop-experiment', methods=['POST'])
def stop_experiment():
  test_uuid = request.args.get("testUUID")
  if test_uuid in stop_events:
    stop_events[test_uuid].set()
    experiment_threads[test_uuid].join()
    del stop_events[test_uuid]
    del experiment_threads[test_uuid]
    return {"status": "Experiment stopped"}, 200
  else:
    return {"error": "Experiment not found"}, 404

if __name__ == "__main__":
  port = int(os.environ.get("LISTENER_PORT", 8890))
  app.run(host="0.0.0.0", port=port)