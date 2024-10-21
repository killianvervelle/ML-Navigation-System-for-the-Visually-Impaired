# photo-validator

This microservice take a picture in input. The output of this microservice is the input picture and a boolean. True if the picture is usable (no blur) or false if the picture is not usable (blur)


# Prerequisites
* Python 3


## Install Python dependencies

Using virtualenv is recommended if you do not use the devcontainer.

### Windows
```shell
python -m venv venv
venv\Scripts\activate.bat
pip install -r src/requirements.txt
```
### Linux / MacOS
```shell
python -m venv venv
source venv/bin/activate
pip install -r src/requirements.txt
```


# Run
## Locally

```shell
cd src
uvicorn main:app
```
## With Docker
```shell
docker build -t photo-validator .
docker run --rm -d --name photo-validator -p 8000:8000 photo-validator
```
