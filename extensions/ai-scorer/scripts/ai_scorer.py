import clip
import json
import torch

import modules.processing as processing
import modules.scripts as scripts

from pathlib import Path


state_name = "sac+logos+ava1-l14-linearMSE.pth"
if not Path(state_name).exists():
    url = f"https://github.com/christophschuhmann/improved-aesthetic-predictor/blob/main/{state_name}?raw=true"
    import requests
    r = requests.get(url)
    with open(state_name, "wb") as f:
        f.write(r.content)

device = "cuda" if torch.cuda.is_available() else "cpu"
# load the model you trained previously or the model available in this repo
pt_state = torch.load(state_name, map_location=torch.device(device=device))
clip_model, clip_preprocess = clip.load("ViT-L/14", device=device)


class AestheticPredictor(torch.nn.Module):
    def __init__(self, input_size):
        super().__init__()

        self.input_size = input_size
        self.layers = torch.nn.Sequential(
            torch.nn.Linear(self.input_size, 1024),
            torch.nn.Dropout(0.2),
            torch.nn.Linear(1024, 128),
            torch.nn.Dropout(0.2),
            torch.nn.Linear(128, 64),
            torch.nn.Dropout(0.1),
            torch.nn.Linear(64, 16),
            torch.nn.Linear(16, 1)
        )

    def forward(self, x):
        return self.layers(x)


# CLIP embedding dim is 768 for CLIP ViT L 14
predictor = AestheticPredictor(768)
predictor.load_state_dict(pt_state)
predictor.to(device)
predictor.eval()


def get_image_features(image, device=device, model=clip_model, preprocess=clip_preprocess):
    image = preprocess(image).unsqueeze(0).to(device)
    with torch.no_grad():
        image_features = model.encode_image(image)
        # l2 normalize
        image_features /= image_features.norm(dim=-1, keepdim=True)
    image_features = image_features.cpu().detach().numpy()
    return image_features


def get_score(image):
    image_features = get_image_features(image)
    score = predictor(torch.from_numpy(image_features).to(device).float())
    return score.item()


def format_image_data(image_data, index):
    info = image_data.info['parameters'].split(',')
    seed = [x for x in info if 'Seed' in x][0].split(':')[1].strip()
    # the seed here is like the file's name. since the image hasn't been saved we
    # don't know for sure the name of the file, but we do know its seed to use as the ID
    return {'score': round(get_score(image_data), 1), f'seed-{index}': seed}


class Script(scripts.Script):
    def title(self):
        return "AI Scorer"

    def show(self, is_img2img):
        return not is_img2img

    def ui(self, is_img2img):
        return []

    def run(self, p, *args):
        processed = processing.process_images(p)

        if (processed is not None and len(processed.images) > 0):
            images = processed.images
            json_data = json.dumps([format_image_data(image, index) for index, image in enumerate(images)])

        # Update the HTML Info string that will be appended to the UI.  This allows us
        # to grab it from the DOM via JavaScript to append the scores to the image previews
        # (i.e. gallery items).
        processed.info = f"{processed.info};{json_data}"

        return processed
