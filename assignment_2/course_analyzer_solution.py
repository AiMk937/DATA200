"""DATA 200 Week 2 - Course Analytics Pipeline student template.

Complete every TODO without changing the required function names or parameters.
Use only the Python standard library. Do not use mutable global variables.
"""

import csv
import sys
from collections import Counter


HEADER = ["student_id", "name", "quiz1", "quiz2", "assignment", "tags"]
MAX_POINTS = (10, 10, 20)


def parse_args(argv):
    """Validate and return the command-line settings.

    Student task:
    - Accept an input CSV path and an output text-file path.
    - Accept an optional passing threshold; use 70.0 when it is omitted.
    - Raise ValueError for the wrong argument count, a nonnumeric threshold,
      or a threshold outside 0 through 100.
    - Return input_path, output_path, and threshold as three values.

    Algorithm:
        check argument count
        choose default or convert argv[3] to float
        validate the threshold range
        return the three settings
    """
    if len(argv) not in (3, 4):
        raise ValueError(
            "Usage: course_analyzer_solution.py INPUT.csv OUTPUT.txt [THRESHOLD]"
        )

    input_path = argv[1]
    output_path = argv[2]

    if len(argv) == 4:
        try:
            threshold = float(argv[3])
        except ValueError:
            raise ValueError(f"Threshold must be a number, got {argv[3]!r}")
    else:
        threshold = 70.0

    if not (0.0 <= threshold <= 100.0):
        raise ValueError(
            f"Threshold must be between 0 and 100, got {threshold}")

    return input_path, output_path, threshold


def parse_score(value, minimum, maximum):
    """Convert and validate one assessment score.

    Student task:
    - Convert value to an integer.
    - Verify that minimum <= score <= maximum.
    - Raise ValueError with a useful message when the score is invalid.
    - Return the validated integer.

    Algorithm:
        score = integer form of value
        if score is outside the inclusive range: raise ValueError
        return score
    """
    try:
        score = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"Score must be an integer, got {value!r}")

    if not (minimum <= score <= maximum):
        raise ValueError(
            f"Score {score} is outside the allowed range [{minimum}, {maximum}]"
        )

    return score


def parse_tags(text):
    """Convert pipe-separated tag text into a normalized set.

    Student task:
    - Split text using the pipe character.
    - Strip surrounding whitespace and convert each tag to lowercase.
    - Ignore empty tags and remove duplicates by returning a set.

    Algorithm:
        split text into pieces
        clean every non-empty piece
        return the cleaned pieces as a set
    """
    pieces = text.split("|")
    tags = set()
    for piece in pieces:
        cleaned = piece.strip().lower()
        if cleaned:
            tags.add(cleaned)
    return tags


def weighted_total(*scores):
    """Return the total of a variable number of scores.

    Student task:
    - Use the *scores tuple supplied by the caller.
    - Return the sum of all supplied numeric values.

    Algorithm:
        add every value in scores
        return the total
    """
    return sum(scores)


def read_students(path, rejected):
    """Generate validated student dictionaries from a CSV file.

    Student task:
    - Open path with newline="" and UTF-8 encoding inside a with block.
    - Create csv.reader(source), obtain the header, and detect an empty file.
    - Require the header to equal HEADER exactly.
    - Use enumerate(..., start=2) to retain original CSV line numbers.
    - Validate the column count, required ID/name, and all three scores.
    - Build a dictionary containing id, name, scores, percent, and tags.
    - yield each valid dictionary instead of returning a complete list.
    - Catch recoverable row errors and append (line_number, reason) to rejected.

    Algorithm:
        open file and validate header
        for each numbered data row:
            try to unpack, clean, validate, and calculate the record
            yield a valid record
            on a row error, add its line number and reason to rejected
    """
    with open(path, newline="", encoding="utf-8-sig") as source:
        reader = csv.reader(source)

        try:
            header = next(reader)
        except StopIteration:
            raise ValueError("Input CSV file is empty")

        if header != HEADER:
            raise ValueError(
                f"Invalid CSV header: expected {HEADER}, got {header}")

        for line_number, row in enumerate(reader, start=2):
            try:
                if len(row) != len(HEADER):
                    raise ValueError(
                        f"Expected {len(HEADER)} columns, got {len(row)}"
                    )

                student_id, name, quiz1_text, quiz2_text, assignment_text, tags_text = row

                student_id = student_id.strip()
                name = name.strip()

                if not student_id:
                    raise ValueError("Missing student_id")
                if not name:
                    raise ValueError("Missing name")

                quiz1 = parse_score(quiz1_text, 0, MAX_POINTS[0])
                quiz2 = parse_score(quiz2_text, 0, MAX_POINTS[1])
                assignment = parse_score(assignment_text, 0, MAX_POINTS[2])
                tags = parse_tags(tags_text)

                total = weighted_total(quiz1, quiz2, assignment)
                percent = total / sum(MAX_POINTS) * 100

                yield {
                    "id": student_id,
                    "name": name,
                    "scores": (quiz1, quiz2, assignment),
                    "percent": percent,
                    "tags": tags,
                }
            except ValueError as error:
                rejected.append((line_number, str(error)))


def component_means(students):
    """Return the mean of each score component as a tuple.

    Student task:
    - Calculate a separate mean for quiz1, quiz2, and assignment.
    - Use the score position in each student["scores"] tuple.
    - Return a tuple whose length matches MAX_POINTS.

    Algorithm:
        for each component index:
            sum that component for all students
            divide by the number of students
        return the component means as a tuple
    """
    count = len(students)
    means = []
    for index in range(len(MAX_POINTS)):
        component_sum = sum(student["scores"][index] for student in students)
        means.append(component_sum / count)
    return tuple(means)


def vector_metrics(scores, means):
    """Return a difference vector and dot product.

    Student task:
    - Pair scores and means using zip(..., strict=True).
    - Difference vector: score - corresponding mean.
    - Dot product: sum(score * corresponding mean).
    - Return both results as two values.

    Algorithm:
        create pairwise differences
        create and sum pairwise products
        return differences, dot_product
    """
    differences = tuple(
        score - mean for score, mean in zip(scores, means, strict=True)
    )
    dot_product = sum(
        score * mean for score, mean in zip(scores, means, strict=True)
    )
    return differences, dot_product


def summarize(students, threshold):
    """Calculate and return the required class-level analytics.

    Student task:
    - Calculate the mean student percentage.
    - Count students whose percentage is at least threshold.
    - Create the union of every student's tag set.
    - Count how frequently each tag appears; Counter may be useful.
    - Return mean_percent, pass_count, all_tags, and frequencies.

    Algorithm:
        calculate percentage mean and passing count
        combine all tag sets
        count every tag occurrence
        return all four results
    """
    mean_percent = sum(student["percent"]
                       for student in students) / len(students)
    pass_count = sum(
        1 for student in students if student["percent"] >= threshold)

    all_tags = set()
    for student in students:
        all_tags |= student["tags"]

    frequencies = Counter()
    for student in students:
        frequencies.update(student["tags"])

    return mean_percent, pass_count, all_tags, frequencies


def write_report(path, students, rejected, threshold):
    """Write the complete course analytics report.

    Student task:
    - Call summarize() and component_means().
    - Sort students by percentage descending, then name ascending.
    - Use a lambda expression for the sorting key.
    - Open path for writing with UTF-8 encoding.
    - Write the run summary, class summary, and leaderboard.
    - Use enumerate(..., start=1) for leaderboard ranks.
    - Write tag union/frequencies and detailed student vector metrics.
    - Finish with every rejected line and reason, or "None".

    Algorithm:
        calculate summaries and component means
        sort the students
        open the output file
        write each required report section in order
    """
    mean_percent, pass_count, all_tags, frequencies = summarize(
        students, threshold)
    means = component_means(students)

    total_students = len(students)
    pass_percent = pass_count / total_students * 100

    ranked = sorted(
        students, key=lambda student: (-student["percent"], student["name"]))

    with open(path, "w", encoding="utf-8") as report:
        report.write("COURSE ANALYTICS REPORT\n")
        report.write(
            f"Valid: {total_students} | Rejected: {len(rejected)} | "
            f"Threshold: {threshold:.1f}%\n"
        )
        report.write(
            f"Class mean: {mean_percent:.2f}% | "
            f"Passing: {pass_count}/{total_students} ({pass_percent:.1f}%)\n"
        )
        report.write("\n")

        report.write("LEADERBOARD\n")
        for rank, student in enumerate(ranked, start=1):
            report.write(
                f"{rank}. {student['name']} ({student['id']}): "
                f"{student['percent']:.2f}%\n"
            )
        report.write("\n")

        report.write("TAGS\n")
        report.write(f"Union: {', '.join(sorted(all_tags))}\n")
        for tag in sorted(frequencies):
            report.write(f"{tag}: {frequencies[tag]}\n")
        report.write("\n")

        report.write("STUDENT DETAIL\n")
        for student in ranked:
            diffs, dot = vector_metrics(student["scores"], means)
            rounded_diffs = tuple(round(value, 2) for value in diffs)
            status = "PASS" if student["percent"] >= threshold else "FAIL"
            report.write(
                f"{student['id']} | {student['name']} | {student['scores']} | "
                f"{student['percent']:.2f}% | {status} | "
                f"tags={sorted(student['tags'])} | diff={rounded_diffs} | "
                f"dot={dot:.2f}\n"
            )
        report.write("\n")

        report.write("REJECTED ROWS\n")
        if rejected:
            for line_number, reason in rejected:
                report.write(f"Line {line_number}: {reason}\n")
        else:
            report.write("None\n")


def main():
    """Coordinate the complete command-line application.

    Student task:
    - Parse sys.argv into input path, output path, and threshold.
    - Create an empty rejected list.
    - Materialize the read_students() generator as a student list.
    - Raise ValueError when no valid records remain.
    - Write the report and print a success message.
    - Catch ValueError and OSError, print the message to sys.stderr,
      and exit with a nonzero status.

    Algorithm:
        try:
            parse arguments
            read valid students while collecting rejected rows
            ensure at least one valid student exists
            write report and announce its path
        except expected fatal errors:
            print an error and exit with status 1
    """
    try:
        input_path, output_path, threshold = parse_args(sys.argv)
        rejected = []
        students = list(read_students(input_path, rejected))

        if not students:
            raise ValueError("No valid student records were found")

        write_report(output_path, students, rejected, threshold)
        print(f"Report written to {output_path}")
    except (ValueError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
