=======
History
=======


0.4.0 (2024-04-19)
------------------

Changed

* possible to have several aypoints for own ship
* fixing pyright error
* beta (relative bearing between osn ship and target ship seen from own ship)
  is not just a number, but could also be a range
* situation length is used when checking if target ship is passing land


0.3.0 (2024-04-10)
------------------

Changed

* using types from maritime schema
* lat/lon used instead of north/east
* the generated output files are using "maritime" units: knots and degrees


0.2.0 (2024-01-11)
------------------

Changed

* add-basic-code-quality-settings-black-ruff-pyright,
* first-small-round-of-code-improvement
* add-domain-specific-data-types-for-ship-situation-etc-using-pydantic-models,
* activate-remaining-pyright-rules,
* add-github-workflows-to-build-package-and-to-build-and-publish-documentation
* sorting output from os.listdir
* github workflow for release
* removed cyclic import
* length of encounter may be specified by user


0.1.0 (2023-11-08)
------------------

* First release on PyPI.
