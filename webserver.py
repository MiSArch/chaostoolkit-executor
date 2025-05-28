import os
from subprocess import run
from threading import Thread

from flask import Flask, request

app = Flask(__name__)

def run_experiment():
  run(["chaos", "run", "experiment.yaml"])

@app.route('/start-experiment', methods=['POST'])
def start_experiment():
  test_uuid = request.args.get("testUUID")
  experiment = request.data.decode("utf-8")

  experiment_data = experiment.replace("{UUID}", test_uuid)

  with open("experiment.yaml", "w") as file:
    file.write(experiment_data)

    Thread(target=run_experiment).start()

    return {"status": "Experiment started"}, 200

if __name__ == "__main__":
  port = int(os.environ.get("LISTENER_PORT", 8890))
  app.run(host="0.0.0.0", port=port)