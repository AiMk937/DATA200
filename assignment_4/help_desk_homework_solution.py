"""DATA 200 Homework: Campus IT Help Desk (20 marks)

Complete every TODO. Do not replace MyStack or MyQueue with Python's deque,
queue.Queue, or another ready-made stack/queue class.
"""


class MyStack:
    """LIFO container used for processed-ticket history."""

    _INITIAL_CAPACITY = 4

    def __init__(self) -> None:
        # Preallocate a fixed-size list of empty slots ourselves.
        self._capacity = MyStack._INITIAL_CAPACITY
        self._data: list = [None] * self._capacity
        self._size = 0  # number of slots in use; also the index of the top + 1

    def _grow(self) -> None:
        """Manually copy every item into a larger array when full."""
        new_capacity = self._capacity * 2
        new_data = [None] * new_capacity
        index = 0
        while index < self._size:
            new_data[index] = self._data[index]
            index += 1
        self._data = new_data
        self._capacity = new_capacity

    def push(self, item: str) -> None:
        """Add item to the top of the stack."""
        if self._size == self._capacity:
            self._grow()
        self._data[self._size] = item
        self._size += 1

    def pop(self) -> str:
        """Remove and return the top item; raise IndexError if empty."""
        if self.is_empty():
            raise IndexError("stack is empty")
        top_index = self._size - 1
        item = self._data[top_index]
        self._data[top_index] = None
        self._size -= 1
        return item

    def top(self) -> str:
        """Return the top item without removing it; raise IndexError if empty."""
        if self.is_empty():
            raise IndexError("stack is empty")
        return self._data[self._size - 1]

    def is_empty(self) -> bool:
        """Return True when the stack contains no items."""
        return self._size == 0

    def __len__(self) -> int:
        """Return the number of stack items."""
        return self._size

    def to_list(self) -> list[str]:
        """Return a copy ordered from bottom to top for display/testing."""
        # Build a fresh, exactly-sized array by hand and copy each used
        # slot in by index; no .append() involved.
        result = [None] * self._size
        index = 0
        while index < self._size:
            result[index] = self._data[index]
            index += 1
        return result


class MyQueue:
    """Fixed-capacity circular FIFO queue used for pending tickets."""

    def __init__(self, capacity: int) -> None:
        # Validate capacity and initialize the array, front, and size.
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self._capacity = capacity
        self._data: list[str | None] = [None] * capacity
        self._front = 0
        self._size = 0

    def enqueue(self, item: str) -> None:
        """Add item at the rear; raise OverflowError if full."""
        if self.is_full():
            raise OverflowError("queue is full")
        rear = (self._front + self._size) % self._capacity
        self._data[rear] = item
        self._size += 1

    def dequeue(self) -> str:
        """Remove and return the front item; raise IndexError if empty."""
        if self.is_empty():
            raise IndexError("queue is empty")
        item = self._data[self._front]
        self._data[self._front] = None
        self._front = (self._front + 1) % self._capacity
        self._size -= 1
        return item

    def first(self) -> str:
        """Return the front item without removing it; raise IndexError if empty."""
        if self.is_empty():
            raise IndexError("queue is empty")
        return self._data[self._front]

    def is_empty(self) -> bool:
        """Return True when the queue contains no items."""
        return self._size == 0

    def is_full(self) -> bool:
        """Return True when the queue has reached capacity."""
        return self._size == self._capacity

    def __len__(self) -> int:
        """Return the number of queue items."""
        return self._size

    def to_list(self) -> list[str]:
        """Return a copy in logical front-to-rear order."""
        # Do not return the physical array directly; walk `size` cells
        # starting at `front`, wrapping with modulo as needed. Build the
        # result as a preallocated array and fill it by index (no
        # .append()) so the logical order is assembled by hand.
        result = [None] * self._size
        offset = 0
        while offset < self._size:
            physical_index = (self._front + offset) % self._capacity
            result[offset] = self._data[physical_index]
            offset += 1
        return result


class CampusHelpDesk:
    """Coordinates pending tickets and processed-ticket history."""

    def __init__(self, capacity: int = 5) -> None:
        self._pending = MyQueue(capacity)
        self._history = MyStack()

    def submit_ticket(self, ticket: str) -> None:
        """Add a nonblank ticket to the pending queue."""
        if not ticket or not ticket.strip():
            raise ValueError("ticket text cannot be blank")
        self._pending.enqueue(ticket)

    def process_next(self) -> str:
        """Process the oldest pending ticket and save it in history."""
        ticket = self._pending.dequeue()
        self._history.push(ticket)
        return ticket

    def undo_last(self) -> str:
        """Reopen the latest processed ticket at the rear of pending."""
        ticket = self._history.pop()
        self._pending.enqueue(ticket)
        return ticket

    def next_ticket(self) -> str:
        """Return the next pending ticket without processing it."""
        return self._pending.first()

    def status(self) -> dict[str, object]:
        """Return pending tickets, processed history, and both counts."""
        pending = self._pending.to_list()
        processed = self._history.to_list()
        return {
            "pending": pending,
            "processed": processed,
            "pending_count": len(pending),
            "processed_count": len(processed),
        }


# Concept questions
# --------------------------------------------------------------------------
# Why does the pending collection require FIFO order?
#   Tickets must be handled in the order they arrive, so the earliest
#   submitted ticket has to be the first one a technician works on. A queue
#   enforces that "first in, first out" access pattern directly.
#
# Why does Undo Last Processed require LIFO order?
#   "Undo" only makes sense relative to the most recent action: if a
#   technician made a mistake, they want to reopen whichever ticket they
#   *just* closed, not the oldest one ever closed. A stack always exposes
#   the most recently pushed (processed) ticket on top, which is exactly
#   the "last in, first out" behavior undo needs.
#
# Why is the circular queue's physical array sometimes different from its
# logical front-to-rear order?
#   Because the array is reused instead of resized or shifted, the front of
#   the queue can sit at any index and the rear can wrap past the end of
#   the array back to index 0. The "logical" order is whatever you'd read
#   starting at `front` and walking `size` cells with wraparound (see
#   to_list()); the "physical" array itself keeps old values sitting after
#   the true front and can even be scrambled by wraparound, so reading it
#   left-to-right does not give the real queue order.


def run_edge_case_tests() -> None:
    """Exercise the required underflow, overflow, and wrap-around cases."""
    print("EDGE CASE TESTS")

    # Empty stack: pop() and top() must raise IndexError.
    empty_stack = MyStack()
    try:
        empty_stack.pop()
    except IndexError as error:
        print(f"MyStack.pop() on empty stack raised IndexError: {error}")
    try:
        empty_stack.top()
    except IndexError as error:
        print(f"MyStack.top() on empty stack raised IndexError: {error}")

    # Empty queue: dequeue() and first() must raise IndexError.
    empty_queue = MyQueue(capacity=2)
    try:
        empty_queue.dequeue()
    except IndexError as error:
        print(f"MyQueue.dequeue() on empty queue raised IndexError: {error}")
    try:
        empty_queue.first()
    except IndexError as error:
        print(f"MyQueue.first() on empty queue raised IndexError: {error}")

    # Full queue: enqueue() must raise OverflowError.
    full_queue = MyQueue(capacity=2)
    full_queue.enqueue("a")
    full_queue.enqueue("b")
    try:
        full_queue.enqueue("c")
    except OverflowError as error:
        print(f"MyQueue.enqueue() on full queue raised OverflowError: {error}")

    # Wrap-around: a sequence that crosses the physical array end must
    # still preserve FIFO order.
    wrap_queue = MyQueue(capacity=3)
    wrap_queue.enqueue("x")
    wrap_queue.enqueue("y")
    wrap_queue.enqueue("z")
    wrap_queue.dequeue()  # removes "x"; front now index 1
    wrap_queue.dequeue()  # removes "y"; front now index 2
    wrap_queue.enqueue("w")  # wraps rear back to index 0
    wrap_queue.enqueue("v")  # fills index 1
    print(f"Wrap-around queue logical order -> {wrap_queue.to_list()}")
    assert wrap_queue.to_list() == [
        "z", "w", "v"], "FIFO order broken across wrap"
    print("Wrap-around preserved FIFO order as expected.\n")


def run_required_scenario() -> None:
    """Run the required test sequence and print every state change."""
    desk = CampusHelpDesk(capacity=5)

    # Step 1: Submit three tickets in order.
    for ticket in ["Wi-Fi unavailable", "Password reset", "Printer jam"]:
        desk.submit_ticket(ticket)
    print("After submitting 3 tickets:")
    print(desk.status())

    # Step 2: Process two tickets.
    first_processed = desk.process_next()
    print(f"\nprocess_next() -> {first_processed!r}")
    print(desk.status())

    second_processed = desk.process_next()
    print(f"\nprocess_next() -> {second_processed!r}")
    print(desk.status())

    # Step 3: Undo the latest processed ticket. It must re-enter at the
    # rear of the pending queue.
    reopened = desk.undo_last()
    print(f"\nundo_last() -> {reopened!r}")
    print(desk.status())

    # Step 4: Submit one more ticket, then inspect the next pending ticket.
    desk.submit_ticket("Software install")
    print("\nAfter submitting 'Software install':")
    print(f"next_ticket() -> {desk.next_ticket()!r}")
    print(desk.status())


if __name__ == "__main__":
    run_edge_case_tests()
    run_required_scenario()
