# Helper script by Swordnut 
# ===================================================
# What it does - 
# outputs RGB values according to the difference between two numeric entity states
# allows customisation of the range of spectrum to be used 
#   use a spectrum that goes from red to blue or from green to magenta etc
#   make sure the values you get from your inputs are always represented
# ===================================================
# How to use - 
# an action bluebrint is avaialable for setting a light to a colour using the script that gives methods of setting the type of range (+/- or just +) as well as brightness, delay, RGB/HS format etc
# Call from an automation, passing the values of two numeric entitiy states. 
#   1st is the base, 2nd is the comparison
#   e.g., 
#   action: pyscript.calculate_differential_rgb_value
#     data:
#       state1: "{{ states('type.entity_name_1') | float(0) }}"
#       state2: "{{ states('type.entity_name_2') | float(0) }}"
#       max_range: 10
#       color_range_min: 240
#       color_range_max: 0

# Set MAX_RANGE to the desired range for your entity state
#   MAX_RANGE value is plus and minus from neutral/baseline
#   e.g., 10 will be plus or minus 10, a total range of 20
# Set COLOR_RANGE_LOW and COLOR_RANGE_HIGH using values 0 - 360
#   these defined the spectrum of colors mapped to the min/max value of the difference between your entity states (diff)
#   0= red 60=yellow 120=green 180=cyan 240=blue 300=magenta
#   e.g., setting low 0 high 240 will result in a spectrum from red at the bottom to blue at the top. 240 low and 0 high will
#   result in blue at the bottom and red at the top


from PIL import ImageColor
# native to pyscript, no other import handling needed

MAX_RANGE = 10
COLOR_RANGE_LOW = 240
COLOR_RANGE_HIGH = 0

@service
def calculate_indicator_rgb(state1: float, state2: float):
    diff = state2 - state1

    # Clamp to range. ensures values do not exceed max range 
    clipped = max(min(diff, MAX_RANGE), -MAX_RANGE)

    # Map clipped diff to hue (240° = blue, 120° = green, 0° = red)
    # -MAX_RANGE → 240, 0 → 120, +MAX_RANGE → 0
    scaled = (clipped + MAX_RANGE) / (2 * MAX_RANGE)
    hue_deg = (1 - scaled) * COLOR_RANGE_LOW

    # Build HSV string and convert to RGB using PIL
    hsv_str = f"hsv({int(hue_deg)}, 100%, 100%)"
    rgb = ImageColor.getrgb(hsv_str)

    # Set state as comma-separated string for YAML automation
    rgb_str = f"{rgb[0]},{rgb[1]},{rgb[2]}"
    state.set("input_text.indicator_rgb_output", rgb_str)
    log.info(f"Set RGB: {rgb_str} from ΔT = {diff:.2f}°C (hue = {hue_deg:.1f}°)")
