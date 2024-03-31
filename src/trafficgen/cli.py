# pyright: reportMissingParameterType=false
# pyright: reportUnknownParameterType=false
# The click package is unfortunately not typed. Hence the following pyright exemption.
# pyright: reportUnknownMemberType=false
"""CLI for trafficgen package."""

import contextlib
import logging
import sys
from pathlib import Path

import click
import click_log

from trafficgen.plot_traffic_situation import plot_specific_traffic_situation, plot_traffic_situations
from trafficgen.ship_traffic_generator import generate_traffic_situations
from trafficgen.write_traffic_situation_to_file import write_traffic_situations_to_json_file

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


@click.group()
@click_log.simple_verbosity_option(logger)
def main(args=None):
    """Entry point for console script as configured in pyproject.toml.

    Runs the command line interface and parses arguments and options entered on the console.
    """
    return 0


@click.command()
@click_log.simple_verbosity_option(logger)
@click.option(
    "-s",
    "--situations",
    help="Path to folder with situations (default=./baseline_situations_input/)",
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
    help="Plot individual traffic situation, specify an INTEGER value larger than 0.",
)
def gen_situation(
    situations,
    own_ship,
    targets,
    settings,
    visualize,
    col,
    row,
    visualize_situation,
    output,
):
    r"""Console script for trafficgen.
    Example: \n
    trafficgen gen-situation -s ./data/example_situations_input
    -o ./data/test_output_1.
    """
    click.echo("Generating traffic situations")
    generated_traffic_situations = generate_traffic_situations(
        situation_folder=Path(situations),
        own_ship_file=Path(own_ship),
        target_ship_folder=Path(targets),
        settings_file=Path(settings),
    )

    if visualize:
        click.echo("Plotting traffic situations")
        plot_traffic_situations(generated_traffic_situations, col, row, settings)

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
            plot_specific_traffic_situation(generated_traffic_situations, visualize_situation, settings)
        else:
            click.echo(
                "Invalid traffic situation number specified, not creating map plot. See --help for more info."
            )
    if output is not None:
        click.echo("Writing traffic situations to files")
        write_traffic_situations_to_json_file(generated_traffic_situations, write_folder=Path(output))


main.add_command(gen_situation)

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
