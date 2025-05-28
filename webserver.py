import os
from subprocess import run
from flask import Flask

app = Flask(__name__)

@app.route('/start-experiment', methods=['POST'])
def start_experiment():
  experiment_file = "experiment.yaml"
  result = run(["chaos", "run", experiment_file])
  return {"status": "Experiment started", "result": result.returncode}, 200

if __name__ == "__main__":
  port = int(os.environ.get("LISTENER_PORT", 4999))
  app.run(host="0.0.0.0", port=port)