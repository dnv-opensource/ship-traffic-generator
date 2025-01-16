# Traffic Generator
The tool generates a structured set of encounters for verifying automatic collision and grounding avoidance systems.
Based on input parameters such as desired situation, relative speed, relative bearing etc,
the tool will generate a set of traffic situations. The traffic situations may be written to files and/or inspected using plots.

A paper is written describing the background for the tool and how it works <a href="./docs/ICMASS23_verfying_caga_systems.pdf" target="_blank">[paper]</a>

## Installation
To install Ship Traffic Generator, run this command in your terminal:
```sh
pip install trafficgen
```

## UV
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

## Python
The traffic generator requires Python 3.10 or later. <br>

If you don't already have a compatible version installed on your machine, you way install Python through `uv`:
```sh
uv python install
```
This will install the latest stable version of Python into the uv Python directory, i.e. as a uv-managed version of Python.

Alternatively, and if you want a standalone version of Python on your machine, you can install Python either via `winget`:
```sh
winget install --id Python.Python
```
or you can download and install Python from the [python.org](https://www.python.org/downloads/) website.

## Clone the repository
Clone the traffig generator repository into your local development directory:
```sh
git clone https://github.com/dnv-opensource/ship-traffic-generator path/to/your/dir/ship-traffic-generator
```
Change into the project directory after cloning:
```sh
cd ship-traffic-generator
```

## Install dependencies
Run `uv sync` to create a virtual environment and install all project dependencies into it:
```sh
uv sync
```
> **Note**: Using `--no-dev` will omit installing development dependencies.

> **Note**: `uv` will create a new virtual environment called `.venv` in the project root directory when running
> `uv sync` the first time. Optionally, you can create your own virtual environment using e.g. `uv venv`, before running
> `uv sync`.

You can check your installation by running:
```sh
uv run trafficgen --help
```

For more information on usage, run:
```sh
trafficgen gen-situation --help
```
or build the documentation (see below).

TODO: FORTSETT HER, HVORDAN BYGGE DOKUMENTASJON
## Development & Documentation
For development (dependency management, documentation and testing) it is recommended to use [Poetry](https://python-poetry.org/docs/).
See Poetry's documentation for information of how to install and set up.

See above notes about creating and using a virtual environment.
To install the package, including dev and doc dependencies:
```sh
$ cd ship_traffic_generator
$ poetry install
$ poetry install --with dev,docs
```
which will install the package, the cli and all development and documentation dependencies.


You can check your installation with:
```sh
$ trafficgen --help
```
or
```sh
$ trafficgen gen-situation --help
```
Note: You may have to restart your terminal (or update the path) for the command line command to work, or use the Poetry shell (`poetry shell`) to correct the search path.

Testing in the project is done using [pytest](https://docs.pytest.org/) and
the format of the code is checked with [flake8](https://flake8.pycqa.org/en/latest/).
You can run the tests and check formating with [`tox`](https://tox.wiki/):
```sh
$ tox run
```

To generate documentation do:
```sh
$ cd docs
$ sphinx-build -M html . build
```
The html documentation will then be available in `docs/build/html/index.html`




## Credits
This package was created with Cookiecutter and the `audreyr/cookiecutter-pypackage` project template.
* [Cookiecutter](https://github.com/audreyr/cookiecutter)
* [`audreyr/cookiecutter-pypackage`](https://github.com/audreyr/cookiecutter-pypackage)
