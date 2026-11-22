# Python in Netlify builds

- Python 3.x is available at build time; choose the version with `PYTHON_VERSION`, `runtime.txt` or `Pipfile`; pip matches the Python version.
- Set it in `netlify.toml`: `[build.environment] PYTHON_VERSION = "3.12"`.
- The build command runs in Bash; `publish` is the folder that gets deployed.

## Sources
- https://docs.netlify.com/build/configure-builds/available-software-at-build-time/
- https://www.netlify.com/blog/announcing-configurable-python-versions-in-netlify-builds
- https://docs.netlify.com/build/configure-builds/file-based-configuration/
