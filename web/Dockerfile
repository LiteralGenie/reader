# OS Deps
FROM nvidia/cuda:12.2.2-devel-ubuntu22.04 AS base
ARG DEBIAN_FRONTEND=noninteractive
RUN apt update -y

RUN apt install git curl -y

RUN curl -fsSL https://deb.nodesource.com/setup_current.x -o nodesource_setup.sh
RUN bash nodesource_setup.sh
RUN apt install -y nodejs


# Node deps
WORKDIR /app/web
COPY . .
RUN npm install

RUN npm run build
CMD HOST=0.0.0.0 PORT=3030 BODY_SIZE_LIMIT=500M node build
