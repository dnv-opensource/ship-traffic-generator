# pyright: reportMissingParameterType=false
# pyright: reportUnknownParameterType=false
# The click package is unfortunately not typed. Hence the following pyright exemption.
# pyright: reportUnknownMemberType=false
"""CLI for trafficgen package."""

import contextlib
import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import click
import click_log

from trafficgen.plot_traffic_situation import plot_specific_traffic_situation, plot_traffic_situations
from trafficgen.read_files import read_encounter_settings_file
from trafficgen.ship_traffic_generator import generate_traffic_situations
from trafficgen.write_traffic_situation_to_file import write_traffic_situations_to_json_file

if TYPE_CHECKING:
    from trafficgen.types import EncounterSettings

logger = logging.getLogger(__name__)
_ = click_log.basic_config(logger)

# if you change the below defaults, then remember to change the description of
# the default values in below @click.option descriptions,
# and docs/usage.rst
default_data_path: Path = Path(__file__).parent.parent.parent / "data"
situation_folder: Path = default_data_path / "baseline_situations_input"
own_ship_file: Path = default_data_path / "own_ship/own_ship.json"
target_ship_folder: Path = default_data_path / "target_ships"
settings_file: Path = Path(__file__).parent / "settings" / "encounter_settings.json"
output_folder: Path = default_data_path / "test_output"


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click_log.simple_verbosity_option(logger)
def main(args=None):  # noqa: ANN001, ANN201, ARG001
    """Entry point for console script as configured in pyproject.toml.

    Runs the command line interface and parses arguments and options entered on the console.
    """
    return 0


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "-s",
    "--situations",
    help="Path to file (.json) or folder with situation input files",
    type=click.Path(exists=True),
    default=situation_folder,
    show_default=True,
)
@click.option(
    "-os",
    "--own_ship",
    help="Path to own ship file",
    type=click.Path(exists=True),
    default=own_ship_file,
    show_default=True,
)
@click.option(
    "-t",
    "--targets",
    help="Folder with target configurations",
    type=click.Path(exists=True),
    default=target_ship_folder,
    show_default=True,
)
@click.option(
    "-o",
    "--output",
    help="Output folder",
    type=click.Path(exists=False),
    default=None,
    show_default=True,
)
@click.option(
    "-c",
    "--settings",
    help="Path to settings file)",
    type=click.Path(exists=True),
    default=settings_file,
    show_default=True,
)
@click.option(
    "-v",
    "--visualize",
    is_flag=True,
    default=False,
    show_default=True,
    help="Plot visualization",
)
@click.option(
    "--col",
    default=6,
    show_default=True,
    help="Number of columns for plot, may be used together with --visualize",
)
@click.option(
    "--row",
    default=5,
    show_default=True,
    help="Number of rows for plot, may be used together with --visualize",
)
@click.option(
    "--visualize-situation",
    type=int,
    help="Plot one individual traffic situation, specify an INTEGER value larger than 0. [OPTIONAL, no default]",
)
@click.option(
    "--ownship-coordinate",
    help="Specify the ownship start coordinate as 'lat,lon' in decimal degrees. If specified, this takes priority over what is specified in the situation file as initial ownship position, and everything will be generated relative to this coordinate. [OPTIONAL, no default]",
    type=str,
)

def gen_situation(
    situations: str,
    own_ship: str,
    targets: str,
    settings: str,
    col: int,
    row: int,
    visualize_situation: int,
    output: str | None,
    visualize: bool,  # noqa: FBT001
    ownship_coordinate: str | None,
) -> None:
    r"""Console script for trafficgen.
    Example:

    trafficgen gen-situation -s ./data/example_situations_input
    -o ./data/test_output_1.
    """  # noqa: D205
    click.echo("Generating traffic situations")
    generated_traffic_situations = generate_traffic_situations(
        situation_folder=Path(situations),
        own_ship_file=Path(own_ship),
        target_ship_folder=Path(targets),
        settings_file=Path(settings),
        ownship_coordinate=ownship_coordinate,
    )

    encounter_settings: EncounterSettings = read_encounter_settings_file(settings_file)
    if visualize:
        click.echo("Plotting traffic situations. Close the plot window to continue.")
        plot_traffic_situations(generated_traffic_situations, col, row, encounter_settings)

    # visualize_situation has no default, this is done on purpose,
    # so it can safely be ignored by users without generating an error msg,
    # and so that if a user specifies a value of zero or negative number,
    # the user will get an error message.

    # Ignore TypeError
    # TypeError is thrown in case a value for a parameter is not defined.
    # In such case, though, we safely ignore that parameter :)
    with contextlib.suppress(TypeError):
        if visualize_situation > 0:
            click.echo("Plotting a specific traffic situation")
            plot_specific_traffic_situation(generated_traffic_situations, visualize_situation, encounter_settings)
        else:
            click.echo("Invalid traffic situation number specified, not creating map plot. See --help for more info.")
    if output is not None:
        click.echo("Writing traffic situations to files")
        write_traffic_situations_to_json_file(generated_traffic_situations, write_folder=Path(output))
    else:
        click.echo(
            "No output folder specified, not writing traffic situations to files.\n"
            "You can use -o to specify the output folder."
        )


main.add_command(gen_situation)

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
