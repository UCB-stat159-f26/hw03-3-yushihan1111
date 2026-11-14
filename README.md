# Tennis Career

Retrieve a player's career matches from Tennis Abstract and plot each match by the player's age, age difference from the opponent, and result.

## Installation

Requires Python 3.10 or later and access to the private course repository.

```bash
python -m pip install git+https://github.com/UCB-stat159-f26/hw03-3-yushihan1111.git
```

To install from a local checkout, run `python -m pip install .` in the repository.

## Usage

```python
import matplotlib.pyplot as plt
from tennis_career import get_career_matches, plot_career_matches

serena = get_career_matches("serena williams")
plot_career_matches(serena)

rafa = get_career_matches("Rafael Nadal")
axes = plot_career_matches(rafa)
axes.figure.savefig("nadal-career.png", dpi=150)

plt.show()
```

`get_career_matches()` accepts spaced names such as `Serena Williams` and compact names such as `SerenaWilliams`. Use spaces when typing an entirely lowercase name. An unknown player such as `GastonSanchez` raises a `ValueError` that asks the user to check the spelling and use the player's full name.

The function returns a pandas DataFrame with the match date, tournament, opponent, player, result (`W` or `L`), player age, opponent age, and age difference. Ages are expressed in decimal years using 365.2425 days per year. The age difference is the player's age minus the opponent's age, so positive values mean the player is older. Matches with unusable dates, ages, or outcomes are omitted.

Match data and player birth dates come from [Tennis Abstract](https://www.tennisabstract.com/). Retrieving a career requires network access and a player profile with a birth date and a career match file.

## Offline tests

After installing the package, run this command from the repository root:

```bash
python -m unittest discover -s tests -v
```

The tests replace network downloads with local fixtures based on the assignment's examples.

## Personal reflections

The number I remember most from this assignment is −4.68. It is the age difference in Serena's first match in the dataset, against Anne Miller. I can check the sign without looking at the code: Serena was younger, so the number should be negative. That small check helped me understand what each point in the plot actually means.

In HW2, I only had to make the code work for Serena. When I moved on to Nadal, I found that the same column meant something different. Serena's file gives the opponent's birth date, so I have to calculate the opponent's age on the match date. Nadal's file already gives the opponent's age. Once both formats produce the same columns, I can use one plotting function for both players. I was glad to see that all 1,038 Serena matches still lined up with my HW2 data after that change. Comparing the rows gave me more confidence than just seeing a familiar-looking plot.