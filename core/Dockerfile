ARG cuda="false"


### OS Deps
FROM nvidia/cuda:12.2.2-devel-ubuntu22.04 AS base
ARG DEBIAN_FRONTEND=noninteractive
RUN apt update -y

RUN apt install -y git curl
RUN apt install -y python3-pip python3.10-full


### Enable GPU
FROM base AS cuda-true
RUN CMAKE_ARGS="-DGGML_CUDA=on" python3.10 -m pip install --upgrade --force-reinstall --no-cache-dir python-doctr llama-cpp-python

FROM base AS cuda-false

FROM cuda-${cuda} AS after_cuda


### Python deps
WORKDIR /app/core
COPY . .
RUN python3.10 -m pip install -r requirements.txt

# llama-cpp
RUN apt install -y libsm6 libxext6

# konlpy
RUN apt install -y g++ openjdk-8-jdk curl

WORKDIR /app
CMD python3.10 core/src/run_server.py