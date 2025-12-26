MATPLOTLIB_FONT = "DejaVu Sans"

# Shared font dicts for Matplotlib text elements
FONT_DEFAULT = {"fontname": MATPLOTLIB_FONT, "size": "11"}
FONT_LIGHT = {"fontname": MATPLOTLIB_FONT, "size": "10", "weight": "light"}
FONT_TITLE = {"fontname": MATPLOTLIB_FONT, "size": "12", "weight": "bold"}
FONT_SMALL = {"fontname": MATPLOTLIB_FONT, "size": "7.5", "weight": "light"}
FONT_BOLD = {"fontname": MATPLOTLIB_FONT, "size": "11", "weight": "bold"}


def apply_matplotlib_defaults():
    """Use a bundled Matplotlib font to avoid missing font warnings."""
    import matplotlib.pyplot as plt

    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": [MATPLOTLIB_FONT],
            "font.size": 11,
        }
    )
