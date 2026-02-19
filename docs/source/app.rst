.. _app_api:

Application API
===============

This page documents the Flask REST API implemented in ``src/trafficgen/app.py``.

Available endpoints
-------------------

* ``GET /api/health``
* ``GET /api/version``
* ``GET /api/settings/default``
* ``GET /api/baseline/{situation_id}``
* ``POST /api/generate``

OpenAPI specification
---------------------

The OpenAPI 3.0 specification for the current app is available below:

.. literalinclude:: openapi.yaml
   :language: yaml
