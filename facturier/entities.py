"""
Entities used to store data between executions.
"""
from decimal import Decimal

from pony.orm import Database, PrimaryKey, Required, Set

DB = Database()


class Client(DB.Entity):
    """A client."""
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    address = Required(str)
    postal_code = Required(str)
    city = Required(str)
    country = Required(str)
    bills = Set('Bill')


class Bill(DB.Entity):
    """A bill."""
    id = PrimaryKey(int, auto=True)
    client = Required(Client)
    entries = Set('BillEntry')

    def get_total(self):
        """Return the total cost of this bill."""
        total = 0
        for entry in self.entries:
            total += entry.get_total()
        return total


class BillEntry(DB.Entity):
    """A single row in the bill."""
    #TODO primary key with the Bill and the content instead of an ID?
    id = PrimaryKey(int, auto=True)
    bill = Required(Bill)
    product = Required(str)
    quantity = Required(int)
    unit_cost = Required(Decimal, precision=10, scale=2)

    def get_total(self):
        """Return the total cost of this row."""
        return self.quantity * self.unit_cost
