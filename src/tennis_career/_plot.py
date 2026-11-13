"""Plot each match by player age, age difference, and outcome."""

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from pandas import DataFrame


def plot_career_matches(matches: DataFrame) -> Axes:
    """Plot the career matches and return the Matplotlib axes."""
    figure, axes = plt.subplots(figsize=(10, 5))
    for result, label, color in [("W", "Win", "#168477"), ("L", "Loss", "#c64b46")]:
        subset = matches.loc[matches["result"].eq(result)]
        axes.scatter(subset["player_age"], subset["age_difference"],
                     s=18, alpha=0.65, color=color, label=label, linewidths=0)
    axes.axhline(0, color="#606060", linewidth=0.8, zorder=0)
    axes.set(xlabel="Player age (years)",
             ylabel="Player age − opponent age (years)")
    if len(matches):
        axes.set_title(matches["player"].iat[0], loc="left")
    axes.spines[["top", "right"]].set_visible(False)
    axes.legend(frameon=False)
    figure.tight_layout()
    return axes
