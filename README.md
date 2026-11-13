# Tennis Career

Retrieve a player's career matches from Tennis Abstract and plot each match by
the player's age, age difference from the opponent, and result.

## Installation

Requires Python 3.10 or later. Replace OWNER and REPO with the GitHub repository
owner and name.

```bash
python -m pip install git+https://github.com/OWNER/REPO.git
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

# get_career_matches("GastonSanchez") raises ValueError with the supplied name.
```

`get_career_matches` accepts names regardless of capitalization or spaces.
The result is a pandas DataFrame with match date, tournament, opponent, player,
result (`W` or `L`), player age, opponent age, and age difference. Age difference
is player age minus opponent age, so points above zero indicate an older player.
Dates are converted to decimal ages using 365.2425 days per year. Matches with
unusable dates, ages, or outcomes are omitted.

Match data come from [Tennis Abstract](https://www.tennisabstract.com/).
Player names and birth dates come from Jeff Sackmann's
[WTA](https://github.com/JeffSackmann/tennis_wta) and
[ATP](https://github.com/JeffSackmann/tennis_atp) player tables. Retrieving a
career requires access to both data sources. A player needs a known birth
date and a corresponding Tennis Abstract career file.

## Offline tests

After installing the package, run:

```bash
python -m unittest discover -s tests -v
```

The tests replace network downloads with local data. The JavaScript fixtures
retain the relevant columns from the examples supplied in the assignment.

## Personal reflections

Draft for the student to revise before submitting.

The opponent-age column was the most instructive part of this assignment.
In the women's sample, the value is a birth date that needs to be compared
with the match date. In the men's sample, the value is already an age.
Converting both formats to the same DataFrame made it possible to use a
single plotting function. The offline fixtures also made it straightforward
to check the sign of the age difference and the placement of the win and
loss points without relying on the website.
