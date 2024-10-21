import sys
import json
import shutil
import random
import os
import tqdm
import re
from minio import Minio
from pathlib import Path


def import_json():
    with open(Path(sys.argv[1])) as json_file:
        labels = json.load(json_file)

        return labels  # list(filter(lambda label: label["document-type"] == "invoice", labels))


def label_to_gt(label):
    gt = {"gt_parse": {}}

    if "busDestination" in label:
        if isinstance(label['busDestination'], str):
            gt['gt_parse']['busDestination'] = [label['busDestination']]
        else:
            gt['gt_parse']['busDestination'] = label['busDestination']['text']
    # else:
    #    gt['gt_parse']['busDestination'] = "<-1/>"

    if "busNumber" in label:
        gt['gt_parse']['busNumber'] = label['busNumber']
    # else:
    #    gt['gt_parse']['busNumber'] = "<-1/>"

    if len(gt["gt_parse"]) == 0:
        gt = None

    return gt


def parse_object_name(object_name):
    regex = re.search(r"s3:\/\/(.*?)\/(.*\/(.*))", object_name)
    bucket = regex.group(1)
    object_name = regex.group(2)
    file_name = regex.group(3)
    return bucket, object_name, file_name


if __name__ == "__main__":
    random.seed(1)
    client = Minio("minio1.isc.heia-fr.ch:9013", "JeWqNCj4u8sBdUxc", "wak49u6HT7sDMbVthfFltx4yk23ODA28")

    labels = import_json()

    path = Path(sys.argv[2])
    folders = [path / "train", path / "validation", path / "test"]

    for i, label in tqdm.tqdm(enumerate(sorted(labels, key=lambda k: random.random())), total=len(labels)):

        percent = i / len(labels)
        folder = ""

        if percent <= 0.8:
            folder = folders[0]
        elif percent <= 0.9:
            folder = folders[1]
        else:
            folder = folders[2]

        gt = label_to_gt(label)

        if gt is not None:
            bucket, object_name, file_name = parse_object_name(label["image"])
            image = client.fget_object(bucket, object_name, folder / file_name)
            gt_parsed = json.dumps(gt, ensure_ascii=False).replace('"', '\\"')

            with open(f"{folder}/metadata.jsonl", "a") as metafile:
                metafile.write(f'{{"file_name": "{file_name}", "ground_truth":"{gt_parsed}"}}\n')
