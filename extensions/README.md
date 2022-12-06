# stable-diffusion-extensions

## Configuration

The `config/config.json` file is meant to be used to apply external dependencies of an extension upon installing it.

As an example, the `depthmap2mask` extension has a dependency for the `MiDaS` repository which needs to be installed in the `repositories/` directory of the `stable-diffusion-webui` in order to be able to use it.

The configuration looks like so in order to apply this dependency when the Web UI is launched:

```json
{
  "depthmap2mask": {
    "repositories": [
      {
        "url": "...",
        "path": "repositories/midas",
        "name": "midas"
      }
    ]
  }
}
```

- `"depthmap2mask"` - type Object, the extension that has the dependency where its value is an object
- `"repositories"` - type List, all extensions that are declared in the file must have this key
  - **Items added to the list must be of Object type**
  - Items added to the list must have the `"url"`, `"path"`, and `"name"` keys
    - `"url"` - type String, the URL that points to a GitHub repo
    - `"path"` - type String, the path of the Stable Diffusion Web UI `repositories/` directory. The prefix should be `repositories/<name_of_folder_for_repo_being_cloned>`
    - `"name"` - type String, a friendly name of the repo that is being downloaded for logging purposes
