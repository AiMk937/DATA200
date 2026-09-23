# Community Maker Lab Equipment Checkout System

A small object-oriented Python project modeling equipment checkout for a
university maker lab, built for DATA 200 (SJSU M.S. Applied Data Intelligence).

## Overview

The system tracks lab members, equipment, and checkout transactions ("loans")
through five collaborating classes:

| Class | Responsibility |
|---|---|
| `Member` | A registered lab user (`member_id`, `name`, computed `display_name`) |
| `Equipment` | One independently existing piece of lab equipment — tracks usage hours and availability, validates its own asset tag format |
| `MakerLab` | Aggregates `Equipment` objects; equipment can exist and be reused outside the lab |
| `Loan` | Represents the lifecycle of a single checkout transaction between a `Member` and an `Equipment` |
| `CheckoutService` | Orchestrates checkouts — creates and owns `Loan` objects, prevents double-checkout |

Plus one standalone function, `print_lab_report(lab, service)`, which is
intentionally **not** a method on any class — it reports status using only
the public interfaces of `MakerLab` and `CheckoutService`.

## Relationships

- **Aggregation** — `MakerLab` → `Equipment`. Removing equipment from a lab
  (`remove_equipment`) returns the same object rather than destroying it;
  equipment can outlive its lab.
- **Composition** — `CheckoutService` → `Loan`. Loans are created *inside*
  `start_loan` and have no meaning outside a service-managed transaction.
- **Association** — `Loan` → `Member`, `Loan` → `Equipment`,
  `CheckoutService` → `MakerLab`. Plain references passed in at construction
  time, with no ownership implied.

A full UML class diagram (attributes, methods, static-method notation, and
relationship types with multiplicity) accompanies this code.

## Design highlights

- All mutable state (`usage_hours`, `available`) is validated through
  properties, not exposed as raw public attributes.
- `Equipment.valid_asset_tag` is a `@staticmethod` — it doesn't need `self`
  and represents a pure format-checking rule, not per-instance behavior.
- `Loan.complete()` validates `hours_used` **before** mutating any state, so
  a rejected completion (e.g., negative hours) leaves the equipment's usage
  hours and availability completely unchanged.

## Running the project

```bash
python3 Maker_Lab_Homework_Starter.py
```

This runs the `main()` demonstration: creates a lab, adds two pieces of
equipment, registers a member, starts and completes a loan, prints a lab
report, then exercises eight edge cases with `assert` / `try`-`except`.

## Test coverage

| Test | Expected result |
|---|---|
| Valid checkout and completion | usage increases; equipment becomes available again |
| Invalid tag / negative usage | `ValueError` |
| Boolean usage value | `TypeError` (bool is rejected before the int check) |
| Duplicate asset tag | `ValueError` |
| Second checkout of the same item | `RuntimeError` (see note below) |
| Negative completion | rejected with no partial state change |
| Assigning `available` directly | `AttributeError` (read-only property) |
| Removing available equipment | same object is returned; lab's count decreases |

**Note on exception types:** checking out equipment that's already checked
out raises `RuntimeError`, not `ValueError`, both in `Equipment.checkout()`
and in `CheckoutService.start_loan()`. This is a deliberate choice —
`RuntimeError` fits an invalid *state transition* better than `ValueError`,
which is reserved for invalid *values*. If your rubric expects `ValueError`
specifically for this case, update those two `raise` statements.

## Academic integrity

This implementation was completed independently following the starter
file's TODOs; the reference solution was not consulted before submission.
