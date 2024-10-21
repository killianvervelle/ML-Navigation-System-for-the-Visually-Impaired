import pandas as pd
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
import os
from pathlib import Path
from pydantic import BaseModel


class Detetron:
    def __init__(self):
        self.thresh_value = 0.5
        self.configuration()

    def configuration(self, thresh_value=0.5):
        self.thresh_value = thresh_value
        # Create config
        cfg = get_cfg()
        cfg.MODEL.DEVICE= "cuda" if os.getenv('USE_GPU') == "true" else "cpu"
        cfg.merge_from_file("./models/faster_rcnn_R_101_FPN_3x.yaml")
        cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = self.thresh_value  # set threshold for this model
        model_path = Path("./models/model_final_cafdb1.pkl")
        if model_path.is_file():
            cfg.MODEL.WEIGHTS = str(model_path)
        else:
            cfg.MODEL.WEIGHTS = "detectron2://COCO-Detection/faster_rcnn_R_101_FPN_3x/139514519/model_final_cafdb1.pkl"
        # Create predictor
        self.predictor = DefaultPredictor(cfg)
        # Make prediction

    
    def predict(self, image, thresh_value):
        if self.thresh_value != thresh_value:
            self.configuration(thresh_value)

        outputs = self.predictor(image)
        height, width, _ = image.shape
        return self.get_output(outputs, width, height)

    def get_output(self, outputs, image_width, image_height):
        test = outputs["instances"].to("cpu")
        test_scores = test.scores.tolist()
        bind_boxes_x_y = test.pred_boxes.tensor.cpu().numpy()
        pred_classes = test.pred_classes.tolist()
        classes = pd.read_csv("classes.txt", sep=":").rename(columns={"{0": "class_number", " u'__background__',": "class_name"})
        classes['class_name'] = classes['class_name'].str[3:].str[:-2]
        classes['class_number'] = classes['class_number'] - 1
        pred_classes_list = list()
        for i in pred_classes:
            pred_classes_list.append(classes.iloc[i, 1])
    
        classes_scores = []
        for pred_class, test_score, bind_box in zip(pred_classes_list, test_scores, bind_boxes_x_y):
            classes_scores.append({
                "class": pred_class,
                "score": float(test_score),
                "bbox": {
                    "x1": float(bind_box[0]) / image_width,
                    "y1": float(bind_box[1]) / image_height,
                    "x2": float(bind_box[2]) / image_width,
                    "y2": float(bind_box[3]) / image_height
                }
            })
            
        return classes_scores
