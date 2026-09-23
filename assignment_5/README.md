# DATA 200 - Linked Lists

Aimaan Khan

Two programs: the in-class LRU cache and the sensor stream monitor homework.
Python 3.10 or newer. Standard library only, no installation needed.

## Files

| File | What it is |
| --- | --- |
| `student_starter.py` | Classwork: doubly linked list and LRU cache |
| `homework_template.py` | Homework: linked-list sensor stream monitor |
| `sensor_readings.csv` | Input data, 24 readings from two sensors |
| `alerts.csv` | Output produced by the homework |
| `test_homework.py` | 21 tests for the homework |
| `reflection.md` | Written answers for Step 6 |

## How to run

Open a terminal in this folder first.

Classwork:

```
python3 student_starter.py
```

Ends with `All 10 demos passed.`

Homework:

```
python3 homework_template.py --input sensor_readings.csv --output alerts.csv
```

Prints `Processed 24 readings; 5 alerts.` and writes `alerts.csv`.

Tests:

```
python3 -m unittest test_homework.py
```

Ends with `Ran 21 tests` and `OK`.
