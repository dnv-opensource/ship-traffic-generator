# Traffic Generator
The tool generates a structured set of encounters for verifying automatic collision and grounding avoidance systems. 
Based on input parameters such as desired situation, relative speed, relative bearing etc, 
the tool will generate a set of traffic situations. The traffic situations may be written to files and/or inspected using plots.

A paper is written describing the background for the tool and how it works <a href="./docs/ICMASS23_verfying_caga_systems.pdf" target="_blank">[paper]</a>


## Quickstart
After you clone this repository, `trafficgen` can then be installed with the following steps:
```sh
$ cd TMA_ship_traffic_generator
```

It is recommended to install the `trafficgen` package and it's dependencies in a separate
Python environment (Anaconda, pyenv, or virtualenv). `trafficgen` requires Python 3.10 or higher.

In Anaconda this can be done with:
```sh
$ conda create --name myenv python=3.10
$ conda activate myenv
```

In Powershell terminal with venv (also from VSCode), this can be done with:
```sh
$ python -m venv .venv
$ .venv\Scripts\Activate.ps1
```

Then update pip/setuptools, and install the dependencies for this repo:
```sh
$ python -m pip install --upgrade pip setuptools
$ pip install -e .
```

This will install the `trafficgen` Python package and command line tool (cli).
You can check your installation by running:
```sh
$ trafficgen --help
```

For more information on usage, run:
```sh
$ trafficgen gen-situation --help
```
or build the documentation (see below).

## Development & Documentation
For development (dependency management, documentation and testing) it is recommended to use [Poetry](https://python-poetry.org/docs/). 
See Poetry's documentation for information of how to install and set up.

See above notes about creating and using a virtual environment.
To install the package, including dev and doc dependencies:
```sh
$ cd TMA_ship_traffic_generator
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
