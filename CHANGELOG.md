# Changelog

All notable changes to the trafficgen project will be documented in this file.<br>
The changelog format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

* Fix build issues; move click and click-log to non-dev dependencies.

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
