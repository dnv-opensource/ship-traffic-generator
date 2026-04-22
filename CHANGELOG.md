# Changelog

All notable changes to the trafficgen project will be documented in this file.<br>
The changelog format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Changed



### Dependencies
* .pre-commit-config.yaml: Updated rev of ruff-pre-commit to v0.15.9
* Updated to dictIO>=0.4.4
* Updated to flask>=3.1
* Updated to numpy>=2.4
* Updated to pytest-cov>=7.1
* Updated to python-dotenv>=1.2.2
* Updated to ruff>=0.15.9
* Updated to sphinx-argparse-cli>=1.21.3


## [0.9.0] - 2026-04-16

### Changed
* martime-schema 0.2.0 necessary updates:
  * top level version number now referencing which version of the maritime-schema is used as basis for the traffic situation files
  * initial position, sog, cog now removed from initial struct since the ships are initially placed in the first waypoint.
  * added assert as initial position, sog  and cog were made optional
  * `docs/source/output_files.rst`: Clarified that the top-level `version` field reflects the maritime-schema version; updated description to explain that `position`, `sog`, and `cog` are omitted from the `initial` struct because ships are initially placed at the first waypoint.
* GitHub workflows:
  * _test_future.yml: Updated job name to 'test315', updated Python specifiers to 3.15/py315, and updated the tested Python version range to 3.15.0-alpha - 3.15.0.
  * _test_future.yml: Improved the regex and PowerShell code that finds and removes the Python upper version constraint in pyproject.toml.
  * _build_and_publish_documentation.yml: Changed 'uv sync --upgrade' to 'uv sync --frozen' to avoid unintentional package upgrades.
  * _code_quality.yml and _build_package.yml: Replaced double quotes with single quotes (the default in .yml files).
  * Added explicit step names for uses of 'actions/checkout', 'actions/download-artifact', 'actions/upload-artifact', and 'pypa/gh-action-pypi-publish' for readability and consistency.
  * Standardized artifact naming by ensuring 'upload-artifact' and 'download-artifact' use 'dist' consistently.
  * pull_request_to_main.yml and nightly_build.yml: Added 'workflow_dispatch:' to allow manual triggering.
  * Changed 'uv sync --upgrade' to 'uv sync -U'.
  * Removed redundant 'Set up Python' steps (no longer needed because 'uv sync' installs Python if required).
  * Renamed workflow step text to be more precise: 'Build source distribution and wheels' and 'Check build artifacts'.
  * Updated the syntax used for OS and Python matrix definitions in test workflows.

Output files structure:
  * Renamed `version` to `trafficgenVersion` and added `schemaVersion` field to distinguish trafficgen version from maritime-schema version

* Project configuration:
  * pyproject.toml: Removed deprecated pyright setting 'reportShadowedImports'.
  * pyproject.toml: Removed leading carets and trailing slashes from 'exclude' paths.
  * pyproject.toml: Updated required Python version to ">= 3.11" and supported versions to 3.11, 3.12, 3.13, 3.14.
  * pyproject.toml: Removed upper Python version constraint in 'requires-python', changing from ">= 3.11, < 3.15" to ">= 3.11". <br>
    Detailed background and reasoning in this good yet long post by Henry Schreiner:
    https://iscinumpy.dev/post/bound-version-constraints/#pinning-the-python-version-is-special <br>
    TLDR: Placing an upper Python version constraint on a Python package causes more harm than it provides benefits.
    The upper version constraint unnecessarily manifests incompatibility with future Python releases.
    Removing the upper version constraint ensures the package remains installable as Python evolves.
    In the majority of cases, the newer Python version will anyhow be backward-compatible. And in the rare case where your package would really not work with a newer Python version,
    users can at least find a solution manually to resolve the conflict, e.g. by pinning your package to the last version compatible with the environment they install it in.
    That way, we ensure it remains _possible_ for users to find a solution, instead of rendering it impossible forever.
  * pyproject.toml: Removed "manage.py" from the default files to include in source distribution.
  * ruff.toml: Added file-specific ignores for modules named "types.py".
  * .pre-commit-config.yaml: Updated id of ruff to ruff-check.
  * .sourcery.yaml: Updated the lowest supported Python version to '3.11'.

* VS Code settings:
  * Recommended extensions: Removed deprecated IntelliCode and replaced it with GitHub Copilot Chat.
  * Recommended extensions: Removed 'njqdev.vscode-python-typehint' (no longer maintained and now covered by GitHub Copilot).
  * Recommended extensions: Added 'ms-python.debugpy' and 'ms-python.vscode-python-envs'.
  * launch.json: Cleaned up launch configurations and made them uniform.

* Documentation:
  * docs/source/conf.py: Updated copyright year to 2026.
  * README.md: Updated minimum required Python version to 3.11.

* Tests:
  * tests/conftest.py: Slightly restructured to improve git diff view and ease manual inclusion/exclusion of torch-related code.


### Dependencies
* .pre-commit-config.yaml: Updated rev of pre-commit-hooks to v6.0.0
* .pre-commit-config.yaml: Updated rev of ruff-pre-commit to v0.15.1
* Updated to click>=8.3
* Updated to dictio>=0.4.3
* Updated to folium>=0.20.0
* Updated to furo>=2025.12
* Updated to jupyter>=1.1.1
* Updated to matplotlib>=3.10
* Updated to mypy>=1.19.1
* Updated to myst-parser>=5.0
* Updated to numpy>=2.3
* Updated to pandas-stubs>=3.0
* Updated to pre-commit>=4.5
* Updated to pydantic>=2.12
* Updated to pyproj>=3.7
* Updated to pyright>=1.1.408
* Updated to pytest>=9.0
* Updated to pytest-cov>=7.0
* Updated to ruff>=0.15.1
* Updated to sourcery>=1.43.0
* Updated to sphinx>=9.0
* Updated to sphinx-argparse-cli>=1.20.1
* Updated to sphinx-autodoc-typehints>=3.6
* Updated to sphinxcontrib-mermaid>=2.0
* GitHub Workflows:
  * Updated 'checkout' action to v5
  * Updated 'download-artifact' action to v5
  * Updated 'setup-uv' action to v7
  * Updated 'upload-artifact' action to v5


## [0.8.5] - 2026-02-20

### Changed

* Add basic REST API and docker build for easier integration

## [0.8.4] - 2025-11-26

### Changed

* Added sog to each waypoint leg. Updated documentation. Generated new baseline_situations_generated files. Updated types.
* Fixed bug where future position of target ship was used instead of initial position of target ship to check encounter evolvement. Updated documentation to make this functionality clearer.
* Added option to pass in a single input situation .json file, not only a folder.

## [0.8.3] - 2025-10-31

### Changed

* [bug] Fixed sourcery dependency constraint to avoid platform compatibility issues on Linux by constraining to <1.41.

## [0.8.2] - 2025-10-03

### Changed

* [bug] fixed bug that all target ships had id = 10.
* [bug] fixed duplicate -v parameter warning.
* If own ship ID is not given in own_ship.json file, then ID is set to 1. Target ship IDs will follow from own ship ID.
* Better documentation of output files, added links to maritime schema, and improved navigation between related sections.
* Updated documentaion of target ships in input_files.rst

## [0.8.1] - 2025-05-12

### Changed

* Changed first assert in  test_basic_cli() from 0 to 2.

## [0.8.0] - 2025-05-09

### Changed

* vectorTime may now be a single float (exact time) or a list of two floats [from, to]. vectorRange is removed from settings file.
* evolveTime is changed to situationDevelopTime.
* Removed Basemap-package and added pyproj package.
* Small update of ruff.toml file to remove a few warnings.
* Documented the use of Waypoints for own ship.
* camelCasing used for encounter settings; was previously snake_case.
* Added missing info and spelling errors in data/example_situation_input.
* Numpy cross product only allowed for 3D vectors from numpy 2; manually calculating the cross product for 2D vectors in method: calculate_min_vector_length_target_ship.
* Updated documentation; fix spelling errors, add link to github.io, explain Usage, add note on defining python version with uv sync, add note on activating venv.
* Fix build issues; move click and click-log to non-dev dependencies.
* Fix issue with file reading when using non-default paths, and add test for it.

## [0.7.2] - 2025-03-14

### Changed

* Fixed ruff errors which appeared during last nightly build
* Removed code quality from nightly build
* Added -U to for the 'uv sync -U' in readme file

## [0.7.1] - 2025-01-30

### Changed

* Made explicit that Python 3.13 is not yet supported in the pyproject.toml file

## [0.7.0] - 2025-01-22

### Changed

* The python package Maritime Schema is no longer open source, necessary types have been included here to remove the link
* Project updated to use uv package installer
* Documentation has been updated
* Updating workflows
* Removed maxSpeed from the output files generated using the tool

## [0.6.0] - 2024-11-11

### Changed

* Updated to download-artifact@v4  (from download-artifact@v3)

## [0.5.0] - 2024-04-26

### Changed

* removed specific names for target ships. Files generated with target ship 1, 2 etc.
* changed tests. Still need to figure out why some tests "fail" using CLI.

## [0.4.0] - 2024-04-19

### Changed

* possible to have several aypoints for own ship
* fixing pyright error
* beta (relative bearing between osn ship and target ship seen from own ship)
  is not just a number, but could also be a range
* situation length is used when checking if target ship is passing land

## [0.3.0] - 2024-04-10

### Changed

* using types from maritime schema
* lat/lon used instead of north/east
* the generated output files are using "maritime" units: knots and degrees

## [0.2.0] - 2024-01-11

### Changed

* add-basic-code-quality-settings-black-ruff-pyright,
* first-small-round-of-code-improvement
* add-domain-specific-data-types-for-ship-situation-etc-using-pydantic-models,
* activate-remaining-pyright-rules,
* add-github-workflows-to-build-package-and-to-build-and-publish-documentation
* sorting output from os.listdir
* github workflow for release
* removed cyclic import
* length of encounter may be specified by user

## [0.1.0] - 2023-11-08

* First release on PyPI.

<!-- Markdown link & img dfn's -->
[0.6.0]: https://github.com/dnv-opensource/ship-traffic-generator/releases/tag/v0.6.0
[0.5.0]: https://github.com/dnv-opensource/ship-traffic-generator/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/dnv-opensource/ship-traffic-generator/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/dnv-opensource/ship-traffic-generator/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/dnv-opensource/ship-traffic-generator/releases/tag/v0.2.0
