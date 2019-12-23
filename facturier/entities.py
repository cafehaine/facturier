"""
Entities used to store data between executions.
"""
from decimal import Decimal
from datetime import date
from random import choice

from pony.orm import commit, Database, db_session, Optional, PrimaryKey, Required, Set

DB = Database()

FAKE_NAMES = [
    'MARY', 'PATRICIA', 'LINDA', 'BARBARA', 'ELIZABETH', 'JENNIFER', 'MARIA',
    'SUSAN', 'MARGARET', 'DOROTHY', 'JAMES', 'JOHN', 'ROBERT', 'MICHAEL',
    'WILLIAM', 'DAVID', 'RICHARD', 'CHARLES', 'JOSEPH', 'THOMAS'
]


class Client(DB.Entity):
    """A client."""
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    address = Optional(str)
    postal_code = Optional(str)
    city = Optional(str)
    country = Optional(str)
    tel = Optional(str)
    email = Optional(str)
    bills = Set('Bill')


@db_session
def generate_random_clients(count=50):
    """Generate random clients for tests."""
    for _ in range(count):
        Client(name="{} {}".format(
            choice(FAKE_NAMES).capitalize(), choice(FAKE_NAMES)))
    commit()


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
