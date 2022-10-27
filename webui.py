import importlib
import os
import signal
import threading
import time

from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

import modules.codeformer_model as codeformer
import modules.extras
import modules.face_restoration
import modules.gfpgan_model as gfpgan
import modules.hypernetworks.hypernetwork
import modules.img2img
import modules.lowvram
import modules.paths
import modules.scripts
import modules.sd_hijack
import modules.sd_models
import modules.shared as shared
import modules.txt2img
import modules.ui
import modules.devices as devices
import modules.modelloader as modelloader
import modules.sd_samplers as sd_samplers
import modules.upscaler as upscaler
import modules.shared_steps.options as shared_opts

from modules.command_options.options import cmd_opts
from modules.shared_steps.templates import face_restorers

queue_lock = threading.Lock()


def wrap_queued_call(func):
    def f(*args, **kwargs):
        with queue_lock:
            res = func(*args, **kwargs)

        return res

    return f


def wrap_gradio_gpu_call(func, extra_outputs=None):
    def f(*args, **kwargs):
        devices.torch_gc()

        shared.state.sampling_step = 0
        shared.state.job_count = -1
        shared.state.job_no = 0
        shared.state.job_timestamp = shared.state.get_job_timestamp()
        shared.state.current_latent = None
        shared.state.current_image = None
        shared.state.current_image_sampling_step = 0
        shared.state.skipped = False
        shared.state.interrupted = False
        shared.state.textinfo = None

        with queue_lock:
            res = func(*args, **kwargs)

        shared.state.job = ""
        shared.state.job_count = 0

        devices.torch_gc()

        return res

    return modules.ui.wrap_gradio_call(f, extra_outputs=extra_outputs)


def initialize():
    if cmd_opts.ui_debug_mode:
        shared.sd_upscalers = upscaler.UpscalerLanczos().scalers
        modules.scripts.load_scripts()
        return

    modelloader.cleanup_models()
    modules.sd_models.setup_model()
    codeformer.setup_model(cmd_opts.codeformer_models_path)
    gfpgan.setup_model(cmd_opts.gfpgan_models_path)
    face_restorers.append(modules.face_restoration.FaceRestoration())
    modelloader.load_upscalers()

    modules.scripts.load_scripts()

    modules.sd_models.load_model()
    # trunk-ignore(git-diff-check/error)
    shared_opts.opts.onchange(
        "sd_model_checkpoint",
        wrap_queued_call(
            lambda: modules.sd_models.reload_model_weights(shared.sd_model)
        ),
    )
    shared_opts.opts.onchange(
        "sd_hypernetwork",
        wrap_queued_call(
            lambda: modules.hypernetworks.hypernetwork.load_hypernetwork(
                shared_opts.opts.sd_hypernetwork
            )
        ),
    )
    shared_opts.opts.onchange(
        "sd_hypernetwork_strength", modules.hypernetworks.hypernetwork.apply_strength
    )

    # make the program just exit at ctrl+c without waiting for anything
    def sigint_handler(sig, frame):
        print(f"Interrupted with signal {sig} in {frame}")
        os._exit(0)

    signal.signal(signal.SIGINT, sigint_handler)


def create_api(app):
    from modules.api.api import Api

    api = Api(app, queue_lock)
    return api


def wait_on_server(demo=None):
    while 1:
        time.sleep(0.5)
        if demo and getattr(demo, "do_restart", False):
            time.sleep(0.5)
            demo.close()
            time.sleep(0.5)
            break


def api_only():
    initialize()

    app = FastAPI()
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    api = create_api(app)

    api.launch(
        server_name="0.0.0.0" if cmd_opts.listen else "127.0.0.1",
        port=cmd_opts.port if cmd_opts.port else 7861,
    )


def webui():
    launch_api = cmd_opts.api
    initialize()

    while 1:
        (samplers, samplers_for_img2img) = sd_samplers.set_samplers()

        demo = modules.ui.create_ui(wrap_gradio_gpu_call, samplers, samplers_for_img2img)

        app, local_url, share_url = demo.launch(
            share=cmd_opts.share,
            server_name="0.0.0.0" if cmd_opts.listen else None,
            server_port=cmd_opts.port,
            debug=cmd_opts.gradio_debug,
            auth=[
                tuple(cred.split(":"))
                for cred in cmd_opts.gradio_auth.strip('"').split(",")
            ]
            if cmd_opts.gradio_auth
            else None,
            inbrowser=cmd_opts.autolaunch,
            prevent_thread_lock=True,
        )
        # after initial launch, disable --autolaunch for subsequent restarts
        cmd_opts.autolaunch = False

        app.add_middleware(GZipMiddleware, minimum_size=1000)

        if launch_api:
            create_api(app)

        wait_on_server(demo)

        print("Reloading Custom Scripts")
        modules.scripts.reload_scripts()
        print("Reloading modules: modules.ui")
        importlib.reload(modules.ui)
        print("Refreshing Model List")
        modules.sd_models.list_models()
        print("Restarting Gradio")


task = []
if __name__ == "__main__":
    if cmd_opts.nowebui:
        api_only()
    else:
        webui()
