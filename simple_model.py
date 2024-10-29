from pulp import LpMaximize, LpProblem, LpVariable, lpSum, value, PULP_CBC_CMD
import players_data



def builder_for_diff_configs(i, basic_team, bench_team):
    # Create lists for player attributes
    players = list(players_data.cleaned_data.keys())
    average_FP = {p: players_data.cleaned_data[p]['average_FP'] for p in players}
    position = {p: players_data.cleaned_data[p]['position'] for p in players}
    cost = {p: players_data.cleaned_data[p]['cost'] for p in players}

    # Define the optimization problem
    model = LpProblem("FantasyTeamSelection", LpMaximize)

    # Create binary decision variables for each player in basic and bench teams
    select_basic = LpVariable.dicts("SelectBasic", players, cat='Binary')
    select_bench = LpVariable.dicts("SelectBench", players, cat='Binary')

    # Objective: Maximize weighted average FP (weight of 1 for basic, 0.5 for bench)
    model += (lpSum(select_basic[p] * average_FP[p] for p in players) +
            lpSum(select_bench[p] * 0.5 * average_FP[p] for p in players)), "TotalWeightedFantasyPoints"

    # Constraint: Total cost cannot exceed 94.5
    model += (lpSum(select_basic[p] * cost[p] for p in players) +
            lpSum(select_bench[p] * cost[p] for p in players)) <= 96.2, "CostConstraint"

    # Constraints for team composition
    # Basic team constraints
    model += lpSum(select_basic[p] for p in players if position[p] == 'C') == basic_team["C"] , "CenterBasic"
    model += lpSum(select_basic[p] for p in players if position[p] == 'F') == basic_team["F"] , "ForwardsBasic"
    model += lpSum(select_basic[p] for p in players if position[p] == 'G') == basic_team["G"] , "GuardsBasic"

    # Bench constraints
    model += lpSum(select_bench[p] for p in players if position[p] == 'C') == bench_team["C"] , "CenterBench"
    model += lpSum(select_bench[p] for p in players if position[p] == 'F') == bench_team["F"] , "ForwardsBench"
    model += lpSum(select_bench[p] for p in players if position[p] == 'G') == bench_team["G"] , "GuardBench"

    # Constraint: Total selected players must equal 10
    model += lpSum(select_basic[p] + select_bench[p] for p in players) == 10, "TotalPlayers"

    # Ensure each player can only be selected once across both basic and bench teams
    for p in players:
        model += select_basic[p] + select_bench[p] <= 1, f"UniqueSelection_{p}"

    # Solve the model
    model.solve(PULP_CBC_CMD(msg=False))  # msg=False suppresses output

    # Get the selected players and their details
    selected_basic_team = [p for p in players if select_basic[p].value() == 1]
    selected_bench_team = [p for p in players if select_bench[p].value() == 1]

    # Display results
    print("Selected Basic Team:")
    for p in selected_basic_team:
        print(f"{p}: Position={position[p]}, Average FP={average_FP[p]}, Cost={cost[p]}")

    print("\nSelected Bench Team:")
    for p in selected_bench_team:
        print(f"{p}: Position={position[p]}, Average FP={average_FP[p]}, Cost={cost[p]}")

    print(f"\nTotal Team Cost: {sum(cost[p] for p in selected_basic_team) + sum(cost[p] for p in selected_bench_team)}")
    print(f"Total Team Weighted FP: {sum(average_FP[p] for p in selected_basic_team) + 0.5 * sum(average_FP[p] for p in selected_bench_team)}")
    print(f"configuration system:{i}")
    print("---------------------------------------------------------------------------------")

# Configurations for team compositions
configurations = [
    {"basic": {"C": 2, "F": 2, "G": 2}, "bench": {"C": 0, "F": 2, "G": 2}},
    {"basic": {"C": 1, "F": 3, "G": 2}, "bench": {"C": 1, "F": 1, "G": 2}},
    {"basic": {"C": 2, "F": 1, "G": 3}, "bench": {"C": 0, "F": 3, "G": 1}},
    {"basic": {"C": 1, "F": 2, "G": 3}, "bench": {"C": 1, "F": 2, "G": 1}},
    {"basic": {"C": 1, "F": 1, "G": 4}, "bench": {"C": 1, "F": 3, "G": 0}}
]


# Iterate over each configuration
for i, config in enumerate(configurations, start=1):
    # Accessing basic and bench parts of the configuration
    basic_team = config['basic']
    bench_team = config['bench']
    builder_for_diff_configs(i, basic_team, bench_team)
 