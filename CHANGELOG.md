# Changelog

All notable changes to the trafficgen project will be documented in this file.<br>
The changelog format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Changed
* GitHub Workflows:
  * _test_future.yml: Updated name of test_future job to 'test315'
  * _test_future.yml: Updated Python specifier in comment to 3.15
  * _test_future.yml: Updated Python specifier in workflow name to py315
  * _test_future.yml: Updated Python version in test_future to 3.15.0-alpha - 3.15.0
  * Added 'name: Checkout code' to uses of 'actions/checkout', for better readability and consistency across workflow files.
  * Added 'name: Download build artifacts' to uses of 'actions/download-artifact', for better readability and consistency across workflow files.
  * Added 'name: Publish to PyPI' to uses of 'pypa/gh-action-pypi-publish', for better readability and consistency across workflow files.
  * Added 'name: Upload build artifacts' to uses of 'actions/upload-artifact', for better readability and consistency across workflow files.
  * Changed 'uv sync --upgrade' to 'uv sync -U'
  * Ensured that actions 'upload-artifact' and 'download-artifact' uniformly specify 'dist' as (file)name for the artifact uploaded (or downloaded, respectively), for consistency across workflow files.
  * pull_request_to_main.yml and nightly_build.yml: Added 'workflow_dispatch:' in selected workflows to allow manual trigger of the workflow.
  * Removed redundant 'Set up Python' steps (no longer needed, as 'uv sync' will automatically install Python if not present).
  * Replaced 'Build source distribution and wheel' with 'Build source distribution and wheels' (plural) in workflow step names.
  * Replaced 'Run twine check' with 'Check build artifacts' in workflow step names, to better reflect the purpose of the step.
  * Updated the syntax used for the OS and Python matrix in test workflows.
* pyproject.toml:
  * pyproject.toml: Removed deprecated pyright setting 'reportShadowedImports'
  * pyproject.toml: Removed leading carets and trailing slashes from 'exclude' paths
  * pyproject.toml: Removed trailing slashes from 'exclude' paths
  * pyproject.toml: Updated required Python version to ">= 3.11"
  * pyproject.toml: Updated supported Python versions to 3.11, 3.12, 3.13, 3.14
  * Removed upper version constraint from required Python version, i.e. changed the "requires-python" field from ">= 3.11, < 3.15" to ">= 3.11". <br>
    Detailed background and reasoning in this good yet long post by Henry Schreiner:
    https://iscinumpy.dev/post/bound-version-constraints/#pinning-the-python-version-is-special <br>
    TLDR: Placing an upper Python version constraint on a Python package causes more harm than it provides benefits.
    The upper version constraint unnecessarily manifests incompatibility with future Python releases.
    Removing the upper version constraint ensures the package remains installable as Python evolves.
    In the majority of cases, the newer Python version will anyhow be backward-compatible. And in the rare case where your package would really not work with a newer Python version,
    users can at least find a solution manually to resolve the conflict, e.g. by pinning your package to the last version compatible with the environment they install it in.
    That way, we ensure it remains _possible_ for users to find a solution, instead of rendering it impossible forever.


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
