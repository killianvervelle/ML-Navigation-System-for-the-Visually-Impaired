# Object Detector

## Getting started

Few steps to follow before getting started:

```cd ./api_rest 
  python3.9 -m venv venv
  source ./venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt
  pip install 'git+https://github.com/facebookresearch/detectron2.git'
  uvicorn main:app --reload
```

## Introduction
The goal of Detectron is to provide a high-quality, high-performance codebase for object detection research. It is designed to be flexible in order to support rapid implementation and evaluation of novel research. For our app, we chose to use the RCNN algorithm named COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x, which is a pretrained model on the COCO dataset. We configured the object detection model using a YAML file, defined a threshold score and loaded the pretrained weights as our starting checkpoint. FiftyOne supports loading annotations for the detection task, including bounding boxes and segmentations. The table of classes can be found inside the classes.txt
