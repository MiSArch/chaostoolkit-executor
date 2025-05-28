FROM python:3.13-slim AS build-venv

ARG DEBIAN_FRONTEND=noninteractive
ARG CTK_VERSION

RUN groupadd -g 1001 svc && useradd -r -u 1001 -g svc svc
RUN pip install pdm docker

COPY pyproject.toml pdm.lock webserver.py experiment.yaml chaostoolkit_docker.py /home/svc/

RUN export PATH="$PATH:/root/.local/bin" && \
    pdm self update && \
    cd /home/svc/ && \
    pdm venv create python3.13 && \
    pdm use .venv && \
    pdm update --no-editable --no-self --dev --frozen-lockfile -G extensions && \
    chown --recursive svc:svc /home/svc/.venv && \
    python -c "import chaostoolkit_docker" && \
    echo "from chaostoolkit_docker import *" >  /home/svc/extension.py

FROM python:3.13-slim

RUN groupadd -g 1001 svc && \
    useradd -m -u 1001 -g svc svc

COPY --from=build-venv --chown=svc:svc /home/svc/.venv/ /home/svc/.venv
COPY --from=build-venv --chown=svc:svc /home/svc/webserver.py /home/svc/webserver.py
COPY --from=build-venv --chown=svc:svc /home/svc/experiment.yaml /home/svc/experiment.yaml
COPY --from=build-venv --chown=svc:svc /home/svc/extension.py /home/svc/extension.py
COPY --from=build-venv --chown=svc:svc /home/svc/chaostoolkit_docker.py /home/svc/chaostoolkit_docker.py

ENV PATH="/home/svc/.venv/bin:$PATH"
ENV PYTHONPATH="/home/svc/:${PYTHONPATH}"

WORKDIR /home/svc
USER root

EXPOSE 4999

CMD ["python3", "webserver.py"]