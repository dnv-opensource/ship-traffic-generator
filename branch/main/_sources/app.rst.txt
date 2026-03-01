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

Localhost TLS (HTTPS)
---------------------

The API enforces HTTPS by default (see ``TRAFFICGEN_ENFORCE_HTTPS`` in ``src/trafficgen/app.py``).
For local testing, start Flask with a local certificate.

Generate certificate and key:

.. code-block:: sh

   openssl req -x509 -newkey rsa:2048 -sha256 -nodes \
     -keyout key.pem -out cert.pem -days 365 \
     -subj "/CN=localhost"

Run the API with TLS:

.. code-block:: sh

   uv run flask --app src/trafficgen/app.py run --host 0.0.0.0 --port 5000 --cert cert.pem --key key.pem


If you use a self-signed certificate that is not trusted by your client,
you may need to add your certificate to trust store (recommended) or use
client-specific insecure flags for local testing only.

OpenAPI specification
---------------------

The OpenAPI 3.0 specification for the current app is available below:

.. literalinclude:: openapi.yaml
   :language: yaml
