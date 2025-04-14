FROM chaostoolkit/chaostoolkit:basic

WORKDIR /app
ENV PYTHONPATH=/app

RUN pip install docker requests
COPY docker_helpers.py ./docker_helpers.py
RUN python -c "import docker_helpers"
RUN echo "from docker_helpers import *" > extension.py

USER root

CMD ["run", "experiment.yaml"]