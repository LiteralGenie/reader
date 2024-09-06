# About

A Korean comic viewer that provides automatic dictionary lookups / translations.

Demo: https://reader.velchees.dev/

Features:

-   Text is OCR'd using [docTR](https://github.com/mindee/doctr) (custom trained using a [synthetic dataset](https://github.com/LiteralGenie/comic_ocr)).
-   Dictionary data is gathered from [Wiktionary](https://kaikki.org/dictionary/Korean/) and the [National Institute of Korean Language's dictionary](https://krdict.korean.go.kr/eng/mainAction).
-   Machine translations are generated via an LLM. LLMs are also used as a context-aware way of scoring dictionary definitions.

<blockquote>
    <details>
        <summary>
        Screenshots
        </summary>

<img width="40%" src="https://github.com/LiteralGenie/reader/blob/master/assets/series_1.png">

<img width="40%" src="https://github.com/LiteralGenie/reader/blob/master/assets/chapters_1.png">

<img width="40%" src="https://github.com/LiteralGenie/reader/blob/master/assets/dict_1.png">

<img width="40%" src="https://github.com/LiteralGenie/reader/blob/master/assets/dict_2.png">

<img width="40%" src="https://github.com/LiteralGenie/reader/blob/master/assets/edit_chap_1.png">

<img width="40%" src="https://github.com/LiteralGenie/reader/blob/master/assets/edit_series_1.png">

<img width="40%" src="https://github.com/LiteralGenie/reader/blob/master/assets/search_1.png">

</details>

</blockquote>

# Setup

The instructions below assume you're using Ubuntu. Other OSes are untested but the only differences should come from how the dependencies are installed.

Installing via Docker is recommended as it prevents access to anything outside of the app folder. (This should also be the case without Docker, but mistakes happen.)

There is no login system, so if you plan to make the app accessible from the internet, it's recommended that you either

-   make it only accessible from a [WireGuard](https://www.wireguard.com/) connection
-   or add a login system via [NGINX's Basic Auth module](https://docs.nginx.com/nginx/admin-guide/security-controls/configuring-http-basic-authentication/)

## Docker (recommended)

Install the following:

-   [Docker](https://docs.docker.com/engine/install/)
-   [git](https://git-scm.com/downloads)
-   [Python](https://www.python.org/downloads/)

(optional) If you have a NVIDIA GPU and want to use it for inference, run:

```bash
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | tee /etc/apt/sources.list.d/nvidia-docker.list

apt-get update && apt-get install -y nvidia-container-toolkit
systemctl restart docker
```

Clone the repo:

```bash
git clone https://github.com/LiteralGenie/reader/
cd reader
```

Create a config file by copying the default template.  
See the [Config section](#config) for details. Note that GPU-acceleration is disabled by default.

Downloading custom weights for `det_weights` and `reco_weights` from [here](https://github.com/LiteralGenie/comic_ocr/releases) is also heavily recommended.

```bash
cp config_example.toml config.toml
```

Build the dictionary

```bash
cd ./core
python3 -m venv venv
. ./venv/bin/activate
pip install -r requirements.txt
python src/scripts/build_dictionary.py
cd ..
```

Build and run the Docker image

```bash
# Build with GPU
docker compose build --build-arg cuda="true"

# Or build without GPU
docker compose build

# Run
docker compose up -d
```

The app should then be running at http://localhost:9494

## Without Docker

Install the following:

-   [Docker](https://docs.docker.com/engine/install/)
-   [Python](https://www.python.org/downloads/)
-   [Node.js](https://github.com/nodesource/distributions)
-   [CUDA](https://gist.github.com/denguir/b21aa66ae7fb1089655dd9de8351a202) - optional and requries a NVIDIA GPU, but it's a huge speed-up

Clone the repo:

```bash
git clone git@github.com:LiteralGenie/reader.git
cd reader
```

Create a config file by copying the default template. Set `api_host = localhost` in the config.

Downloading custom weights for `det_weights` and `reco_weights` from [here](https://github.com/LiteralGenie/comic_ocr/releases) is also heavily recommended.

See the [Config section](#config) for more details. Note that GPU-acceleration is disabled by default.

```bash
cp config_example.toml config.toml
```

Install dependencies:

```bash
cd ./core
python3 -m venv venv
. ./venv/bin/activate
pip install -r requirements.txt

cd ../web
npm install

cd ..
```

Build the dictionary

```bash
cd ./core
. ./venv/bin/activate
python src/scripts/build_dictionary.py
cd ..
```

(optional) If you plan to enable GPU-acceleration (which requires a NVIDIA GPU), you'll also need to recompile certain dependencies:

```
CMAKE_ARGS="-DGGML_CUDA=on" pip install --upgrade --force-reinstall --no-cache-dir python-doctr llama-cpp-python
```

And finally launch the API and web servers. Each needs to be launched in a separate terminal (or [screen](https://www.gnu.org/software/screen/manual/screen.html))

```bash
cd core
. ./venv/bin/activate
python src/run_server.py
```

```bash
cd web
npm run build
HOST=0.0.0.0 PORT=3030 BODY_SIZE_LIMIT=500M node build
```

# Config

Some notable config options / defaults are...

-   Enable GPU-acceleration for the OCR step by setting `use_gpu_for_ocr = true`
-   Enable GPU-acceleration for machine translations / definition sorting by setting `llm_num_gpu_layers` to a positive number.
-   Definition sorting is also disabled by default (because it's super slow on CPU) but can be enabled by setting `use_llm_for_definition_sort = true`
-   Custom weights for the OCR models can be downloaded from https://github.com/LiteralGenie/comic_ocr/releases and enabled by modifying `det_weights` and `reco_weights`.
-   If using Docker, set `api_host = core` (the default). Otherwise set `api_host = localhost`.

If using Docker, do **NOT** modify the `root_image_folder` option. Also, the paths specified in `det_weights` and `reco_weights` (if any) should point to somewhere in the data folder.

For example:

```toml
# Path to model weights (*.pt). Leave blank ("") to use default weights (not recommended)
det_weights = "data/models/db_resnet50.pt"
reco_weights = "data/models/parseq.pt"
```

This is because only the data folder is mounted to the Docker container, any other paths will not be visible to the container.

# Usage

Series and chapters can be added through the web gui (via file upload or URL), but for bulk imports, copying the files to the `root_image_folder` specified in `config.toml` (default `reader/data/series`) may be faster.

# Troubleshooting

It's a known issue that things will occasionally get stuck (like chapter imports). Restarting the backend should fix this:

```bash
# If using Docker, find the container name
docker container ls
# And replace reader-core-1 in the below with it
docker container restart reader-core-1

###

# If not using Docker, kill the process (eg ctrl+c) and rerun the launch command
python src/run_server.py
```

# Limitations

-   New OCR blocks cannot be added through the web GUI at the moment.
    -   If you really need it, you'll have you edit the `_reader_data.sqlite` database in the folder for that chapter.
    -   As a workaround you could just edit a nearby block to include the missing text.
    -   The boxes tend to be correct 99% of the time so this has been low-priority.
-   Only the series title / cover and the chapter title are currently displayed / saved. I do not plan to support other metadata like genre tags and series descriptions.
