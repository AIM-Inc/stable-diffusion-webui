#!/bin/bash

# Run the web ui
python3 webui.py --precision full --no-half --use-cpu Interrogate GFPGAN CodeFormer ESRGAN SCUNet
