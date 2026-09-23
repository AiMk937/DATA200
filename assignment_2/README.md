# Course Analytics Pipeline

Reads student scores from a CSV, checks them, and writes a report.

## Requirements

Python 3.10 or later.


## How to run

```
python3 course_analyzer.py students.csv report.txt
```

- `students.csv` = input file
- `report.txt` = output file generated
- `70` = passing percentage (optional, defaults to 70)

## Input format

CSV header must be exactly:
```
student_id,name,quiz1,quiz2,assignment,tags
```
- quiz1, quiz2: 0–10
- assignment: 0–20
- tags: separated by `|` (e.g. `python|files`)

## Output

The report includes: class average, pass/fail counts, a leaderboard,
tag counts, per-student details, and any rejected (bad) rows.

## Testing

```
python3 test.py course_analyzer.py
```
