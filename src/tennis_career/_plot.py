"""Plot each match by player age, age difference, and outcome."""

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.ticker import MultipleLocator
from pandas import DataFrame


def _style_axes(axes):
    axes.xaxis.tick_top()
    axes.xaxis.set_label_position("top")
    axes.xaxis.set_major_locator(MultipleLocator(2))
    axes.yaxis.set_major_locator(MultipleLocator(10))
    axes.set_axisbelow(True)
    axes.grid(color="#e5e5e5")
    axes.axhline(0, color="#8c8c8c", linewidth=0.8)
    axes.spines[:].set_visible(False)
    axes.tick_params(length=0)


def plot_career_matches(matches: DataFrame) -> Axes:
    """Plot the career matches and return the Matplotlib axes."""
    figure, axes = plt.subplots(figsize=(11, 7), layout="constrained")
    for result, label, color in [("W", "Match won", "#35C5EB"), ("L", "Match lost", "#993399")]:
        subset = matches.loc[matches["result"].eq(result)]
        axes.scatter(subset["player_age"], subset["age_difference"],
                     s=14, alpha=0.8, color=color, label=label, linewidths=0,
                     zorder=3)
    _style_axes(axes)
    axes.set(xlabel="Player age at match (years)",
             ylabel="Player age − opponent age (years)")
    if len(matches):
        figure.suptitle(f"{matches['player'].iat[0]} Career Matches",
                        x=0.02, ha="left", fontweight="bold")
    axes.legend(loc="lower center", bbox_to_anchor=(0.5, 1.12),
                ncol=2, frameon=False)
    return axes
