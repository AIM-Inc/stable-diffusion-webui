import argparse
import os

import modules.paths as paths

sd_model_file = os.path.join(paths.script_path, "model.ckpt")

default_sd_model_file = sd_model_file

parser = argparse.ArgumentParser()

parser.add_argument(
    "--config",
    type=str,
    default=os.path.join(paths.sd_path, "configs/stable-diffusion/v1-inference.yaml"),
    help="path to config which constructs model",
)
parser.add_argument(
    "--ckpt",
    type=str,
    default=sd_model_file,
    help="path to checkpoint of stable diffusion model; if specified, this checkpoint will be added to the list of checkpoints and loaded",
)
parser.add_argument(
    "--ckpt-dir",
    type=str,
    default=None,
    help="Path to directory with stable diffusion checkpoints",
)
parser.add_argument(
    "--gfpgan-dir",
    type=str,
    help="GFPGAN directory",
    default=("./src/gfpgan" if os.path.exists("./src/gfpgan") else "./GFPGAN"),
)
parser.add_argument(
    "--gfpgan-model", type=str, help="GFPGAN model file name", default=None
)
parser.add_argument(
    "--no-half", action="store_true", help="do not switch the model to 16-bit floats"
)
parser.add_argument(
    "--no-half-vae",
    action="store_true",
    help="do not switch the VAE model to 16-bit floats",
)
parser.add_argument(
    "--no-progressbar-hiding",
    action="store_true",
    help="do not hide progressbar in gradio UI (we hide it because it slows down ML if you have hardware acceleration in browser)",
)
parser.add_argument(
    "--max-batch-count",
    type=int,
    default=16,
    help="maximum batch count value for the UI",
)
parser.add_argument(
    "--embeddings-dir",
    type=str,
    default=os.path.join(paths.script_path, "embeddings"),
    help="embeddings directory for textual inversion (default: embeddings)",
)
parser.add_argument(
    "--hypernetwork-dir",
    type=str,
    default=os.path.join(paths.models_path, "hypernetworks"),
    help="hypernetwork directory",
)
parser.add_argument(
    "--localizations-dir",
    type=str,
    default=os.path.join(paths.script_path, "localizations"),
    help="localizations directory",
)
parser.add_argument(
    "--allow-code", action="store_true", help="allow custom script execution from webui"
)
parser.add_argument(
    "--medvram",
    action="store_true",
    help="enable stable diffusion model optimizations for sacrificing a little speed for low VRM usage",
)
parser.add_argument(
    "--lowvram",
    action="store_true",
    help="enable stable diffusion model optimizations for sacrificing a lot of speed for very low VRM usage",
)
parser.add_argument(
    "--lowram",
    action="store_true",
    help="load stable diffusion checkpoint weights to VRAM instead of RAM",
)
parser.add_argument(
    "--always-batch-cond-uncond",
    action="store_true",
    help="disables cond/uncond batching that is enabled to save memory with --medvram or --lowvram",
)
parser.add_argument(
    "--unload-gfpgan", action="store_true", help="does not do anything."
)
parser.add_argument(
    "--precision",
    type=str,
    help="evaluate at this precision",
    choices=["full", "autocast"],
    default="autocast",
)
parser.add_argument(
    "--share",
    action="store_true",
    help="use share=True for gradio and make the UI accessible through their site (doesn't work for me but you might have better luck)",
)

parser.add_argument(
    "--ngrok",
    type=str,
    help="ngrok authtoken, alternative to gradio --share",
    default=None,
)
parser.add_argument(
    "--ngrok-region",
    type=str,
    help="The region in which ngrok should start.",
    default="us",
)
parser.add_argument(
    "--codeformer-models-path",
    type=str,
    help="Path to directory with codeformer model file(s).",
    default=os.path.join(paths.models_path, "Codeformer"),
)
parser.add_argument(
    "--gfpgan-models-path",
    type=str,
    help="Path to directory with GFPGAN model file(s).",
    default=os.path.join(paths.models_path, "GFPGAN"),
)
parser.add_argument(
    "--esrgan-models-path",
    type=str,
    help="Path to directory with ESRGAN model file(s).",
    default=os.path.join(paths.models_path, "ESRGAN"),
)
parser.add_argument(
    "--bsrgan-models-path",
    type=str,
    help="Path to directory with BSRGAN model file(s).",
    default=os.path.join(paths.models_path, "BSRGAN"),
)
parser.add_argument(
    "--realesrgan-models-path",
    type=str,
    help="Path to directory with RealESRGAN model file(s).",
    default=os.path.join(paths.models_path, "RealESRGAN"),
)
parser.add_argument(
    "--scunet-models-path",
    type=str,
    help="Path to directory with ScuNET model file(s).",
    default=os.path.join(paths.models_path, "ScuNET"),
)
parser.add_argument(
    "--swinir-models-path",
    type=str,
    help="Path to directory with SwinIR model file(s).",
    default=os.path.join(paths.models_path, "SwinIR"),
)
parser.add_argument(
    "--ldsr-models-path",
    type=str,
    help="Path to directory with LDSR model file(s).",
    default=os.path.join(paths.models_path, "LDSR"),
)
parser.add_argument(
    "--xformers", action="store_true", help="enable xformers for cross attention layers"
)
parser.add_argument(
    "--force-enable-xformers",
    action="store_true",
    help="enable xformers for cross attention layers regardless of whether the checking code thinks you can run it; do not make bug reports if this fails to work",
)
parser.add_argument(
    "--deepdanbooru", action="store_true", help="enable deepdanbooru interrogator"
)
parser.add_argument(
    "--opt-split-attention",
    action="store_true",
    help="force-enables Doggettx's cross-attention layer optimization. By default, it's on for torch cuda.",
)
parser.add_argument(
    "--opt-split-attention-invokeai",
    action="store_true",
    help="force-enables InvokeAI's cross-attention layer optimization. By default, it's on when cuda is unavailable.",
)

parser.add_argument(
    "--opt-split-attention-v1",
    action="store_true",
    help="enable older version of split attention optimization that does not consume all the VRAM it can find",
)
parser.add_argument(
    "--disable-opt-split-attention",
    action="store_true",
    help="force-disables cross-attention layer optimization",
)
parser.add_argument(
    "--use-cpu",
    nargs="+",
    choices=[
        "all",
        "sd",
        "interrogate",
        "gfpgan",
        "swinir",
        "esrgan",
        "scunet",
        "codeformer",
    ],
    help="use CPU as torch device for specified modules",
    default=[],
    type=str.lower,
)
parser.add_argument(
    "--listen",
    action="store_true",
    help="launch gradio with 0.0.0.0 as server name, allowing to respond to network requests",
)
parser.add_argument(
    "--port",
    type=int,
    help="launch gradio with given server port, you need root/admin rights for ports < 1024, defaults to 7860 if available",
    default=None,
)

parser.add_argument(
    "--show-negative-prompt",
    action="store_true",
    help="does not do anything",
    default=False,
)
parser.add_argument(
    "--ui-config-file",
    type=str,
    help="filename to use for ui configuration",
    default=os.path.join(paths.script_path, "ui-config.json"),
)
parser.add_argument(
    "--hide-ui-dir-config",
    action="store_true",
    help="hide directory configuration from webui",
    default=False,
)
parser.add_argument(
    "--freeze-settings",
    action="store_true",
    help="disable editing settings",
    default=False,
)
parser.add_argument(
    "--ui-settings-file",
    type=str,
    help="filename to use for ui settings",
    default=os.path.join(paths.script_path, "config.json"),
)
parser.add_argument(
    "--gradio-debug", action="store_true", help="launch gradio with --debug option"
)
parser.add_argument(
    "--gradio-auth",
    type=str,
    help='set gradio authentication like "username:password"; or comma-delimit multiple like "u1:p1,u2:p2,u3:p3"',
    default=None,
)

parser.add_argument(
    "--gradio-img2img-tool",
    type=str,
    help="gradio image uploader tool: can be either editor for ctopping, or color-sketch for drawing",
    choices=["color-sketch", "editor"],
    default="editor",
)
parser.add_argument(
    "--opt-channelslast",
    action="store_true",
    help="change memory type for stable diffusion to channels last",
)
parser.add_argument(
    "--styles-file",
    type=str,
    help="filename to use for styles",
    default=os.path.join(paths.script_path, "styles.csv"),
)
parser.add_argument(
    "--autolaunch",
    action="store_true",
    help="open the webui URL in the system's default browser upon launch",
    default=False,
)
parser.add_argument(
    "--theme", type=str, help="launches the UI with light or dark theme", default=None
)
parser.add_argument(
    "--use-textbox-seed",
    action="store_true",
    help="use textbox for seeds in UI (no up/down, but possible to input long seeds)",
    default=False,
)
parser.add_argument(
    "--disable-console-progressbars",
    action="store_true",
    help="do not output progressbars to console",
    default=False,
)
parser.add_argument(
    "--enable-console-prompts",
    action="store_true",
    help="print prompts to console when generating with txt2img and img2img",
    default=False,
)
parser.add_argument(
    "--vae-path", type=str, help="Path to Variational Autoencoders model", default=None
)

parser.add_argument(
    "--disable-safe-unpickle",
    action="store_true",
    help="disable checking pytorch models for malicious code",
    default=False,
)
parser.add_argument(
    "--api", action="store_true", help="use api=True to launch the api with the webui"
)
parser.add_argument(
    "--nowebui",
    action="store_true",
    help="use api=True to launch the api instead of the webui",
)
parser.add_argument(
    "--ui-debug-mode", action="store_true", help="Don't load model to quickly launch UI"
)
parser.add_argument(
    "--device-id",
    type=str,
    help="Select the default CUDA device to use (export CUDA_VISIBLE_DEVICES=0,1,etc might be needed before)",
    default=None,
)

cmd_opts = parser.parse_args()
