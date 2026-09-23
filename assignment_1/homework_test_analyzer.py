from Lecture_1_export.assignment_1.homework_solution import parse_values, analyze

print("Running Integer Data Analyzer test suite...")
print("=" * 45)

# -------------------------------------------------------------
# Test 1: Basic parsing of well-formed input
# -------------------------------------------------------------
print("\nTest 1: Parsing well-formed input")
result_1 = parse_values("10 20 30")
print(f"  Input:    '10 20 30'")
print(f"  Output:   {result_1}")
assert result_1 == [10, 20, 30]
print("  PASSED")

# -------------------------------------------------------------
# Test 2: Parsing handles negative numbers and extra whitespace
# -------------------------------------------------------------
print("\nTest 2: Parsing negative numbers and extra whitespace")
result_2 = parse_values("  -10   20  -5 ")
print(f"  Input:    '  -10   20  -5 '")
print(f"  Output:   {result_2}")
assert result_2 == [-10, 20, -5]
print("  PASSED")

# -------------------------------------------------------------
# Test 3: Parsing raises ValueError on non-integer input
# -------------------------------------------------------------
print("\nTest 3: Parsing rejects non-integer input")
try:
    parse_values("10 abc 30")
    assert False, "Expected a ValueError for invalid input"
except ValueError as error:
    print(f"  Input:    '10 abc 30'")
    print(f"  Raised:   ValueError: {error}")
    print("  PASSED")

# -------------------------------------------------------------
# Test 4: Parsing raises ValueError on empty input
# -------------------------------------------------------------
print("\nTest 4: Parsing rejects empty input")
try:
    parse_values("")
    assert False, "Expected a ValueError for empty input"
except ValueError as error:
    print(f"  Input:    ''")
    print(f"  Raised:   ValueError: {error}")
    print("  PASSED")

# -------------------------------------------------------------
# Test 5: Analyzer computes correct core statistics
# -------------------------------------------------------------
print("\nTest 5: Analyzer computes core statistics")
result = analyze([10, 20, 30, 20])
print(f"  Input:    [10, 20, 30, 20]")
print(f"  Count:    {result['count']}")
print(f"  Minimum:  {result['minimum']}")
print(f"  Maximum:  {result['maximum']}")
print(f"  Sum:      {result['sum']}")
print(f"  Average:  {result['average']}")
print(f"  Duplicates: {result['duplicates']}")
assert result["count"] == 4
assert result["minimum"] == 10
assert result["maximum"] == 30
assert result["sum"] == 80
assert result["average"] == 20
assert result["duplicates"] == [20]
print("  PASSED")

# -------------------------------------------------------------
# Test 6: Analyzer computes correct frequency map
# -------------------------------------------------------------
print("\nTest 6: Analyzer computes frequency map")
print(f"  Frequencies: {result['frequencies']}")
assert result["frequencies"] == {10: 1, 20: 2, 30: 1}
print("  PASSED")

# -------------------------------------------------------------
# Test 7: Analyzer handles multiple duplicates and negative values
# -------------------------------------------------------------
print("\nTest 7: Analyzer handles negative values and duplicates")
result2 = analyze([-10, 20, -5, 30, -10])
print(f"  Input:    [-10, 20, -5, 30, -10]")
print(f"  Count:    {result2['count']}")
print(f"  Minimum:  {result2['minimum']}")
print(f"  Maximum:  {result2['maximum']}")
print(f"  Sum:      {result2['sum']}")
print(f"  Average:  {result2['average']}")
print(f"  Duplicates: {result2['duplicates']}")
print(f"  Frequencies: {result2['frequencies']}")
assert result2["count"] == 5
assert result2["minimum"] == -10
assert result2["maximum"] == 30
assert result2["sum"] == 25
assert result2["average"] == 5.0
assert result2["duplicates"] == [-10]
assert result2["frequencies"] == {-10: 2, 20: 1, -5: 1, 30: 1}
print("  PASSED")

# -------------------------------------------------------------
# Test 8: Analyzer raises ValueError on an empty list
# -------------------------------------------------------------
print("\nTest 8: Analyzer rejects an empty list")
try:
    analyze([])
    assert False, "Expected a ValueError for an empty list"
except ValueError as error:
    print(f"  Input:    []")
    print(f"  Raised:   ValueError: {error}")
    print("  PASSED")

print("\n" + "=" * 45)
print("All 8 tests passed!")
