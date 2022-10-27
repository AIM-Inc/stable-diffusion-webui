import gradio as gr
import os

import modules.artists as artists
import modules.command_options.options as modules_options
import modules.hypernetworks.hypernetwork as hypernetwork
import modules.localization as localization
import modules.paths as paths
import modules.sd_models as sd_models
import modules.sd_samplers as sd_samplers


artist_db = artists.ArtistsDatabase(os.path.join(paths.script_path, "artists.csv"))

localization.list_localizations(modules_options.cmd_opts.localizations_dir)

hypernetworks = hypernetwork.list_hypernetworks(modules_options.cmd_opts.hypernetwork_dir)


class OptionInfo:
    def __init__(
        self,
        default=None,
        label="",
        component=None,
        component_args=None,
        onchange=None,
        section=None,
        refresh=None,
    ):
        self.default = default
        self.label = label
        self.component = component
        self.component_args = component_args
        self.onchange = onchange
        self.section = section
        self.refresh = refresh


def options_section(section_identifier, options_dict):
    for k, v in options_dict.items():
        v.section = section_identifier

    return options_dict


def realesrgan_models_names():
    import modules.realesrgan_model

    return [x.name for x in modules.realesrgan_model.get_realesrgan_models(None)]


def reload_hypernetworks():
    global hypernetworks

    hypernetworks = hypernetworks.hypernetwork.list_hypernetworks(modules_options.cmd_opts.hypernetwork_dir)
    hypernetworks.hypernetwork.load_hypernetwork(modules_options.opts.sd_hypernetwork)


sd_upscalers = []
face_restorers = []

hide_dirs = {"visible": not modules_options.cmd_opts.hide_ui_dir_config}

options_templates = {}

options_templates.update(
    options_section(
        ("saving-images", "Saving images/grids"),
        {
            "samples_save": OptionInfo(True, "Always save all generated images"),
            "samples_format": OptionInfo("png", "File format for images"),
            "samples_filename_pattern": OptionInfo(
                "", "Images filename pattern", component_args=hide_dirs
            ),
            "save_images_add_number": OptionInfo(
                True, "Add number to filename when saving", component_args=hide_dirs
            ),
            "grid_save": OptionInfo(True, "Always save all generated image grids"),
            "grid_format": OptionInfo("png", "File format for grids"),
            "grid_extended_filename": OptionInfo(
                False, "Add extended info (seed, prompt) to filename when saving grid"
            ),
            "grid_only_if_multiple": OptionInfo(
                True, "Do not save grids consisting of one picture"
            ),
            "grid_prevent_empty_spots": OptionInfo(
                False, "Prevent empty spots in grid (when set to autodetect)"
            ),
            "n_rows": OptionInfo(
                -1,
                "Grid row count; use -1 for autodetect and 0 for it to be same as batch size",
                gr.Slider,
                {"minimum": -1, "maximum": 16, "step": 1},
            ),
            "enable_pnginfo": OptionInfo(
                True,
                "Save text information about generation parameters as chunks to png files",
            ),
            "save_txt": OptionInfo(
                False,
                "Create a text file next to every image with generation parameters.",
            ),
            "save_images_before_face_restoration": OptionInfo(
                False, "Save a copy of image before doing face restoration."
            ),
            "jpeg_quality": OptionInfo(
                80,
                "Quality for saved jpeg images",
                gr.Slider,
                {"minimum": 1, "maximum": 100, "step": 1},
            ),
            "export_for_4chan": OptionInfo(
                True,
                "If PNG image is larger than 4MB or any dimension is larger than 4000, downscale and save copy as JPG",
            ),
            "use_original_name_batch": OptionInfo(
                False,
                "Use original name for output filename during batch process in extras tab",
            ),
            "save_selected_only": OptionInfo(
                True, "When using 'Save' button, only save a single selected image"
            ),
            "do_not_add_watermark": OptionInfo(False, "Do not add watermark to images"),
        },
    )
)

options_templates.update(
    options_section(
        ("saving-paths", "Paths for saving"),
        {
            "outdir_samples": OptionInfo(
                "",
                "Output directory for images; if empty, defaults to three directories below",
                component_args=hide_dirs,
            ),
            "outdir_txt2img_samples": OptionInfo(
                "outputs/txt2img-images",
                "Output directory for txt2img images",
                component_args=hide_dirs,
            ),
            "outdir_img2img_samples": OptionInfo(
                "outputs/img2img-images",
                "Output directory for img2img images",
                component_args=hide_dirs,
            ),
            "outdir_extras_samples": OptionInfo(
                "outputs/extras-images",
                "Output directory for images from extras tab",
                component_args=hide_dirs,
            ),
            "outdir_grids": OptionInfo(
                "",
                "Output directory for grids; if empty, defaults to two directories below",
                component_args=hide_dirs,
            ),
            "outdir_txt2img_grids": OptionInfo(
                "outputs/txt2img-grids",
                "Output directory for txt2img grids",
                component_args=hide_dirs,
            ),
            "outdir_img2img_grids": OptionInfo(
                "outputs/img2img-grids",
                "Output directory for img2img grids",
                component_args=hide_dirs,
            ),
            "outdir_save": OptionInfo(
                "log/images",
                "Directory for saving images using the Save button",
                component_args=hide_dirs,
            ),
        },
    )
)

options_templates.update(
    options_section(
        ("saving-to-dirs", "Saving to a directory"),
        {
            "save_to_dirs": OptionInfo(False, "Save images to a subdirectory"),
            "grid_save_to_dirs": OptionInfo(False, "Save grids to a subdirectory"),
            "use_save_to_dirs_for_ui": OptionInfo(
                False, 'When using "Save" button, save images to a subdirectory'
            ),
            "directories_filename_pattern": OptionInfo(
                "", "Directory name pattern", component_args=hide_dirs
            ),
            "directories_max_prompt_words": OptionInfo(
                8,
                "Max prompt words for [prompt_words] pattern",
                gr.Slider,
                {"minimum": 1, "maximum": 20, "step": 1, **hide_dirs},
            ),
        },
    )
)

options_templates.update(
    options_section(
        ("upscaling", "Upscaling"),
        {
            "ESRGAN_tile": OptionInfo(
                192,
                "Tile size for ESRGAN upscalers. 0 = no tiling.",
                gr.Slider,
                {"minimum": 0, "maximum": 512, "step": 16},
            ),
            "ESRGAN_tile_overlap": OptionInfo(
                8,
                "Tile overlap, in pixels for ESRGAN upscalers. Low values = visible seam.",
                gr.Slider,
                {"minimum": 0, "maximum": 48, "step": 1},
            ),
            "realesrgan_enabled_models": OptionInfo(
                ["R-ESRGAN x4+", "R-ESRGAN x4+ Anime6B"],
                "Select which Real-ESRGAN models to show in the web UI. (Requires restart)",
                gr.CheckboxGroup,
                lambda: {"choices": realesrgan_models_names()},
            ),
            "SWIN_tile": OptionInfo(
                192,
                "Tile size for all SwinIR.",
                gr.Slider,
                {"minimum": 16, "maximum": 512, "step": 16},
            ),
            "SWIN_tile_overlap": OptionInfo(
                8,
                "Tile overlap, in pixels for SwinIR. Low values = visible seam.",
                gr.Slider,
                {"minimum": 0, "maximum": 48, "step": 1},
            ),
            "ldsr_steps": OptionInfo(
                100,
                "LDSR processing steps. Lower = faster",
                gr.Slider,
                {"minimum": 1, "maximum": 200, "step": 1},
            ),
            "upscaler_for_img2img": OptionInfo(
                None,
                "Upscaler for img2img",
                gr.Dropdown,
                lambda: {"choices": [x.name for x in sd_upscalers]},
            ),
            "use_scale_latent_for_hires_fix": OptionInfo(
                False, "Upscale latent space image when doing hires. fix"
            ),
        },
    )
)

options_templates.update(
    options_section(
        ("face-restoration", "Face restoration"),
        {
            "face_restoration_model": OptionInfo(
                None,
                "Face restoration model",
                gr.Radio,
                lambda: {"choices": [x.name() for x in face_restorers]},
            ),
            "code_former_weight": OptionInfo(
                0.5,
                "CodeFormer weight parameter; 0 = maximum effect; 1 = minimum effect",
                gr.Slider,
                {"minimum": 0, "maximum": 1, "step": 0.01},
            ),
            "face_restoration_unload": OptionInfo(
                False, "Move face restoration model from VRAM into RAM after processing"
            ),
        },
    )
)

options_templates.update(
    options_section(
        ("system", "System"),
        {
            "memmon_poll_rate": OptionInfo(
                8,
                "VRAM usage polls per second during generation. Set to 0 to disable.",
                gr.Slider,
                {"minimum": 0, "maximum": 40, "step": 1},
            ),
            "samples_log_stdout": OptionInfo(
                False, "Always print all generation info to standard output"
            ),
            "multiple_tqdm": OptionInfo(
                True,
                "Add a second progress bar to the console that shows progress for an entire job.",
            ),
        },
    )
)

options_templates.update(
    options_section(
        ("training", "Training"),
        {
            "unload_models_when_training": OptionInfo(
                False,
                "Move VAE and CLIP to RAM when training hypernetwork. Saves VRAM.",
            ),
            "dataset_filename_word_regex": OptionInfo("", "Filename word regex"),
            "dataset_filename_join_string": OptionInfo(" ", "Filename join string"),
            "training_image_repeats_per_epoch": OptionInfo(
                1,
                "Number of repeats for a single input image per epoch; used only for displaying epoch number",
                gr.Number,
                {"precision": 0},
            ),
            "training_write_csv_every": OptionInfo(
                500,
                "Save an csv containing the loss to log directory every N steps, 0 to disable",
            ),
        },
    )
)

options_templates.update(
    options_section(
        ("sd", "Stable Diffusion"),
        {
            "sd_model_checkpoint": OptionInfo(
                None,
                "Stable Diffusion checkpoint",
                gr.Dropdown,
                lambda: {"choices": sd_models.checkpoint_tiles()},
                refresh=sd_models.list_models,
            ),
            "sd_checkpoint_cache": OptionInfo(
                0,
                "Checkpoints to cache in RAM",
                gr.Slider,
                {"minimum": 0, "maximum": 10, "step": 1},
            ),
            "sd_hypernetwork": OptionInfo(
                "None",
                "Hypernetwork",
                gr.Dropdown,
                lambda: {"choices": ["None"] + [x for x in hypernetworks.keys()]},
                refresh=reload_hypernetworks,
            ),
            "sd_hypernetwork_strength": OptionInfo(
                1.0,
                "Hypernetwork strength",
                gr.Slider,
                {"minimum": 0.0, "maximum": 1.0, "step": 0.001},
            ),
            "img2img_color_correction": OptionInfo(
                False,
                "Apply color correction to img2img results to match original colors.",
            ),
            "save_images_before_color_correction": OptionInfo(
                False,
                "Save a copy of image before applying color correction to img2img results",
            ),
            "img2img_fix_steps": OptionInfo(
                False,
                "With img2img, do exactly the amount of steps the slider specifies (normally you'd do less with less denoising).",
            ),
            "enable_quantization": OptionInfo(
                False,
                "Enable quantization in K samplers for sharper and cleaner results. This may change existing seeds. Requires restart to apply.",
            ),
            "enable_emphasis": OptionInfo(
                True,
                "Emphasis: use (text) to make model pay more attention to text and [text] to make it pay less attention",
            ),
            "use_old_emphasis_implementation": OptionInfo(
                False,
                "Use old emphasis implementation. Can be useful to reproduce old seeds.",
            ),
            "enable_batch_seeds": OptionInfo(
                True,
                "Make K-diffusion samplers produce same images in a batch as when making a single image",
            ),
            "comma_padding_backtrack": OptionInfo(
                20,
                "Increase coherency by padding from the last comma within n tokens when using more than 75 tokens",
                gr.Slider,
                {"minimum": 0, "maximum": 74, "step": 1},
            ),
            "filter_nsfw": OptionInfo(False, "Filter NSFW content"),
            "CLIP_stop_at_last_layers": OptionInfo(
                1,
                "Stop At last layers of CLIP model",
                gr.Slider,
                {"minimum": 1, "maximum": 12, "step": 1},
            ),
            "random_artist_categories": OptionInfo(
                [],
                "Allowed categories for random artists selection when using the Roll button",
                gr.CheckboxGroup,
                {"choices": artist_db.categories()},
            ),
        },
    )
)

options_templates.update(
    options_section(
        ("interrogate", "Interrogate Options"),
        {
            "interrogate_keep_models_in_memory": OptionInfo(
                False, "Interrogate: keep models in VRAM"
            ),
            "interrogate_use_builtin_artists": OptionInfo(
                True, "Interrogate: use artists from artists.csv"
            ),
            "interrogate_return_ranks": OptionInfo(
                False,
                "Interrogate: include ranks of model tags matches in results (Has no effect on caption-based interrogators).",
            ),
            "interrogate_clip_num_beams": OptionInfo(
                1,
                "Interrogate: num_beams for BLIP",
                gr.Slider,
                {"minimum": 1, "maximum": 16, "step": 1},
            ),
            "interrogate_clip_min_length": OptionInfo(
                24,
                "Interrogate: minimum description length (excluding artists, etc..)",
                gr.Slider,
                {"minimum": 1, "maximum": 128, "step": 1},
            ),
            "interrogate_clip_max_length": OptionInfo(
                48,
                "Interrogate: maximum description length",
                gr.Slider,
                {"minimum": 1, "maximum": 256, "step": 1},
            ),
            "interrogate_clip_dict_limit": OptionInfo(
                1500, "CLIP: maximum number of lines in text file (0 = No limit)"
            ),
            "interrogate_deepbooru_score_threshold": OptionInfo(
                0.5,
                "Interrogate: deepbooru score threshold",
                gr.Slider,
                {"minimum": 0, "maximum": 1, "step": 0.01},
            ),
            "deepbooru_sort_alpha": OptionInfo(
                True, "Interrogate: deepbooru sort alphabetically"
            ),
            "deepbooru_use_spaces": OptionInfo(
                False, "use spaces for tags in deepbooru"
            ),
            "deepbooru_escape": OptionInfo(
                True,
                "escape (\\) brackets in deepbooru (so they are used as literal brackets and not for emphasis)",
            ),
        },
    )
)

options_templates.update(
    options_section(
        ("ui", "User interface"),
        {
            "show_progressbar": OptionInfo(True, "Show progressbar"),
            "show_progress_every_n_steps": OptionInfo(
                0,
                "Show image creation progress every N sampling steps. Set 0 to disable.",
                gr.Slider,
                {"minimum": 0, "maximum": 32, "step": 1},
            ),
            "show_progress_grid": OptionInfo(
                True, "Show previews of all images generated in a batch as a grid"
            ),
            "return_grid": OptionInfo(True, "Show grid in results for web"),
            "do_not_show_images": OptionInfo(
                False, "Do not show any images in results for web"
            ),
            "add_model_hash_to_info": OptionInfo(
                True, "Add model hash to generation information"
            ),
            "add_model_name_to_info": OptionInfo(
                False, "Add model name to generation information"
            ),
            "disable_weights_auto_swap": OptionInfo(
                False,
                "When reading generation parameters from text into UI (from PNG info or pasted text), do not change the selected model/checkpoint.",
            ),
            "font": OptionInfo("", "Font for image grids that have text"),
            "js_modal_lightbox": OptionInfo(True, "Enable full page image viewer"),
            "js_modal_lightbox_initially_zoomed": OptionInfo(
                True, "Show images zoomed in by default in full page image viewer"
            ),
            "show_progress_in_title": OptionInfo(
                True, "Show generation progress in window title."
            ),
            "quicksettings": OptionInfo("sd_model_checkpoint", "Quicksettings list"),
            "localization": OptionInfo(
                "None",
                "Localization (requires restart)",
                gr.Dropdown,
                lambda: {"choices": ["None"] + list(localization.localizations.keys())},
                refresh=lambda: localization.list_localizations(
                    modules_options.cmd_opts.localizations_dir
                ),
            ),
        },
    )
)

options_templates.update(
    options_section(
        ("sampler-params", "Sampler parameters"),
        {
            "hide_samplers": OptionInfo(
                [],
                "Hide samplers in user interface (requires restart)",
                gr.CheckboxGroup,
                lambda: {"choices": [x.name for x in sd_samplers.all_samplers]},
            ),
            "eta_ddim": OptionInfo(
                0.0,
                "eta (noise multiplier) for DDIM",
                gr.Slider,
                {"minimum": 0.0, "maximum": 1.0, "step": 0.01},
            ),
            "eta_ancestral": OptionInfo(
                1.0,
                "eta (noise multiplier) for ancestral samplers",
                gr.Slider,
                {"minimum": 0.0, "maximum": 1.0, "step": 0.01},
            ),
            "ddim_discretize": OptionInfo(
                "uniform",
                "img2img DDIM discretize",
                gr.Radio,
                {"choices": ["uniform", "quad"]},
            ),
            "s_churn": OptionInfo(
                0.0,
                "sigma churn",
                gr.Slider,
                {"minimum": 0.0, "maximum": 1.0, "step": 0.01},
            ),
            "s_tmin": OptionInfo(
                0.0,
                "sigma tmin",
                gr.Slider,
                {"minimum": 0.0, "maximum": 1.0, "step": 0.01},
            ),
            "s_noise": OptionInfo(
                1.0,
                "sigma noise",
                gr.Slider,
                {"minimum": 0.0, "maximum": 1.0, "step": 0.01},
            ),
            "eta_noise_seed_delta": OptionInfo(
                0, "Eta noise seed delta", gr.Number, {"precision": 0}
            ),
        },
    )
)
