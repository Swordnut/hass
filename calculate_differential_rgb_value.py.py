# Helper script by Swordnut 
# ===================================================
# What it does - 
# Calculates a color value based on the difference between two numeric inputs.
# Supports RGB, HS, and color_temp outputs. Range type can be symmetric (±max) or positive (0→max).
# ===================================================
# How to use - 
# Call from an automation, passing the values of your 
#   two entitiy states. 
#   1st is the base, 2nd is the comparison
#   e.g., 
#   action: pyscript.calculate_differential_rgb_value
#     data:
#       state1: "{{ states('type.entity_name_1') | float(0) }}"
#       state2: "{{ states('type.entity_name_2') | float(0) }}"
#       max_range: 10
#       color_range_min: 240
#       color_range_max: 0
#       use_color_temp: bool = False
#       range_type: str = "symmetric"
#
# Set MAX_RANGE to the desired range for your entity state
#   MAX_RANGE value is plus and minus from neutral/baseline
#   e.g., 10 will be plus or minus 10, a total range of 20
# Set color_range_min and color_range_max using values 0 - 360
#   these defined the spectrum of colors mapped to the min/max 
#   value of the difference between your entity states (diff)
#   0= red 60=yellow 120=green 180=cyan 240=blue 300=magenta
#   e.g., setting low 0 high 240 will result in a spectrum from
#   red at the bottom to blue at the top. 240 low and 0 high will
#   result in blue at the bottom and red at the top


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
    use_color_temp: bool = False
    range_type: str = "symmetric"
):

    diff = state2 - state1

    if range_type == "positive":
        clipped = max(min(diff, max_range), 0)
        scaled = clipped / max_range if max_range != 0 else 0
    else:  # symmetric
        clipped = max(min(diff, max_range), -max_range)
        scaled = (clipped + max_range) / (2 * max_range) if max_range != 0 else 0.5

    if use_color_temp:
        color_temp = int((1 - scaled) * color_temp_min + scaled * color_temp_max)
        state.set("input_text.indicator_color_temp_output", str(color_temp))
        log.info(
            f"[pyscript] Δ={diff:.2f} (clipped: {clipped}) → color_temp: {color_temp} mireds"
        )
    else:
        hue_deg = (1 - scaled) * color_range_min + scaled * color_range_max
        hsv_str = f"hsv({int(hue_deg)}, 100%, 100%)"
        rgb = ImageColor.getrgb(hsv_str)
        rgb_str = f"{rgb[0]},{rgb[1]},{rgb[2]}"
        hs_str = f"{round(hue_deg)},100"

        state.set("input_text.indicator_rgb_output", rgb_str)
        state.set("input_text.indicator_hs_output", hs_str)

        log.info(
            f"[pyscript] Δ={diff:.2f} (clipped: {clipped}) "
            f"→ hue={hue_deg:.1f}° → RGB: {rgb_str} / HS: {hs_str}"
        )
