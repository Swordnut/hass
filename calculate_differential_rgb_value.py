# script by Swordnut
# ===================================================
# What this script does:
# - Calculates a color based on the difference between two numbers
#   (for example: temperature in two rooms).
# - The colour is returned in one of these formats:
#   - RGB (Red, Green, Blue)
#   - HS (Hue and Saturation)
#   - Color Temperature (in mireds)
#
# How to use it:
# Use action blueprint swordnut_light_color_from_state_diff
# https://www.github.com/Swordnut/hass
# create a new empty script in the home assistant UI and paste the code above into it

# OR
# - You can call this script from an automation or another script.
# - You must provide two values to compare (for example: two temperature sensors).
#
# Example:
# service: pyscript.calculate_differential_color_value
# data:
#   state1: "{{ states('sensor.kitchen_temperature') | float(0) }}"
#   state2: "{{ states('sensor.lounge_temperature') | float(0) }}"
#   max_range: 10          # range of difference between values 
#   color_range_min: 240   # Hue for lowest value (e.g. blue)
#   color_range_max: 0     # Hue for highest value (e.g. red)
#   color_temp_min: int = 500,
#   color_temp_max: int = 153,
#   use_color_temp: false,
#   use_hue_sat: false,
#   range_type: "symmetric"
#
# Notes:
# - max_range: This sets the size of the range from lowest to highest difference.
#   For example, if max_range is 10:
#     - symmetric: values from -10 to +10 (around the baseline)
#     - positive: values from 0 to +10 only
#
# - color_range_min / color_range_max:
#     These are hue values from 0 to 360:
#     - 0 = red
#     - 60 = yellow
#     - 120 = green
#     - 180 = cyan
#     - 240 = blue
#     - 300 = magenta
#
#     Example:
#       - 240 to 0 = blue to red
#       - 0 to 120 = red to green
#
# Output:
# - This script returns a dictionary with:
#     - type: "rgb", "hs", or "color_temp"
#     - value: the corresponding colour in a format you can use with light.turn_on
#
# No input_text helpers are needed. The returned value can be used directly in your automation.
# ===================================================
from PIL import ImageColor

@service
def calculate_differential_rgb_value(
    state1: float,
    state2: float,
    max_range: float = 10,
    color_range_min: int = 240,
    color_range_max: int = 0,
    color_temp_min: int = 500,
    color_temp_max: int = 153,
    use_color_temp: bool = False,
    use_hue_sat: bool = False,
    range_type: str = "symmetric"
):
    """
    Returns a dict with:
    - type: one of "color_temp", "hs", or "rgb"
    - value: appropriate color setting (int or list)
    """

    diff = state2 - state1

    if range_type == "positive":
        clipped = max(min(diff, max_range), 0)
        scaled = clipped / max_range if max_range != 0 else 0
    else:  # symmetric
        clipped = max(min(diff, max_range), -max_range)
        scaled = (clipped + max_range) / (2 * max_range) if max_range != 0 else 0.5

    if use_color_temp:
        color_temp = int((1 - scaled) * color_temp_min + scaled * color_temp_max)
        log.info(f"[pyscript] Δ={diff:.2f} (clipped: {clipped}) → color_temp: {color_temp} mireds")
        return {
            "type": "color_temp",
            "value": color_temp
        }

    hue_deg = (1 - scaled) * color_range_min + scaled * color_range_max
    hsv_str = f"hsv({int(hue_deg)}, 100%, 100%)"

    if use_hue_sat:
        hs = [round(hue_deg), 100]
        log.info(f"[pyscript] Δ={diff:.2f} (clipped: {clipped}) → HS: {hs}")
        return {
            "type": "hs",
            "value": hs
        }
    else:
        rgb = ImageColor.getrgb(hsv_str)
        log.info(f"[pyscript] Δ={diff:.2f} (clipped: {clipped}) → RGB: {rgb}")
        return {
            "type": "rgb",
            "value": list(rgb)
        }
