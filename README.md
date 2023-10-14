# avatar

Uses Google Colab & Jupyter notebook to create an AI Avatar project using Dreambooth and Stable Diffusion.

## Prerequisites

- 4-5 GB/s of free space on Google Drive
- [Copy Colab file to your Google Drive](https://colab.research.google.com/github/buildspace/diffusers/blob/main/examples/dreambooth/DreamBooth_Stable_Diffusion.ipynb?utm_source=buildspace.so&utm_medium=buildspace_project#scrollTo=XU7NuMAA2drw)
- [Register or Login at Huggingface.co](https://huggingface.co/login)

## Procedures

- Step 0: Connect to a virtual machine and Google Drive
- Step 1: Install Requirements
- Step 2:[Create Hugginface.co access token](https://huggingface.co/settings/tokens)
- Step 3: Install xformers from precompiled wheels, use the following if you have issues (ETA:~40mins): `pip install git+https://github.com/facebookresearch/xformers@4c06c79#egg=xformers`
- Step 4: Configure your model //TODO
- Step 5: Configure the training resources
- Step 5.5 - Tell Stable Diffusion what you're turning for
- Step 6: Upload your images
- Step 7.1: Change `max_train_steps` (MAX: 2000)
- Step 7.2: Update `save_sample_prompt`, more than just "Photo of xyz person", ex: `Photo of NITSUAH MAN, highly detailed, 8k, uhd, studio lighting, beautiful`
- Step 7.2 - Set weights (run without changes first time)
- Step 7.3 - Generate test images!
- Step 8 - Convert weights to CKPT
- Step 9 - Inference
- Step 10 - Generate images!
- Step 11 - Upload your custom trained model to HuggingFace
