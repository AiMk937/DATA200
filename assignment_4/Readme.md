# DATA 200 Homework 4 - Campus IT Help Desk

A hand-built stack and circular queue used together to model a help desk
ticket workflow: pending tickets are served oldest-first, and a processed
ticket can be "undone" to reopen the most recently closed one.

## Files

- `help_desk_homework_solution.py` - the completed submission. Contains
  `MyStack`, `MyQueue`, `CampusHelpDesk`, the required scenario runner, and
  the required edge-case tests.
- `DESIGN_REFLECTION.md` - write-up explaining the design decisions behind
  the implementation.

## How to run

```
python help_desk_homework_template.py
```

No input is required. Running the file prints, in order:

1. The results of the edge-case tests (stack underflow, queue underflow,
   queue overflow, and wrap-around FIFO order).
2. The required scenario: submitting three tickets, processing two,
   undoing the last processed ticket, submitting one more ticket, and
   inspecting the next pending ticket - with `status()` printed after
   every step.

The final printed state matches the assignment spec exactly:

```
pending = ['Printer jam', 'Password reset', 'Software install']
processed = ['Wi-Fi unavailable']
pending_count = 3
processed_count = 1
```