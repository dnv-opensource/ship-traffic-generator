# Traffic Generator
The tool generates a structured set of encounters for verifying automatic collision and grounding avoidance systems.
Based on input parameters such as desired situation, relative speed, relative bearing etc,
the tool will generate a set of traffic situations. The traffic situations may be written to files and/or inspected using plots.

A paper is written describing the background for the tool and how it works <a href="./docs/source/ICMASS23_verfying_caga_systems.pdf" target="_blank">[paper]</a>

For package documentation, see [https://dnv-opensource.github.io/ship-traffic-generator/](https://dnv-opensource.github.io/ship-traffic-generator/)

## Installation

To install Ship Traffic Generator, run this command in your terminal:
```sh
pip install trafficgen
```
This is the preferred method to install Traffic Generator, as it will always install the most recent stable release.

You can check your installation by running:
```sh
uv run trafficgen --help
```

## Usage

For simplest usage, clone this repo, then run ```pip install -e .``` (you may want to do this in a local environment, such as a venv, see an example with `uv` below).

Then run: ```trafficgen gen-situation```.  You can add the option `-v` for visualization.

For further explanations, see the [documentation pages](https://dnv-opensource.github.io/ship-traffic-generator/) of the Ship Traffic Generator.

## Development Setup

### Install UV

This project uses `uv` as package manager.
If you haven't already, install [uv](https://docs.astral.sh/uv), preferably using it's ["Standalone installer"](https://docs.astral.sh/uv/getting-started/installation/#__tabbed_1_2) method: <br>
..on Windows:
```sh
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
..on MacOS and Linux:
```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```
(see [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/) for all / alternative installation methods.)

Once installed, you can update `uv` to its latest version, anytime, by running:
```sh
uv self update
```

### Install Python
The traffic generator requires Python 3.11 or later. <br>

If you don't already have a compatible version installed on your machine, you way install Python through `uv`:
```sh
uv python install
```
This will install the latest stable version of Python into the uv Python directory, i.e. as a uv-managed version of Python.
> **Note**: you can also do this after you clone the repo, see below.

Alternatively, and if you want a standalone version of Python on your machine, you can install Python either via `winget`:
```sh
winget install --id Python.Python
```
or you can download and install Python from the [python.org](https://www.python.org/downloads/) website.

### Clone the repository
Clone the traffig generator repository into your local development directory:
```sh
git clone https://github.com/dnv-opensource/ship-traffic-generator path/to/your/dir/ship-traffic-generator
```
Change into the project directory after cloning:
```sh
cd ship-traffic-generator
```

### Install dependencies

Run `uv sync -U` to create a virtual environment and install all project dependencies into it:
```sh
uv sync -U
```
> **Note**: Using `--no-dev` will omit installing development dependencies.

> **Note**: You can also define the python environment at the same time, by running for example ```uv sync -U -p 3.12``` to install Python 3.12.

> **Note**: `uv` will create a new virtual environment called `.venv` in the project root directory when running
> `uv sync` the first time. Optionally, you can create your own virtual environment using e.g. `uv venv`, before running
> `uv sync`.

### (Optional) Activate the virtual environment
When using `uv`, there is in almost all cases no longer a need to manually activate the virtual environment. <br>
`uv` will find the `.venv` virtual environment in the working directory or any parent directory, and activate it on the fly whenever you run a command via `uv` inside your project folder structure:
```sh
uv run <command>
```

However, you still _can_ manually activate the virtual environment if needed.
When developing in an IDE, for instance, this can in some cases be necessary depending on your IDE settings.
To manually activate the virtual environment, run one of the "known" legacy commands: <br>
..on Windows:
```sh
.venv\Scripts\activate.bat
```
> **Note**: If you use the cmd terminal in VS Code, it will show this activated venv as (trafficgen) at the start of every line command.
..on Linux:
```sh
source .venv/bin/activate
```

### Install the package

```sh
uv pip install -e .
```

### Documentation

For pre-generated package documentation, see [https://dnv-opensource.github.io/ship-traffic-generator/](https://dnv-opensource.github.io/ship-traffic-generator/)

To generate documentation from the source code, use:
```sh
uv run docs/make.bat html
```
The html documentation will then be available in `docs/build/html/index.html`
