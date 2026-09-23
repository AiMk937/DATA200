"""Linked-list sensor stream monitor. Python 3.10+.

Run:
    python homework_template.py --input sensor_readings.csv --output alerts.csv
    python -m unittest test_homework.py

Each sensor's retained history lives only in Node.next links. No list, tuple,
array, deque, dictionary, pandas object, NumPy object, or third-party linked-list
class stores that history, and no method converts the window to a list in order to
compute a mean. The single dictionary maps sensor IDs to LinkedWindow objects, and
the only list is FIELDS, the CSV column order.
"""
import argparse
import csv
import math
from datetime import datetime
from pathlib import Path


class Reading:
    """One CSV row: when it was taken, which sensor took it, and the value."""

    def __init__(self, timestamp, sensor_id, value):
        # A plain record. Ingestion and StreamMonitor.process own all validation.
        self.timestamp = timestamp
        self.sensor_id = sensor_id
        self.value = value


class Node:
    """Linked-list wrapper: one Reading plus the forward link."""

    def __init__(self, reading):
        self.reading = reading
        self.next = None


class LinkedWindow:
    """Own the latest capacity readings for one sensor, oldest at head."""

    def __init__(self, capacity):
        # bool is a subclass of int, so reject it before the int check.
        if isinstance(capacity, bool) or not isinstance(capacity, int):
            raise ValueError("capacity must be a positive integer")
        if capacity <= 0:
            raise ValueError("capacity must be a positive integer")
        self.capacity = capacity
        self.head = None
        self.tail = None
        self.size = 0
        self.total = 0.0

    def append(self, reading):
        """Append in O(1); evict and return oldest Reading if over capacity."""
        node = Node(reading)
        if self.tail is None:
            self.head = node
        else:
            self.tail.next = node
        self.tail = node
        self.size += 1
        self.total += reading.value
        if self.size > self.capacity:
            return self.remove_first()
        return None

    def remove_first(self):
        """Remove and return oldest Reading in O(1); raise IndexError if empty."""
        if self.head is None:
            raise IndexError("cannot remove from an empty window")
        node = self.head
        self.head = node.next
        # Detach so the caller cannot walk back into the window.
        node.next = None
        self.size -= 1
        self.total -= node.reading.value
        if self.head is None:
            # Last node removed: reset both endpoints and clear accumulated drift.
            self.tail = None
            self.total = 0.0
        return node.reading

    def mean(self):
        """Return running mean in O(1), or None when empty."""
        if self.size == 0:
            return None
        return self.total / self.size

    def __iter__(self):
        """Yield Readings oldest first by traversing actual links."""
        current = self.head
        while current is not None:
            yield current.reading
            current = current.next


class StreamMonitor:
    def __init__(self, capacity=5, min_history=3, threshold=6.0):
        if isinstance(capacity, bool) or not isinstance(capacity, int) or capacity <= 0:
            raise ValueError("capacity must be a positive integer")
        if isinstance(min_history, bool) or not isinstance(min_history, int):
            raise ValueError("min_history must be an integer")
        if not 1 <= min_history <= capacity:
            raise ValueError("min_history must be between 1 and capacity")
        if isinstance(threshold, bool) or not isinstance(threshold, (int, float)):
            raise ValueError("threshold must be a positive finite number")
        if not math.isfinite(threshold) or threshold <= 0:
            raise ValueError("threshold must be a positive finite number")
        self.capacity = capacity
        self.min_history = min_history
        self.threshold = float(threshold)
        # The one permitted dictionary: sensor ID -> that sensor's LinkedWindow.
        self.windows = {}

    def process(self, reading):
        """Return report dict. Validate before mutation; compare BEFORE append."""
        sensor_id = reading.sensor_id
        if not isinstance(sensor_id, str) or not sensor_id.strip():
            raise ValueError("sensor_id must be a nonblank string")
        value = reading.value
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("value must be a finite number")
        if not math.isfinite(value):
            raise ValueError("value must be a finite number")

        # Reject a repeated or out-of-order timestamp before touching any state.
        window = self.windows.get(sensor_id)
        if window is not None and window.tail is not None:
            latest = window.tail.reading.timestamp
            if reading.timestamp <= latest:
                raise ValueError(
                    f"timestamp {reading.timestamp.isoformat()} is not after "
                    f"{latest.isoformat()} for sensor {sensor_id}")

        if window is None:
            window = LinkedWindow(self.capacity)
            self.windows[sensor_id] = window

        # The baseline comes from retained previous readings only; the incoming
        # reading is classified first and appended afterwards.
        prior_size = window.size
        baseline = window.mean()
        if prior_size < self.min_history:
            status = "WARMUP"
            baseline_text = ""
            deviation_text = ""
        else:
            deviation = abs(value - baseline)  # Compare unrounded values.
            status = "ALERT" if deviation >= self.threshold else "OK"
            baseline_text = f"{baseline:.2f}"
            deviation_text = f"{deviation:.2f}"

        evicted = window.append(reading)
        return {
            "timestamp": reading.timestamp.isoformat(),
            "sensor_id": sensor_id,
            "value": f"{value:.2f}",
            "baseline_mean": baseline_text,
            "abs_deviation": deviation_text,
            "status": status,
            "window_size_after": window.size,
            "evicted_value": "" if evicted is None else f"{evicted.value:.2f}",
        }


INPUT_HEADER = ["timestamp", "sensor_id", "value"]


def read_readings(path):
    """Stream CSV rows. Valid ISO naive timestamps, nonblank IDs, finite floats."""
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != INPUT_HEADER:
            raise ValueError(
                f"expected header {','.join(INPUT_HEADER)}; found {reader.fieldnames}")
        for line, row in enumerate(reader, start=2):
            # Extra columns land under the None key; short rows leave None values.
            if None in row:
                raise ValueError(f"row {line}: too many fields")
            if any(row[name] is None for name in INPUT_HEADER):
                raise ValueError(f"row {line}: too few fields")

            raw_timestamp = row["timestamp"].strip()
            try:
                timestamp = datetime.fromisoformat(raw_timestamp)
            except ValueError as error:
                raise ValueError(
                    f"row {line}: bad timestamp {raw_timestamp!r}") from error
            if timestamp.tzinfo is not None:
                raise ValueError(
                    f"row {line}: timestamp must be timezone naive")

            sensor_id = row["sensor_id"].strip()
            if not sensor_id:
                raise ValueError(f"row {line}: sensor_id is blank")

            raw_value = row["value"].strip()
            try:
                value = float(raw_value)
            except ValueError as error:
                raise ValueError(
                    f"row {line}: bad value {raw_value!r}") from error
            if not math.isfinite(value):
                raise ValueError(
                    f"row {line}: value {raw_value!r} is not finite")

            # Yield one object at a time; the input is never held in memory.
            yield Reading(timestamp, sensor_id, value)


FIELDS = ["timestamp", "sensor_id", "value", "baseline_mean", "abs_deviation",
          "status", "window_size_after", "evicted_value"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path,
                        default=Path(__file__).with_name("sensor_readings.csv"))
    parser.add_argument("--output", type=Path, default=Path("alerts.csv"))
    args = parser.parse_args()
    monitor = StreamMonitor()
    count = alerts = 0
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for reading in read_readings(args.input):
            row = monitor.process(reading)
            writer.writerow(row)
            count += 1
            alerts += row["status"] == "ALERT"
    print(f"Processed {count} readings; {alerts} alerts.")


if __name__ == "__main__":
    main()
