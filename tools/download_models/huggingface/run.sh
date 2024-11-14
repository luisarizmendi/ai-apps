#! /bin/bash

hf_model_url=${1:="facebook/detr-resnet-101"}
hf_token=${HF_TOKEN:="None"}

echo "Downloading PIP requirements"
python3 -m pip install -r requirements.txt

echo "Downloading $hf_model_url"
python download_huggingface.py --model $hf_model_url --token $hf_token
