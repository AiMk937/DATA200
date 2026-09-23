# Reflection: Linked-List Sensor Stream Monitor

## 1. Head removal and tail insertion

The window is FIFO: the newest reading arrives at one end and the oldest leaves
at the other, and nothing is read or removed from the middle. A singly linked
list holding both `head` and `tail` matches that exactly. Appending is
`tail.next = node; tail = node`, and evicting is `head = head.next`. Only
forward traversal is needed, so `prev` pointers would be dead weight.

## 2. Why `list.pop(0)` costs O(w)

A list stores element pointers in one contiguous block. Removing index 0
leaves a hole, so every remaining element shifts down one slot to close it:
`w - 1` moves, or O(w). Removing a linked list's head rebinds a single
reference. No other node is touched, so the cost stays constant however large
the window grows.

## 3. The running sum

`mean()` runs once per reading. Summing by traversal would cost O(w) each time
and push the program to O(Nw). Adjusting `total` by `+ value` on append and
`- value` on removal reduces `mean()` to one division, keeping the per-reading
cost fixed. Resetting `total` to `0.0` when the window empties also stops
floating-point drift accumulating.

## 4. Why a linked list is not automatically better

Each reading needs a `Node` with its own header, instance dictionary and `next`
pointer, on top of the `Reading` it wraps: far more memory per element than one
array pointer. Those nodes also sit wherever the allocator put them, so
traversal chases pointers across cache lines instead of streaming contiguous
memory. The linked list wins only on the asymptotic cost of head removal. At
`w = 5` the list's shift is a fast `memmove` and likely quicker in practice.
Asymptotics describe growth, not constants.

## 5. Production choice

`collections.deque` for a general queue: implemented in C as a doubly linked
list of fixed-size blocks, it gives O(1) at both ends without a Python object
per element. For dense numeric data at high rates I would preallocate a NumPy
ring buffer and advance two indices, avoiding allocation entirely. NumPy arrays
remain right for batch model training because training reads whole columns at
once and benefits from contiguous memory and vectorized arithmetic; it never
needs O(1) eviction from the front.

## 6. Expected cost

Each reading costs one dictionary lookup, one O(1) append, at most one O(1)
eviction, and fixed-cost scalar arithmetic, so processing `N` readings is O(N).
Retained history is capped at `w` nodes per sensor, giving O(Sw) space for `S`
sensors, independent of `N`. Report rows stream to disk through
`csv.DictWriter`, so output never accumulates in memory.
