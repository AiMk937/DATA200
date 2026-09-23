# -------------------------------------------------------------
# Integer Data Analyzer
#
# This program:
# 1. Accepts space-separated integers from the user.
# 2. Converts the input into integer values.
# 3. Finds:
#       - Count
#       - Minimum
#       - Maximum
#       - Sum
#       - Average
#       - Duplicate values
#       - Frequency of each value
# 4. Handles invalid input using exceptions.
# -------------------------------------------------------------


# -------------------------------------------------------------
# Function: parse_values
#
# Purpose:
# Convert user input from a string into a list of integers.
#
# Example:
# Input:
#     "10 20 30"
#
# Output:
#     [10, 20, 30]
# -------------------------------------------------------------
def parse_values(text):

    # Split the input string wherever whitespace occurs.
    tokens = text.split()

    # If there is nothing to parse, that is an invalid input.
    if not tokens:
        raise ValueError("No integers were entered.")

    values = []
    for token in tokens:
        try:
            values.append(int(token))
        except ValueError:
            # Re-raise with a clearer message that names the bad token.
            raise ValueError(f"'{token}' is not a valid integer.")

    return values


# -------------------------------------------------------------
# Function: analyze
#
# Purpose:
# Analyze a list of integers and calculate statistics.
# -------------------------------------------------------------
def analyze(values):

    # Make sure the list is not empty.
    if not values:
        raise ValueError("Cannot analyze an empty list.")

    count = len(values)
    minimum = min(values)
    maximum = max(values)
    total = sum(values)
    average = total / count

    # Build a frequency map: value -> how many times it appears.
    frequencies = {}
    for value in values:
        frequencies[value] = frequencies.get(value, 0) + 1

    # Duplicates are any values whose frequency is greater than 1.
    # Preserve first-seen order.
    duplicates = []
    for value in values:
        if frequencies[value] > 1 and value not in duplicates:
            duplicates.append(value)

    return {
        "count": count,
        "minimum": minimum,
        "maximum": maximum,
        "sum": total,
        "average": average,
        "duplicates": duplicates,
        "frequencies": frequencies,
    }


# -------------------------------------------------------------
# Function: display_results
#
# Purpose:
# Display analysis results in a readable format.
# -------------------------------------------------------------
def display_results(result):

    print("\n----- Analysis Results -----")
    print(f"Count: {result['count']}")
    print(f"Minimum: {result['minimum']}")
    print(f"Maximum: {result['maximum']}")
    print(f"Sum: {result['sum']}")
    print(f"Average: {result['average']}")
    print(f"Duplicates: {result['duplicates']}")

    print("\nFrequencies:")
    for value, freq in result["frequencies"].items():
        print(f"{value}: {freq}")


# -------------------------------------------------------------
# Function: main
#
# Purpose:
# Control the overall program.
# -------------------------------------------------------------
def main():

    print("INTEGER DATA ANALYZER")
    print("---------------------")

    # Ask the user to enter integers.
    text = input(
        "Enter integers separated by spaces: "
    )

    try:

        # Convert input into integers.
        values = parse_values(text)

        # Analyze the integers.
        result = analyze(values)

        # Display the result.
        display_results(result)

    except ValueError as error:

        # Display any input error.
        print("\nError:", error)


# -------------------------------------------------------------
# Start the program.
#
# This condition makes sure main() runs only when
# this Python file is executed directly.
# -------------------------------------------------------------
if __name__ == "__main__":
    main()

###### Sample Output with Input#####
# INTEGER DATA ANALYZER
# ---------------------
# Enter integers separated by spaces: -10 20 -5 30 -10

# ----- Analysis Results -----
# Count: 5
# Minimum: -10
# Maximum: 30
# Sum: 25
# Average: 5.0
# Duplicates: [-10]

# Frequencies:
# -10: 2
# -5: 1
# 20: 1
# 30: 1
##################
