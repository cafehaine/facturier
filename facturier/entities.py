"""
Entities used to store data between executions.
"""
from decimal import Decimal
from datetime import date

from pony.orm import Database, Optional, PrimaryKey, Required, Set

DB = Database()


class Client(DB.Entity):
    """A client."""
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    address = Optional(str)
    postal_code = Optional(str)
    city = Optional(str)
    country = Optional(str)
    bills = Set('Bill')


class Bill(DB.Entity):
    """A bill."""
    id = PrimaryKey(int, auto=True)
    client = Optional(Client)
    date = Optional(date)
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
    product = Optional(str)
    quantity = Optional(int)
    unit_cost = Optional(Decimal, precision=10, scale=2)

    def get_total(self):
        """Return the total cost of this row."""
        return self.quantity * self.unit_cost
