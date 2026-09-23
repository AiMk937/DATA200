"""
Test harness for course_analyzer_template.py (DATA 200 Week 2).

Usage:
    python3 test_course_analyzer.py /path/to/your/course_analyzer_template.py

This runs your script as a real subprocess (the same way the grader/shell
would) against 10 scenarios and prints PASS/FAIL for each, with details
on failures so you can go fix the actual bug yourself.

This does NOT check every possible edge case exhaustively -- it's a sanity
check, not a substitute for reading your own report output.
"""

import subprocess
import sys
import tempfile
import os
from pathlib import Path


def run(script_path, args, cwd):
    """Run `python3 script_path *args` and capture exit code + stdout/stderr."""
    result = subprocess.run(
        [sys.executable, str(script_path), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=15,
    )
    return result.returncode, result.stdout, result.stderr


def write(path, content):
    Path(path).write_text(content, encoding="utf-8")


SAMPLE_CSV = """student_id,name,quiz1,quiz2,assignment,tags
S101,Ana,8,9,18,python|files|sets
S102,Bo,6,7,15,functions|exceptions
S103,Cam,10,9,20,python|generators|zip
S104,Dee,5,6,14,files|exceptions
S105,Eli,9,8,17,sets|vectors|python
S106,Fay,7,10,19,lambda|enumerate|zip
"""

MIXED_CSV = """student_id,name,quiz1,quiz2,assignment,tags
S101,Ana,8,9,18,python|files
,NoId,5,5,10,x
S102,Bo,99,7,15,y
S103,Cam,7,notanumber,15,z
S104,Dee,7,7,7,7,extra
S105,Eli,6,6,12,ok
"""

BAD_HEADER_CSV = """id,name,q1,q2,hw,topics
S1,Ana,8,9,18,python
"""

ALL_BAD_CSV = """student_id,name,quiz1,quiz2,assignment,tags
,X,999,1,1,a
"""


results = []


def check(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    results.append((name, status, detail))
    print(f"[{status}] {name}")
    if not condition and detail:
        print(f"       -> {detail}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 test_course_analyzer.py /path/to/course_analyzer_template.py")
        sys.exit(1)

    script_path = Path(sys.argv[1]).resolve()
    if not script_path.exists():
        print(f"Cannot find script at {script_path}")
        sys.exit(1)

    print(f"Testing: {script_path}\n")

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        # ---------- Test 1: happy path ----------
        write(tmp / "students_sample.csv", SAMPLE_CSV)
        code, out, err = run(
            script_path, ["students_sample.csv", "out1.txt", "70"], tmp)
        report = (tmp / "out1.txt").read_text() if (tmp /
                                                    "out1.txt").exists() else ""
        check(
            "1. Happy path runs and exits 0",
            code == 0 and "Valid: 6 | Rejected: 0" in report and "Class mean: 82.08%" in report,
            f"exit={code}, stderr={err!r}, report_head={report[:120]!r}",
        )

        # ---------- Test 2: default threshold ----------
        code, out, err = run(
            script_path, ["students_sample.csv", "out2.txt"], tmp)
        report = (tmp / "out2.txt").read_text() if (tmp /
                                                    "out2.txt").exists() else ""
        check(
            "2. Default threshold (omitted) defaults to 70.0",
            code == 0 and "Threshold: 70.0%" in report,
            f"exit={code}, stderr={err!r}",
        )

        # ---------- Test 3: wrong argument count ----------
        code, out, err = run(script_path, ["students_sample.csv"], tmp)
        check(
            "3. Wrong argument count -> exit 1 with error",
            code == 1 and len(err.strip()) > 0,
            f"exit={code}, stderr={err!r}",
        )

        # ---------- Test 4: nonnumeric threshold ----------
        code, out, err = run(
            script_path, ["students_sample.csv", "out4.txt", "abc"], tmp)
        check(
            "4. Nonnumeric threshold -> exit 1 with error",
            code == 1 and len(err.strip()) > 0,
            f"exit={code}, stderr={err!r}",
        )

        # ---------- Test 5: out-of-range threshold ----------
        code, out, err = run(
            script_path, ["students_sample.csv", "out5.txt", "150"], tmp)
        check(
            "5. Out-of-range threshold (150) -> exit 1 with error",
            code == 1 and len(err.strip()) > 0,
            f"exit={code}, stderr={err!r}",
        )

        # ---------- Test 6: missing input file ----------
        code, out, err = run(
            script_path, ["does_not_exist.csv", "out6.txt"], tmp)
        check(
            "6. Missing input file -> exit 1 with error",
            code == 1 and len(err.strip()) > 0,
            f"exit={code}, stderr={err!r}",
        )

        # ---------- Test 7: empty CSV ----------
        write(tmp / "empty.csv", "")
        code, out, err = run(script_path, ["empty.csv", "out7.txt"], tmp)
        check(
            "7. Empty CSV -> exit 1 with error",
            code == 1 and len(err.strip()) > 0,
            f"exit={code}, stderr={err!r}",
        )

        # ---------- Test 8: wrong header ----------
        write(tmp / "badheader.csv", BAD_HEADER_CSV)
        code, out, err = run(script_path, ["badheader.csv", "out8.txt"], tmp)
        check(
            "8. Wrong CSV header -> exit 1 with error",
            code == 1 and len(err.strip()) > 0,
            f"exit={code}, stderr={err!r}",
        )

        # ---------- Test 9: mixed valid/invalid rows ----------
        write(tmp / "mixed.csv", MIXED_CSV)
        code, out, err = run(script_path, ["mixed.csv", "out9.txt", "70"], tmp)
        report = (tmp / "out9.txt").read_text() if (tmp /
                                                    "out9.txt").exists() else ""
        check(
            "9a. Mixed rows -> program does NOT crash (exit 0)",
            code == 0,
            f"exit={code}, stderr={err!r}",
        )
        check(
            "9b. Mixed rows -> exactly 2 valid, 4 rejected",
            "Valid: 2 | Rejected: 4" in report,
            f"report_head={report[:200]!r}",
        )
        check(
            "9c. Mixed rows -> REJECTED ROWS section lists 4 lines",
            report.count("Line ") == 4,
            f"report_tail={report[-400:]!r}",
        )

        # ---------- Test 10: no valid students at all ----------
        write(tmp / "allbad.csv", ALL_BAD_CSV)
        code, out, err = run(script_path, ["allbad.csv", "out10.txt"], tmp)
        out10_created_nonempty = (
            tmp / "out10.txt").exists() and (tmp / "out10.txt").stat().st_size > 0
        check(
            "10. No valid students -> exit 1, no report written",
            code == 1 and not out10_created_nonempty,
            f"exit={code}, stderr={err!r}, file_exists_nonempty={out10_created_nonempty}",
        )

    print("\n" + "=" * 50)
    passed = sum(1 for _, status, _ in results if status == "PASS")
    total = len(results)
    print(f"RESULT: {passed}/{total} tests passed")
    if passed != total:
        print("See [FAIL] lines above for what to fix.")


if __name__ == "__main__":
    main()
