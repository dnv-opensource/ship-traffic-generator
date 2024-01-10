"""Top-level package for Traffic Generator."""
from .ship_traffic_generator import generate_traffic_situations

from .marine_system_simulator import flat2llh
from .marine_system_simulator import llh2flat
from .marine_system_simulator import ssa

from .check_land_crossing import path_crosses_land

from .write_traffic_situation_to_file import write_traffic_situations_to_json_file

from .encounter import generate_encounter
from .encounter import check_encounter_evolvement
from .encounter import find_start_position_target_ship
from .encounter import assign_future_position_to_target_ship
from .encounter import determine_colreg
from .encounter import calculate_relative_bearing
from .encounter import calculate_ship_course
from .encounter import assign_vector_time
from .encounter import assign_speed_to_target_ship
from .encounter import assign_beta
from .encounter import update_position_data_target_ship
from .encounter import update_position_data_own_ship
from .encounter import decide_target_ship

from .plot_traffic_situation import plot_traffic_situations
from .plot_traffic_situation import plot_specific_traffic_situation

from .read_files import read_situation_files
from .read_files import read_own_ship_file
from .read_files import read_target_ship_files
from .read_files import read_encounter_settings_file


from .utils import knot_2_m_pr_min
from .utils import m_pr_min_2_knot
from .utils import m2nm
from .utils import nm_2_m
from .utils import deg_2_rad
from .utils import rad_2_deg
from .utils import convert_angle_minus_180_to_180_to_0_to_360
from .utils import convert_angle_0_to_360_to_minus_180_to_180
from .utils import calculate_position_at_certain_time


__all__ = [
    "knot_2_m_pr_min",
    "m_pr_min_2_knot",
    "m2nm",
    "nm_2_m",
    "deg_2_rad",
    "rad_2_deg",
    "convert_angle_minus_180_to_180_to_0_to_360",
    "convert_angle_0_to_360_to_minus_180_to_180",
    "calculate_position_at_certain_time",
    "flat2llh",
    "llh2flat",
    "ssa",
    "path_crosses_land",
    "write_traffic_situations_to_json_file",
    "generate_encounter",
    "check_encounter_evolvement",
    "find_start_position_target_ship",
    "assign_future_position_to_target_ship",
    "determine_colreg",
    "calculate_relative_bearing",
    "calculate_ship_course",
    "assign_vector_time",
    "assign_speed_to_target_ship",
    "assign_beta",
    "generate_traffic_situations",
    "update_position_data_own_ship",
    "update_position_data_target_ship",
    "decide_target_ship",
    "read_situation_files",
    "read_own_ship_file",
    "read_target_ship_files",
    "read_encounter_settings_file",
    "plot_traffic_situations",
    "plot_specific_traffic_situation",
]
