"""DATA 200 - Object-Oriented Programming Homework Starter

Case study: Community Maker Lab Equipment Checkout System

Student instructions
--------------------
1. Read the case study in the homework PDF before completing this file.
2. Replace every TODO and `pass` with working Python code.
3. Keep the requested public names unchanged so the supplied tests can run.
4. Add at least five tests of your own, including normal and edge cases.
5. Do not look at the solution file until after submitting your attempt.
"""

from __future__ import annotations


class Member:
    """Represent one registered Maker Lab member.

    Required constructor inputs:
        member_id: non-empty string
        name: non-empty string

    Required read-only property:
        display_name -> "<name> (<member_id>)"
    """

    def __init__(self, member_id: str, name: str) -> None:
        # TODO: Validate both inputs, then create instance attributes.
        if not isinstance(member_id, str):
            raise TypeError("Member ID should be a string")
        if not member_id.strip():
            raise ValueError("Member ID can not be blank")
        if not isinstance(name, str):
            raise TypeError("Member name should be a string")
        if not name.strip():
            raise ValueError("Member name can not be blank")

        self._member_id = member_id
        self._name = name

    @property
    def display_name(self) -> str:
        # TODO: Return the computed display label. Do not add a setter.
        return f"{self._name} ({self._member_id})"


class Equipment:
    """Represent one independently existing piece of lab equipment.

    Class attribute:
        objects_created - count successfully initialized Equipment objects.

    Instance state:
        asset_tag, name, _usage_hours, _available

    Required public interface:
        usage_hours property with validated setter
        available read-only property
        add_usage(hours), checkout(), return_item()
        valid_asset_tag(value) static method
    """

    objects_created = 0

    def __init__(self, asset_tag: str, name: str, usage_hours: int = 0) -> None:
        # TODO: Use valid_asset_tag. Reject blank names.
        # TODO: Assign usage_hours through its property setter.
        # TODO: New equipment starts available.
        # TODO: Increment objects_created only after successful initialization.

        if not self.valid_asset_tag(asset_tag):
            raise ValueError(
                "Asset tag must contain a hyphen and be at least five (5) characters long.")
        if not isinstance(name, str):
            raise TypeError("Name should be a string")
        if not name.strip():
            raise ValueError("Name can not be Blank/Empty")

        self.asset_tag = asset_tag
        self.name = name
        self.usage_hours = usage_hours
        self._available = True

        Equipment.objects_created += 1

    @staticmethod
    def valid_asset_tag(value: object) -> bool:
        """Return True for tags such as 'EQ-101' or 'TOOL-22'.

        Rules: value must be a string, contain a hyphen, and have at least
        five characters. Invalid types return False rather than raising.
        """
        # TODO: Implement without using self or cls.
        return isinstance(value, str) and "-" in value and len(value) >= 5

    @property
    def usage_hours(self) -> int:
        # TODO: Return the backing attribute.
        return self._usage_hours

    @usage_hours.setter
    def usage_hours(self, value: int) -> None:
        # TODO: Reject bool and non-int values with TypeError.
        # TODO: Reject negative integers with ValueError.
        # TODO: Store the value in _usage_hours (avoid property recursion).
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError("Usage hours should be an integer only.")
        if value < 0:
            raise ValueError("Usage hours can not be in negative.")
        self._usage_hours = value

    @property
    def available(self) -> bool:
        # TODO: Return _available. Deliberately do not create a public setter.
        return self._available

    def add_usage(self, hours: int) -> None:
        # TODO: Validate through the existing usage_hours rules.
        # Hint: self.usage_hours = self.usage_hours + hours
        self.usage_hours = self.usage_hours + hours

    def checkout(self) -> None:
        # TODO: Reject checkout when already unavailable.
        # TODO: Change the internal availability state.
        if not self._available:
            raise ValueError(
                "Equipment is not available as it is already checked out.")
        self._available = False

    def return_item(self) -> None:
        # TODO: Reject return when already available.
        # TODO: Change the internal availability state.
        if self._available:
            raise ValueError("Equipment is already available.")
        self._available = True


class MakerLab:
    """Aggregate Equipment objects that can exist outside this lab.

    Instance state:
        name, _equipment

    Required public interface:
        add_equipment, remove_equipment, find_available, equipment_count

    Relationship requirement:
        This is AGGREGATION. Removing an Equipment reference must not destroy
        the Equipment object; return the removed object to the caller.
    """

    def __init__(self, name: str) -> None:
        # TODO: Validate name and initialize an empty collection.
        if not isinstance(name, str):
            raise TypeError("Lab name should always be a string")
        if not name.strip():
            raise ValueError("Lab name can not be blank or empty")
        self.name = name
        self._equipment: list[Equipment] = []

    def add_equipment(self, item: Equipment) -> None:
        # TODO: Accept Equipment objects only.
        # TODO: Reject a duplicate asset_tag.
        if not isinstance(item, Equipment):
            raise TypeError("Only Equipment objects can be added to the lab.")

        if any(existing.asset_tag == item.asset_tag for existing in self._equipment):
            raise ValueError(
                f"Duplicate asset tag, Equipment with asset tag '{item.asset_tag}' already exists in the lab.")
        self._equipment.append(item)

    def remove_equipment(self, asset_tag: str) -> Equipment:
        # TODO: Find the item or raise LookupError.
        # TODO: Reject removal while the item is checked out.
        # TODO: Remove and return the same object.
        for i in self._equipment:
            if i.asset_tag == asset_tag:
                if not i.available:
                    raise ValueError(
                        "Cannot remove equipment that is currently checked out.")
                self._equipment.remove(i)
                return i
        raise LookupError(
            f"Equipment with asset tag '{asset_tag}' was not found.")

    def find_available(self, asset_tag: str) -> Equipment | None:
        # TODO: Return the matching available item, otherwise None.
        for i in self._equipment:
            if i.asset_tag == asset_tag and i.available:
                return i
        return None

    @property
    def equipment_count(self) -> int:
        # TODO: Return the current collection size. No public setter.
        return len(self._equipment)


class Loan:
    """Represent one checkout lifecycle for one Member and Equipment object.

    Constructor state:
        member, equipment, start_usage_hours, _active

    Required public interface:
        active read-only property
        complete(hours_used)
    """

    def __init__(self, member: Member, equipment: Equipment) -> None:
        # TODO: Type-check both objects.
        # TODO: Store references and starting usage hours; start active.
        if not isinstance(member, Member):
            raise TypeError("member must be an object in Member")
        if not isinstance(equipment, Equipment):
            raise TypeError("equipment must be an object in Equipment")
        self.member = member
        self.equipment = equipment
        self.start_usage_hours = equipment.usage_hours
        self._active = True

    @property
    def active(self) -> bool:
        # TODO: Return _active. No public setter.
        return self._active

    def complete(self, hours_used: int) -> None:
        # TODO: Reject repeated completion.
        # TODO: Add usage, return equipment, then mark the loan inactive.
        # Important: validate before leaving objects partly changed.
        if not self._active:
            raise ValueError("Loan has already been completed successfulyy.")

        # Validation befro making changes
        if isinstance(hours_used, bool) or not isinstance(hours_used, int):
            raise TypeError("Usage hours should be an integer only.")
        if hours_used < 0:
            raise ValueError("Usage hours can not be negative (< 0).")
        if self.equipment.available:
            raise ValueError(
                "Equipment is already available, cannot complete loan.")
        self.equipment.add_usage(hours_used)
        self.equipment.return_item()
        self._active = False


class CheckoutService:
    """Coordinate lab checkouts and compose active Loan objects.

    Instance state:
        lab, _active_loans (dictionary keyed by asset tag)

    Required public interface:
        start_loan, end_loan, active_loan_count

    Relationship requirement:
        The service COMPOSES Loan objects by creating them inside start_loan.
    """

    def __init__(self, lab: MakerLab) -> None:
        # TODO: Require a MakerLab and create an empty active-loan dictionary.
        if not isinstance(lab, MakerLab):
            raise TypeError("lab must be an object in MakerLab")
        self.lab = lab
        self._active_loans: dict[str, Loan] = {}

    def start_loan(self, member: Member, asset_tag: str) -> Loan:
        # TODO: Reject an asset tag already in _active_loans.
        # TODO: Find available equipment or raise LookupError.
        # TODO: Checkout the item, create a Loan, store it, and return it.
        if not isinstance(member, Member):
            raise TypeError("member must be an object in Member")
        if asset_tag in self._active_loans:
            raise ValueError(
                f"Asset tag '{asset_tag}' is already checked out and has an active loan.")

        equipment = self.lab.find_available(asset_tag)
        if equipment is None:
            raise LookupError(
                f"Equipment with asset tag '{asset_tag}' is not available for checkout.")

        equipment.checkout()
        loan = Loan(member, equipment)
        self._active_loans[asset_tag] = loan
        return loan

    def end_loan(self, asset_tag: str, hours_used: int) -> Loan:
        # TODO: Find active Loan or raise LookupError.
        # TODO: Complete it, remove it from the dictionary, and return it.
        if asset_tag not in self._active_loans:
            raise LookupError(
                f"No active loan found for asset tag '{asset_tag}'.")

        loan = self._active_loans[asset_tag]
        loan.complete(hours_used)
        del self._active_loans[asset_tag]
        return loan

    @property
    def active_loan_count(self) -> int:
        # TODO: Return the dictionary size. No public setter.
        return len(self._active_loans)


def print_lab_report(lab: MakerLab, service: CheckoutService) -> None:
    """Print a short lab status report.

    TODO: This is deliberately a standalone function. Print lab name,
    equipment_count, and active_loan_count using public interfaces.
    """
    print(f"Lab Name: {lab.name}")
    print(f"Total Equipment Count: {lab.equipment_count}")
    print(f"Active Loan Count: {service.active_loan_count}")


def main() -> None:
    """Create a normal demonstration after implementing every TODO.

    Suggested sequence:
        1. Create a MakerLab, two Equipment objects, and one Member.
        2. Aggregate both equipment objects into the lab.
        3. Start and end one Loan through CheckoutService.
        4. Print availability, usage hours, and the lab report.
        5. Add at least five edge-case tests with try/except or assertions.
    """
    # TODO: Write the demonstration and tests.
    lab = MakerLab("San Jose State University Maker Lab")
    Printer_3D = Equipment("MACH-001", "3D Printer", 10)
    GPU_Miner = Equipment("GPU-002", "GPU Miner", 20)
    member1 = Member("M-009", "Aimaan Khan")

    lab.add_equipment(Printer_3D)
    lab.add_equipment(GPU_Miner)

    service = CheckoutService(lab)
    loan1 = service.start_loan(member1, "MACH-001")
    print(f"{Printer_3D.name} available after checkout: {Printer_3D.available}")

    completed_loan = service.end_loan("MACH-001", 5)

    print(f"{completed_loan.equipment.name} available after return: {completed_loan.equipment.available}")
    print(
        f"Usage hours for {completed_loan.equipment.name}: {completed_loan.equipment.usage_hours}")
    print_lab_report(lab, service)

    # Additional tests: normal and edge cases.
    assert member1.display_name == "Aimaan Khan (M-009)"
    assert Equipment.valid_asset_tag("EQ-101") is True
    assert Equipment.valid_asset_tag("BAD") is False
    assert lab.equipment_count == 2
    assert service.active_loan_count == 0
    assert completed_loan.active is False
    assert Printer_3D.usage_hours == 15

    try:
        Equipment("BAD", "Invalid Equipment")
        assert False, "Invalid asset tag should raise ValueError"
    except ValueError:
        pass

    try:
        Printer_3D.usage_hours = -1
        assert False, "Negative usage hours should raise ValueError"
    except ValueError:
        pass

    try:
        lab.add_equipment(Equipment("MACH-001", "Duplicate Tag"))
        assert False, "Duplicate asset tags should raise ValueError"
    except ValueError:
        pass

    try:
        service.end_loan("MACH-001", 1)
        assert False, "Ending a missing loan should raise LookupError"
    except LookupError:
        pass

    try:
        lab.remove_equipment("MISSING-1")
        assert False, "Missing equipment should raise LookupError"
    except LookupError:
        pass

    print("All tests passed.")


if __name__ == "__main__":
    main()
