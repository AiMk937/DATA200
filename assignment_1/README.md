# Integer Data Analyzer

## Overview
The Integer Data Analyzer is a command-line Python program built for the DATA 200 "Python Foundations" application project. The program accepts a space-separated sequence of integers from the user, analyzes the data, and
reports a clear summary of statistics. It demonstrates core Python fundamentals: input handling, type conversion, 
loops, conditionals, and the use of lists and dictionaries to organize data.

## Features
- Accepts a space-separated sequence of integers entered by the user.
- Converts raw text input into a list of integers.
- Calculates:
  - Count
  - Minimum
  - Maximum
  - Sum
  - Average
  - Duplicate values
  - Frequency of each value
- Separates the program into distinct functions for parsing, analysis, and display, keeping each responsibility isolated and easy to test.
- Handles invalid and empty input gracefully using exceptions, so the program never crashes on bad input.

## Requirements
- Python 3.8 or later
- No external libraries are required; the program only uses the Python standard library.

## How to Run the Program
1. Open a terminal in the project folder.
2. Run the program with:
   
   python3 homework_solution.py
   
3. When prompted, enter a series of integers separated by spaces, for example:
   
   Enter integers separated by spaces: -10 20 -5 30 -10
   
4. The program will print the analysis results to the terminal.

## How to Run the Tests
The test suite checks both the parsing and analysis functions, including error handling for invalid and empty input.

Run the tests with:

python3 homework_test_analyzer.py


A successful run will end with:

All 8 tests passed!


## Sample Input and Output
*Input:*

Enter integers separated by spaces: -10 20 -5 30 -10


*Output:*

----- Analysis Results -----
Count: 5
Minimum: -10
Maximum: 30
Sum: 25
Average: 5.0
Duplicates: [-10]

Frequencies:
-10: 2
20: 1
-5: 1
30: 1


## Project Structure

homework_solution.py       Main program: parsing, analysis, and display logic
homework_test_analyzer.py  Test suite with eight tests covering normal and edge-case behavior
README.md                  Project documentation (this file)
Design_Reflection.md       One-page reflection on design decisions
Test_Evidence.md           Recorded output from running the test suite
Submission_Checklist.md    Checklist confirming assignment requirements



