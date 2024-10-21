FROM anibali/pytorch:1.10.2-cuda11.3-ubuntu20.04
# use an older system (18.04) to avoid opencv incompatibility (issue#3524)

USER root

ENV DEBIAN_FRONTEND=noninteractive

RUN sed -i 's/htt[p|ps]:\/\/archive.ubuntu.com\/ubuntu\//mirror:\/\/mirrors.ubuntu.com\/mirrors.txt/g' /etc/apt/sources.list

RUN apt-get update && apt-get install -y \
	ca-certificates python3-dev ninja-build gcc g++ python3-opencv

# install detectron2
RUN pip install 'git+https://github.com/facebookresearch/detectron2'
# set FORCE_CUDA because during `docker build` cuda is not accessible
ENV FORCE_CUDA="1"
# This will by default build detectron2 for all common cuda architectures and take a lot more time,
# because inside `docker build`, there is no way to tell which architecture will be used.
ARG TORCH_CUDA_ARCH_LIST="Kepler;Kepler+Tesla;Maxwell;Maxwell+Tegra;Pascal;Volta;Turing"
ENV TORCH_CUDA_ARCH_LIST="${TORCH_CUDA_ARCH_LIST}"

# Set a fixed model cache directory.
WORKDIR /home/appuser/

ENV USE_GPU="true"

RUN curl --create-dirs -o ./models/model_final_cafdb1.pkl https://dl.fbaipublicfiles.com/detectron2/COCO-PanopticSegmentation/panoptic_fpn_R_101_3x/139514519/model_final_cafdb1.pkl

COPY requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

COPY classes.txt ./classes.txt
COPY models ./models
COPY *.py ./

EXPOSE 8000

CMD ["uvicorn", "--host", "0.0.0.0", "main:app", "--port", "8000"]

# run detectron2 under user "appuser":
# wget http://images.cocodataset.org/val2017/000000439715.jpg -O input.jpg
# python3 demo/demo.py  \
	#--config-file configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml \
	#--input input.jpg --output outputs/ \
	#--opts MODEL.WEIGHTS detectron2://COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/137849600/model_final_f10217.pkl