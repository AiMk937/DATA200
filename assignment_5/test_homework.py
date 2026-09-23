"""Automated tests for the linked-list sensor stream monitor.

Run:
    python -m unittest test_homework.py

Lists here are only test expectations and snapshots taken by walking the real
Node.next links; they never stand in for the window under test.
"""
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from homework_template import (FIELDS, LinkedWindow, Node, Reading,
                               StreamMonitor, read_readings)

BASE = datetime(2026, 9, 1, 9, 0, 0)


def make_reading(minute, sensor_id="TEMP_A", value=20.0):
    """Build one Reading at BASE plus the given number of minutes."""
    return Reading(BASE + timedelta(minutes=minute), sensor_id, value)


def walk(window):
    """Snapshot retained values by following actual links, not __iter__."""
    values = []
    node = window.head
    while node is not None:
        values.append(node.reading.value)
        node = node.next
    return values


def fill(window, values, sensor_id="TEMP_A"):
    """Append the given values in order and return the evictions they caused."""
    evicted = []
    for minute, value in enumerate(values):
        evicted.append(window.append(make_reading(minute, sensor_id, value)))
    return evicted


class TestEmptyAndSingleton(unittest.TestCase):
    """Group 1 and 2: empty removal, empty mean, and one-node endpoint reset."""

    def test_empty_removal_and_empty_mean(self):
        window = LinkedWindow(3)
        self.assertIsNone(window.mean())
        with self.assertRaises(IndexError):
            window.remove_first()
        # The failed removal must not have disturbed any metadata.
        self.assertIsNone(window.head)
        self.assertIsNone(window.tail)
        self.assertEqual(window.size, 0)
        self.assertAlmostEqual(window.total, 0.0)
        self.assertEqual(walk(window), [])

    def test_one_node_removal_resets_both_endpoints_and_total(self):
        window = LinkedWindow(3)
        window.append(make_reading(0, value=12.5))
        self.assertIs(window.head, window.tail)
        self.assertIsNone(window.tail.next)
        self.assertEqual(window.size, 1)
        self.assertAlmostEqual(window.total, 12.5)
        self.assertAlmostEqual(window.mean(), 12.5)

        removed = window.remove_first()
        self.assertIsInstance(removed, Reading)
        self.assertAlmostEqual(removed.value, 12.5)
        self.assertIsNone(window.head)
        self.assertIsNone(window.tail)
        self.assertEqual(window.size, 0)
        self.assertAlmostEqual(window.total, 0.0)
        self.assertIsNone(window.mean())

    def test_node_starts_detached_and_iteration_follows_links(self):
        node = Node(make_reading(0, value=1.0))
        self.assertIsNone(node.next)
        window = LinkedWindow(4)
        fill(window, [1.0, 2.0, 3.0])
        self.assertEqual([r.value for r in window], walk(window))
        self.assertEqual([r.value for r in window], [1.0, 2.0, 3.0])


class TestEviction(unittest.TestCase):
    """Group 3: capacity-one and capacity-five eviction and the running sum."""

    def test_capacity_one_replaces_and_keeps_endpoints_aligned(self):
        window = LinkedWindow(1)
        self.assertIsNone(window.append(make_reading(0, value=10.0)))
        self.assertIs(window.head, window.tail)

        evicted = window.append(make_reading(1, value=20.0))
        self.assertIsNotNone(evicted)
        self.assertAlmostEqual(evicted.value, 10.0)
        self.assertEqual(walk(window), [20.0])
        self.assertIs(window.head, window.tail)
        self.assertIsNone(window.tail.next)
        self.assertEqual(window.size, 1)
        self.assertAlmostEqual(window.total, 20.0)
        self.assertAlmostEqual(window.mean(), 20.0)

    def test_capacity_five_eviction_preserves_order_and_running_sum(self):
        window = LinkedWindow(5)
        evicted = fill(window, [10.0, 20.0, 30.0, 40.0, 50.0])
        self.assertEqual(evicted, [None, None, None, None, None])
        self.assertEqual(walk(window), [10.0, 20.0, 30.0, 40.0, 50.0])
        self.assertEqual(window.size, 5)
        self.assertAlmostEqual(window.total, 150.0)
        self.assertAlmostEqual(window.mean(), 30.0)

        oldest = window.append(make_reading(5, value=60.0))
        self.assertAlmostEqual(oldest.value, 10.0)
        self.assertEqual(walk(window), [20.0, 30.0, 40.0, 50.0, 60.0])
        self.assertEqual(window.size, 5)
        self.assertAlmostEqual(window.total, 200.0)
        self.assertAlmostEqual(window.mean(), 40.0)
        self.assertIsNone(window.tail.next)

    def test_running_sum_tracks_repeated_eviction(self):
        window = LinkedWindow(3)
        fill(window, [1.5, 2.5, 3.5, 4.5, 5.5, 6.5])
        self.assertEqual(walk(window), [4.5, 5.5, 6.5])
        self.assertAlmostEqual(window.total, 16.5)
        self.assertAlmostEqual(window.mean(), 5.5)


class TestMonitorBehaviour(unittest.TestCase):
    """Groups 4 and 5: independent windows, warmup, inclusive threshold."""

    def test_interleaved_sensors_keep_independent_windows(self):
        monitor = StreamMonitor()
        for minute, (a_value, b_value) in enumerate([(20.0, 30.0), (21.0, 31.0),
                                                     (19.0, 29.0)]):
            monitor.process(make_reading(minute, "TEMP_A", a_value))
            monitor.process(make_reading(minute, "TEMP_B", b_value))

        self.assertEqual(sorted(monitor.windows), ["TEMP_A", "TEMP_B"])
        self.assertIsNot(monitor.windows["TEMP_A"], monitor.windows["TEMP_B"])
        self.assertEqual(walk(monitor.windows["TEMP_A"]), [20.0, 21.0, 19.0])
        self.assertEqual(walk(monitor.windows["TEMP_B"]), [30.0, 31.0, 29.0])
        self.assertAlmostEqual(monitor.windows["TEMP_A"].mean(), 20.0)
        self.assertAlmostEqual(monitor.windows["TEMP_B"].mean(), 30.0)

        # A shared timestamp across different sensors is legal.
        report = monitor.process(make_reading(3, "TEMP_B", 36.0))
        self.assertEqual(report["status"], "ALERT")
        self.assertEqual(walk(monitor.windows["TEMP_A"]), [20.0, 21.0, 19.0])

    def test_warmup_reports_blank_baseline_and_deviation(self):
        monitor = StreamMonitor()
        for minute, value in enumerate([30.0, 31.0, 29.0]):
            report = monitor.process(make_reading(minute, "TEMP_B", value))
            self.assertEqual(report["status"], "WARMUP")
            self.assertEqual(report["baseline_mean"], "")
            self.assertEqual(report["abs_deviation"], "")
            self.assertEqual(report["evicted_value"], "")
            self.assertEqual(report["window_size_after"], minute + 1)

    def test_inclusive_threshold_and_baseline_excludes_current_reading(self):
        # Worked checkpoint: prior TEMP_B values 30, 31, 29 give a baseline of
        # 30.00. The incoming 36 deviates by exactly 6.00, which is an ALERT.
        monitor = StreamMonitor()
        for minute, value in enumerate([30.0, 31.0, 29.0]):
            monitor.process(make_reading(minute, "TEMP_B", value))

        report = monitor.process(make_reading(3, "TEMP_B", 36.0))
        self.assertEqual(report["baseline_mean"], "30.00")
        self.assertEqual(report["abs_deviation"], "6.00")
        self.assertEqual(report["status"], "ALERT")
        # The baseline is the prior mean, not 31.50, which would include 36.
        self.assertNotEqual(report["baseline_mean"], "31.50")
        # An alert reading still enters the window.
        self.assertEqual(report["window_size_after"], 4)
        self.assertEqual(walk(monitor.windows["TEMP_B"]), [30.0, 31.0, 29.0, 36.0])

    def test_deviation_just_below_threshold_is_ok(self):
        monitor = StreamMonitor()
        for minute in range(3):
            monitor.process(make_reading(minute, "TEMP_A", 20.0))
        report = monitor.process(make_reading(3, "TEMP_A", 25.99))
        self.assertEqual(report["baseline_mean"], "20.00")
        self.assertEqual(report["abs_deviation"], "5.99")
        self.assertEqual(report["status"], "OK")

    def test_full_window_reports_the_evicted_value(self):
        monitor = StreamMonitor()
        for minute, value in enumerate([20.0, 21.0, 19.0, 20.0, 28.0]):
            report = monitor.process(make_reading(minute, "TEMP_A", value))
            self.assertEqual(report["evicted_value"], "")
        report = monitor.process(make_reading(5, "TEMP_A", 21.0))
        self.assertEqual(report["evicted_value"], "20.00")
        self.assertEqual(report["window_size_after"], 5)
        self.assertEqual(report["baseline_mean"], "21.60")
        self.assertEqual(sorted(report), sorted(FIELDS))

    def test_configuration_values_are_used_instead_of_defaults(self):
        monitor = StreamMonitor(capacity=2, min_history=1, threshold=1.0)
        first = monitor.process(make_reading(0, "TEMP_A", 10.0))
        self.assertEqual(first["status"], "WARMUP")
        second = monitor.process(make_reading(1, "TEMP_A", 12.0))
        self.assertEqual(second["status"], "ALERT")
        self.assertEqual(second["baseline_mean"], "10.00")


class TestValidation(unittest.TestCase):
    """Group 6: invalid configuration, invalid CSV, and rejected timestamps."""

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)

    def write_csv(self, text):
        path = Path(self.directory.name) / "input.csv"
        path.write_text(text, encoding="utf-8")
        return path

    def test_invalid_window_capacity_raises_value_error(self):
        for capacity in (0, -1, True, False, 2.5, "3", None):
            with self.subTest(capacity=capacity):
                with self.assertRaises(ValueError):
                    LinkedWindow(capacity)

    def test_invalid_monitor_configuration_raises_value_error(self):
        invalid = [
            {"capacity": 0}, {"capacity": -4}, {"capacity": True}, {"capacity": 5.0},
            {"min_history": 0}, {"min_history": 6}, {"min_history": True},
            {"min_history": 2.0}, {"threshold": 0}, {"threshold": -1.0},
            {"threshold": float("inf")}, {"threshold": float("nan")},
            {"threshold": True}, {"threshold": "6.0"},
        ]
        for kwargs in invalid:
            with self.subTest(**kwargs):
                with self.assertRaises(ValueError):
                    StreamMonitor(**kwargs)

    def test_repeated_or_earlier_timestamp_leaves_state_unchanged(self):
        monitor = StreamMonitor()
        monitor.process(make_reading(0, "TEMP_A", 20.0))
        monitor.process(make_reading(1, "TEMP_A", 21.0))
        window = monitor.windows["TEMP_A"]
        before = (walk(window), window.size, window.total, window.head, window.tail)

        for minute in (1, 0):
            with self.subTest(minute=minute):
                with self.assertRaises(ValueError):
                    monitor.process(make_reading(minute, "TEMP_A", 99.0))
                after = (walk(window), window.size, window.total,
                         window.head, window.tail)
                self.assertEqual(before, after)
        self.assertEqual(walk(window), [20.0, 21.0])

    def test_invalid_reading_fields_are_rejected_without_mutation(self):
        monitor = StreamMonitor()
        monitor.process(make_reading(0, "TEMP_A", 20.0))
        window = monitor.windows["TEMP_A"]

        for sensor_id, value in [("", 20.0), ("   ", 20.0), (None, 20.0),
                                 ("TEMP_A", float("nan")),
                                 ("TEMP_A", float("inf")), ("TEMP_A", "20.0")]:
            with self.subTest(sensor_id=sensor_id, value=value):
                with self.assertRaises(ValueError):
                    monitor.process(Reading(BASE + timedelta(minutes=9),
                                            sensor_id, value))
        self.assertEqual(walk(window), [20.0])
        self.assertEqual(window.size, 1)

    def test_bad_header_is_rejected(self):
        path = self.write_csv("sensor_id,timestamp,value\nTEMP_A,2026-09-01T09:00:00,20\n")
        with self.assertRaises(ValueError):
            list(read_readings(path))

    def test_malformed_csv_rows_raise_value_error(self):
        header = "timestamp,sensor_id,value\n"
        bad_rows = [
            "2026-09-01T09:00:00,,20\n",                      # blank sensor id
            "2026-09-01T09:00:00,TEMP_A,abc\n",               # non-numeric value
            "2026-09-01T09:00:00,TEMP_A,nan\n",               # not finite
            "2026-09-01T09:00:00,TEMP_A,inf\n",               # not finite
            "2026-09-01T09:00:00+05:30,TEMP_A,20\n",          # timezone aware
            "not-a-timestamp,TEMP_A,20\n",                    # unparseable
            "2026-09-01T09:00:00,TEMP_A\n",                   # too few fields
            "2026-09-01T09:00:00,TEMP_A,20,extra\n",          # too many fields
        ]
        for row in bad_rows:
            with self.subTest(row=row.strip()):
                path = self.write_csv(header + row)
                with self.assertRaises(ValueError):
                    list(read_readings(path))

    def test_valid_csv_is_parsed_and_whitespace_is_stripped(self):
        path = self.write_csv("timestamp,sensor_id,value\n"
                              "2026-09-01T09:00:00,  TEMP_A  ,20\n"
                              "2026-09-01T09:01:00,TEMP_A,21.5\n")
        readings = list(read_readings(path))
        self.assertEqual([r.sensor_id for r in readings], ["TEMP_A", "TEMP_A"])
        self.assertAlmostEqual(readings[1].value, 21.5)
        self.assertEqual(readings[0].timestamp, datetime(2026, 9, 1, 9, 0))
        self.assertIsNone(readings[0].timestamp.tzinfo)

    def test_timezone_aware_reading_is_not_silently_accepted(self):
        aware = datetime(2026, 9, 1, 9, 0, tzinfo=timezone.utc)
        monitor = StreamMonitor()
        monitor.process(Reading(aware, "TEMP_A", 20.0))
        # A second aware reading at the same instant is still out of order.
        with self.assertRaises(ValueError):
            monitor.process(Reading(aware, "TEMP_A", 21.0))


class TestSampleDataset(unittest.TestCase):
    """End-to-end check against the supplied dataset, when it is present."""

    def test_sample_dataset_gives_24_readings_and_5_alerts(self):
        path = Path(__file__).with_name("sensor_readings.csv")
        if not path.exists():
            self.skipTest("sensor_readings.csv is not beside the tests")
        monitor = StreamMonitor()
        count = alerts = 0
        for reading in read_readings(path):
            row = monitor.process(reading)
            count += 1
            alerts += row["status"] == "ALERT"
        self.assertEqual(count, 24)
        self.assertEqual(alerts, 5)
        self.assertEqual(walk(monitor.windows["TEMP_B"]), [30.0, 31.0, 30.0, 38.0, 30.0])


if __name__ == "__main__":
    unittest.main()
