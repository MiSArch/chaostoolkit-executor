FROM python:3.13-slim AS build-venv

ARG DEBIAN_FRONTEND=noninteractive

RUN groupadd -g 1001 svc && useradd -r -u 1001 -g svc svc
RUN pip install pdm docker

COPY pyproject.toml pdm.lock /home/svc/
COPY misarch_chaostoolkit /home/svc/misarch_chaostoolkit

RUN export PATH="$PATH:/root/.local/bin" && \
    cd /home/svc && \
    pdm self update && \
    cd /home/svc/ && \
    pdm venv create python3.13 && \
    pdm use .venv && \
    pdm update --no-editable --no-self --dev --frozen-lockfile && \
    chown --recursive svc:svc /home/svc/.venv && \
    python -c "import misarch_chaostoolkit.chaostoolkit_docker" && \
    echo "from misarch_chaostoolkit.chaostoolkit_docker import *" > /home/svc/extension.py

FROM python:3.13-slim

COPY --from=build-venv --chown=svc:svc /home/svc/.venv/ /home/svc/.venv
COPY --from=build-venv --chown=svc:svc /home/svc/misarch_chaostoolkit /home/svc/misarch_chaostoolkit
COPY --from=build-venv --chown=svc:svc /home/svc/extension.py /home/svc/extension.py

WORKDIR /home/svc
USER root
ENV PATH="/home/svc/.venv/bin:$PATH"
ENV PYTHONPATH="/home/svc/:${PYTHONPATH}"

EXPOSE 8890

CMD ["python3", "-m", "misarch_chaostoolkit.webserver"]