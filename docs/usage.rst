=====
Usage
=====

To use Traffic Generator in a project::

    import trafficgen

To use Traffic Generator as a command line tool for generating traffic situations, write::

    trafficgen gen-situation

The command line tool takes different input options::

    -s, --situations PATH          Folders with situations (default=./baseline_situations_input/)
    -t, --targets PATH             Folder with target configurations (default=./target_ships/)
    -c, --settings PATH            Path to settings file (default=./settings/encounter_settings.json)
    --visualize                    Plot visualization
    --col INTEGER                  Number of columns for plot, may be used with visualize (default=10)
    --row INTEGER                  Number of rows for plot, may be used with visualize (default=6)
    --visualize-situation INTEGER  Plot individual traffic situation, specify INTEGER value
    -o, --output PATH              Output folder (default=None)
    --help                         Show this message and exit.

Example::

    trafficgen gen-situation -s ./data/example_situations_input -o ./data/test_output_1

Situations
~~~~~~~~~~
When generating situations without specifying where the desired situations (``--situation``) are found, the
default path, which is ``default=./baseline_situations_input/``, will be used.

Baseline situations
~~~~~~~~~~~~~~~~~~~
The baseline situations are a set of generic traffic situations covering head-on, overtaking stand-on/give-way
and crossing stand-on/give-way encounters. To cover the combination of encounters for 1, 2 and 3 target ships,
there are in total 55 baseline situations. The input files for generating these situations are found in
``./baseline_situations_input/``

Plotting
~~~~~~~~
Plotting all generated traffic situations
-----------------------------------------
All the generated situations are displayed if using ``--visualize``. This will pop up one or more plot windows,
which show all the traffic situations. The number of colums and rows for the plots (per figure) can be specified by
using ``--col`` and ``--row``, respectively.

Individual plots with map background
------------------------------------
A specific encounter is visualized by using ``--visualize-situation INTEGER``, e.g.::

    trafficgen gen-situation -s ./data/example_situations_input -o ./data/test_output_1 --visualize-situation 2

This will open a browser window/tab with an OpenStreetMap background and the traffic situation
radar plot as an overlay.
Note that the integer needs to be within the range of the number of generated situations,
for example 1 - 12 if you generated 12 situations.
