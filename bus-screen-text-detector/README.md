#BUS SCREEN TEXT DETECTOR
==========================

## Specs
------------

### Input

This microservice take a picture in input

### Output

The output of this microservice is a string with the bus number and the destination. (To be confirmed)

--------

## Data

The testing data are stored in the minIO bucket:
url: https://minio1.isc.heia-fr.ch:9113/buckets/pi-aimarket-visionaid/bus-screen-text-detector

### DVC start guide
- Install DVC: `brew install dvc`
- Init inside a git project: `dvc init`
- Commit the new files: `git add .` `git commit -m "init dvc"`
- Add the data directory to dvc: `dvc add data` This while create a data.dvc file, this file must be push on git, but don't forget to gitignore the data folder
- Configure dvc with the minio: `dvc remote add myminio -d s3://pi-aimarket-visionaid/photo-validator/`
- Then update the endpoint url: `dvc remote modify myminio endpointurl http://https://minio1.isc.heia-fr.ch:9013`
- Then configure the remote access key id: `dvc remote modify myminio access_key_id ***`
- Then configure the remote secret access key: `dvc remote modify myminio secret_access_key ***`
- Then push the data: `dvc push`


## Local use and development
### Setup a virtual env
- Create venv: `python -m venv venv`
- Activate venv: `source ./venv/bin/activate` (Mac, Linux)
- Activate venv: `venv\Scripts\activate.bat` (Windows)
- Install requirements: `pip install -r requirements.txt`

### Exit venv
`deactivate`