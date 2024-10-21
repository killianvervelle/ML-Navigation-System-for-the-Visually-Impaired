import requests
import os
import sys
from datetime import date


BASE_URL = os.getenv("LABEL_STUDIO_URL", "https://visionaid-labelstudio.kube.isc.heia-fr.ch")
PROJECT_NB = os.getenv("LABEL_STUDIO_PROJECT_NB", "2")
TOKEN = os.getenv("LABEL_STUDIO_TOKEN")
EXPORT_TYPE = os.getenv("LABEL_STUDIO_EXPORT_TYPE", "JSON_MIN")

req = requests.get(
    f"{BASE_URL}/api/projects/{PROJECT_NB}/export?exportType={EXPORT_TYPE}",
    headers={
        'Authorization': f"Token {TOKEN}"
    }
)

with open(f"{sys.argv[1]}/labels.json", "wb") as file:
    file.write(req.content)