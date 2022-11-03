# Simulate the FIFA World Cup tournament, including Groups phase

import csv
import sys
import random
import operator
from math import factorial
from itertools import groupby

# Number of simluations to run
N = 10000


def main():

    # Ensure correct usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python tournament.py FILENAME")

    # Store name of the file containing rankings
    filename = sys.argv[1]

    # List to store teams data
    teams = []

    # Open CSV file
    with open(filename) as csvfile:
        # Uning DictReared instead of reader returns a dict
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Append rows to teams list
            row["rating"] = int(row["rating"])
            teams.append(row)

    # Split teams by group
    groups = {}
    for k, v in groupby(teams, lambda x: x['group']):
        groups[k] = list(v)

    # print(groups)

    # List to store knock off phase teams
    knockoff_teams = []

    # Keep index of Group for team position in knockoff teams list (list must be in right order)
    group_index = 0
    knockoff_teams = list(range(int(len(teams) / 2)))

    # Simulate N groups phase and select most likely 1st and 2nd of each group
    for group in groups:
        group_counts = {}
        for i in range(N):
            first_place = simulate_group(groups[group])[0]
            second_place = simulate_group(groups[group])[1]
            # Add 1st and 2nd places to counts dict
            if first_place in group_counts:
                group_counts[first_place] += 1
            else:
                group_counts[first_place] = 1
            if second_place in group_counts:
                group_counts[second_place] += 1
            else:
                group_counts[second_place] = 1

        top_two = sorted(
            group_counts, key=lambda team: group_counts[team], reverse=True)[0:2]
        # print(top_two)

        # Order of teams in knockoff_teams list must be:
        # list =  [1A, 2B, 1B, 2A, 1C, 2D, 1D, 2C, 1E, 2F, 1F, 2E, 1G, 2H, 1H, 2G]
        # index    0   1   2   3   4   5   6   7   8   9   10  11  12  13  14  15
        # gr_i*2 = 0   2   2   0   4   6   6   4   8   10  10  8   12  14  14  12
        # group_i  0   1   1   0   2   3   3   2   4   5   5   4   6   7   7   6
        # The first place location in the list always matches group_index * 2
        # For the second place, the easy solution is to store the correct locations in a list
        loc_second = [3, 1, 7, 5, 11, 9, 15, 13]

        for i in range(len(teams)):
            if teams[i]['team'] == top_two[0]:
                knockoff_teams[group_index*2] = teams[i]
            elif teams[i]['team'] == top_two[1]:
                knockoff_teams[loc_second[group_index]] = teams[i]

        # Increase index for next group
        group_index += 1

    # print(knockoff_teams)

    knockoff_counts = {}
    # Simulate N knock-off phases and keep track of win counts
    for i in range(N):
        winner = simulate_tournament(knockoff_teams)
        # Add winner to counts dict
        if winner in knockoff_counts:
            knockoff_counts[winner] += 1
        else:
            knockoff_counts[winner] = 1

    # Print each team's chances of winning, according to simulation
    for team in sorted(knockoff_counts, key=lambda team: knockoff_counts[team], reverse=True):
        print(f"{team}: {knockoff_counts[team] * 100 / N:.1f}% chance of winning")


def simulate_game(team1, team2):
    """Simulate a game. Return True if team1 wins, False otherwise."""
    rating1 = team1["rating"]
    rating2 = team2["rating"]
    probability = 1 / (1 + 10 ** ((rating2 - rating1) / 600))
    return random.random() < probability


def simulate_group(teams):
    # Simulates group phase matches returning 1st and 2nd places
    # Note: there are no ties in this simulation. Rating is used as tie breaker
    # points = {}
    for i in range(len(teams)):
        teams[i]['points'] = 0

    # Simulate all combinations for list of teams
    for i in range(len(teams)):
        for j in range(i+1, len(teams)):
            if simulate_game(teams[i], teams[j]):
                # print(f"{teams[i]['team']} vs {teams[j]['team']}")
                teams[i]['points'] += 3
            else:
                teams[j]['points'] += 3

    # print(teams)

    points_1st = 0
    points_2nd = 0
    first_place = {}
    second_place = {}

    # Iterate over list of teams for find 1st and 2nd places
    # Rating is used as tie breaker
    for team in teams:
        if team['points'] > points_1st:
            second_place = first_place
            points_2nd = points_1st
            first_place = team
            points_1st = team['points']
        elif team['points'] == points_1st and first_place != {}:
            if team['rating'] > first_place['rating']:
                second_place = first_place
                points_2nd = points_1st
                first_place = team
            else:
                second_place = team
                points_2nd = team['points']
        elif team['points'] > points_2nd:
            second_place = team
            points_2nd = team['points']
        elif team['points'] == points_2nd and second_place != {}:
            if team['rating'] > second_place['rating']:
                second_place = team

    # print(f"Results {first_place}, {second_place}")
    return [first_place['team'], second_place['team']]


def simulate_round(teams):
    """Simulate a round. Return a list of winning teams."""
    winners = []

    # Simulate games for all pairs of teams
    for i in range(0, len(teams), 2):
        if simulate_game(teams[i], teams[i + 1]):
            winners.append(teams[i])
        else:
            winners.append(teams[i + 1])

    return winners


def simulate_tournament(teams):
    """Simulate a tournament. Return name of winning team."""
    # Continue to simulate rounds until only one is left
    while len(teams) > 1:
        teams = simulate_round(teams)
    return teams[0]['team']


if __name__ == "__main__":
    main()
