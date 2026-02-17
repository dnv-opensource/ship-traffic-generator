API Reference
=============

.. toctree::
   :maxdepth: 4

   trafficgen


HTTP Endpoint: /api/generate
============================

Method
------

``POST /api/generate``

Description
-----------

Generates one or more traffic situations from a JSON payload.

Request JSON
------------

Top-level payload object:

.. code-block:: json

    {
       "trafficSituations": { "...": "..." } | [{ "...": "..." }],
       "ownShipStatic": { "...": "..." },
       "targetShipsStatic": [{ "...": "..." }],
       "encounterSettings": { "...": "..." }
    }

Required top-level fields:

* ``trafficSituations``
* ``ownShipStatic``
* ``targetShipsStatic``
* ``encounterSettings``

``trafficSituations`` supports either:

* a single situation object, or
* a list of situation objects.

Situation object (minimum shape):

.. code-block:: json

    {
       "title": "Head-on example",
       "description": "Single target encounter",
       "numSituations": 1,
       "ownShip": {
          "initial": {
             "position": { "lat": 58.763449, "lon": 10.490654 },
             "sog": 10.0,
             "cog": 0.0
          }
       },
       "encounters": [
          {
             "desiredEncounterType": "head-on",
             "vectorTime": 20.0
          }
       ]
    }

Notes:

* CamelCase keys are accepted (for example ``trafficSituations``, ``ownShipStatic``, ``disableLandCheck``).
* Additional fields are allowed by the schema where configured in the model definitions.

Successful response (200)
-------------------------

Returns a JSON array of generated traffic situations.

.. code-block:: json

    [
       {
          "version": "...",
          "title": "...",
          "description": "...",
          "startTime": null,
          "ownShip": { "...": "..." },
          "targetShips": [{ "...": "..." }]
       }
    ]

Response keys are emitted in camelCase (alias form), for example ``startTime``, ``ownShip`` and ``targetShips``.

Error responses
---------------

* ``400 Bad Request``: Invalid or missing JSON body.

   .. code-block:: json

       {
          "error": "Invalid or missing JSON request body or content-type header."
       }

* ``422 Unprocessable Entity``: JSON body is present but fails schema validation.

   .. code-block:: json

       {
          "errors": [
             {
                "type": "...",
                "loc": ["..."],
                "msg": "...",
                "input": "..."
             }
          ]
       }
