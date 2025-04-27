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
    -v, --visualize                Plot visualization
    --col INTEGER                  Number of columns for plot, may be used with visualize (default=10)
    --row INTEGER                  Number of rows for plot, may be used with visualize (default=6)
    --visualize-situation INTEGER  Plot individual traffic situation, specify INTEGER value
    -o, --output PATH              Output folder (default=None)
    --help                         Show this message and exit.

Example::

    trafficgen gen-situation -s ./data/example_situations_input -o ./data/test_output

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
All the generated situations are displayed if using ``-v`` or ``--visualize``. This will pop up one or more plot windows,
which show all the traffic situations. The number of colums and rows for the plots (per figure) can be specified by
using ``--col`` and ``--row``, respectively.

Individual plots with map background
------------------------------------
A specific encounter is visualized by using ``--visualize-situation INTEGER``, e.g.::

    trafficgen gen-situation -s ./data/example_situations_input -o ./data/test_output --visualize-situation 2

This will open a browser window/tab with an OpenStreetMap background and the traffic situation
radar plot as an overlay.
Note that the integer needs to be within the range of the number of generated situations,
for example 1 - 12 if you generated 12 situations.


Scaling encounters
~~~~~~~~~~~~~~~~~~
As you may have understood from the documentation of the input files, the scale of encounters
(i.e. how many meters or nautical miles does the scenario play out over)
is determined by time-based parameters.
If you want to change the range that the scenario plays out over,
you will need to change the following parameters:

* in the input situation file: change `vectorTime`: the time at which the target vessel will be in the encounter circle of the ownship. (Note; the encounter circle radius is defined by the maxMeetingDistance in `encounter_settings.json`.)
* in `encounter_settings.json`: change `vectorRange` (the range within which `vectorTime` is varied, min), `situationLength` (total duration of situation, min).

By default, the ownship will travel in a straight line from its start position, defined in the input file, to a position that is `situationLength` minutes into the future.
It is possible to specify waypoints for the own ship in the input file, which will be used instead of the straight line. If defining
waypoints, the first waypoint shallbe the same as the initil position of the ownship.
The ownship will then travel to the first waypoint, and then to the second waypoint, and so on.

For the target ship, the future position of 'meeting' is calculated based on the ownship initial position, the vector_time, and the maximum meeting distance.
At time vectorTime, the target ship will be within maxMeetingDistance radius of the ownship position (at vector time).

If vectorTime is not set, then the ship traffic generator will randomly sample a vector time within the range of vectorRange.

> **Note:** When generating a specific traffic situation, e.g. crossing give-way, this specific situation should also have been a
crossing give-way situation at some time in the past, e.g. 10 minutes ago. This is specified by the evolveTime` parameter.
This ensures that the COLREG encounter is the same type also for some time (evolve_time) before the actual encounter is started.
