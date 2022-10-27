import datetime
import os
import sys

import tqdm

import modules.command_options.options as options
import modules.shared_steps.options as shared_options
import modules.devices as devices
import modules.interrogate
import modules.memmon
import modules.sd_models
import modules.styles


restricted_opts = {
    "samples_filename_pattern",
    "directories_filename_pattern",
    "outdir_samples",
    "outdir_txt2img_samples",
    "outdir_img2img_samples",
    "outdir_extras_samples",
    "outdir_grids",
    "outdir_txt2img_grids",
    "outdir_save",
}

(
    devices.device,
    devices.device_interrogate,
    devices.device_gfpgan,
    devices.device_swinir,
    devices.device_esrgan,
    devices.device_scunet,
    devices.device_codeformer,
) = (
    devices.cpu
    if any(y in options.cmd_opts.use_cpu for y in [x, "all"])
    else devices.get_optimal_device()
    for x in ["sd", "interrogate", "gfpgan", "swinir", "esrgan", "scunet", "codeformer"]
)

device = devices.device
weight_load_location = None if options.cmd_opts.lowram else "cpu"

batch_cond_uncond = options.cmd_opts.always_batch_cond_uncond or not (
    options.cmd_opts.lowvram or options.cmd_opts.medvram
)
parallel_processing_allowed = not options.cmd_opts.lowvram and not options.cmd_opts.medvram
xformers_available = False
config_filename = options.cmd_opts.ui_settings_file

os.makedirs(options.cmd_opts.hypernetwork_dir, exist_ok=True)
loaded_hypernetwork = None


class State:
    skipped = False
    interrupted = False
    job = ""
    job_no = 0
    job_count = 0
    job_timestamp = "0"
    sampling_step = 0
    sampling_steps = 0
    current_latent = None
    current_image = None
    current_image_sampling_step = 0
    textinfo = None

    def skip(self):
        self.skipped = True

    def interrupt(self):
        self.interrupted = True

    def nextjob(self):
        self.job_no += 1
        self.sampling_step = 0
        self.current_image_sampling_step = 0

    def get_job_timestamp(self):
        return datetime.datetime.now().strftime(
            "%Y%m%d%H%M%S"
        )  # shouldn't this return job_timestamp?


state = State()

styles_filename = options.cmd_opts.styles_file
prompt_styles = modules.styles.StyleDatabase(styles_filename)

interrogator = modules.interrogate.InterrogateModels("interrogate")


if os.path.exists(config_filename):
    shared_options.opts.load(config_filename)


sd_model = None

clip_model = None

progress_print_out = sys.stdout


class TotalTQDM:
    def __init__(self):
        self._tqdm = None

    def reset(self):
        self._tqdm = tqdm.tqdm(
            desc="Total progress",
            total=state.job_count * state.sampling_steps,
            position=1,
            file=progress_print_out,
        )

    def update(self):
        if not shared_options.opts.multiple_tqdm or options.cmd_opts.disable_console_progressbars:
            return
        if self._tqdm is None:
            self.reset()
        self._tqdm.update()

    def updateTotal(self, new_total):
        if not shared_options.opts.multiple_tqdm or options.cmd_opts.disable_console_progressbars:
            return
        if self._tqdm is None:
            self.reset()
        self._tqdm.total = new_total

    def clear(self):
        if self._tqdm is not None:
            self._tqdm.close()
            self._tqdm = None


total_tqdm = TotalTQDM()

mem_mon = modules.memmon.MemUsageMonitor("MemMon", device, shared_options.opts)
mem_mon.start()
