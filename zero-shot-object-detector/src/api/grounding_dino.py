from groundingdino.util.inference import load_model, predict
import groundingdino.datasets.transforms as T

class ObjectDetector:
    BOX_TRESHOLD = 0.35
    TEXT_TRESHOLD = 0.25

    def __init__(self):
        self._load_model()

    def _load_model(self):
        self.model = load_model("config/GroundingDINO_SwinB_cfg.py", "weights/groundingdino_swinb_cogcoor.pth")

    def _transform_image(self, image):
        transform = T.Compose(
            [
                T.RandomResize([800], max_size=1333),
                T.ToTensor(),
                T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
            ]
        )

        image_transformed, _ = transform(image, None)
        return image_transformed

    def predict(self, image, prompt):
        boxes, logits, phrases = predict(
            model=self.model,
            image=self._transform_image(image),
            caption=prompt,
            box_threshold=self.BOX_TRESHOLD,
            text_threshold=self.TEXT_TRESHOLD
        )

        if len(boxes) > 0:
            boxes_np = boxes.numpy().tolist()[0]
            cx = boxes_np[0]
            cy = boxes_np[1]
            w = boxes_np[2]
            h = boxes_np[3]
            return {
                'item': phrases[0],
                'position': {
                    'x1': cx - (w / 2),
                    'y1': cy - (h / 2),
                    'x2': cx + (w / 2),
                    'y2': cy + (h / 2)
                }
            }
        return {}