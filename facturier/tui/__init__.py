"""
A set of classes and functions to create a terminal ui.
"""

from datetime import date
from enum import Enum, auto
from typing import Any, Optional, List, Dict

from pony.orm import commit, db_session, select
import urwid

from facturier.entities import Bill, Client
from .widgets import Date, NextPile, Select, StackMainLoop

PALETTE = [('ui', 'light green', 'default')]


class FieldType(Enum):
    """Types of fields handled by the forms."""
    TEXT = auto()
    SELECT = auto()
    DATE = auto()


class Field:
    """A field for a form."""
    def __init__(self,
                 ftype: FieldType,
                 label: str,
                 value: Optional[Any] = None,
                 **kwargs: Dict[str, Any]):
        self.type = ftype
        self.label = label
        self.value = value
        self.kwargs = kwargs


def _show_form(title: str, fields: List[Field]) -> Dict[str, Any]:
    """Show a form and return all the fields and their values."""
    results: Dict[str, Any] = {}
    form_fields: Dict[str, urwid.Widget] = {}
    widgets = [urwid.Text(('ui', title + "\n"))]
    to_wire_stack = []

    for field in fields:
        widget: urwid.Widget
        if field.type == FieldType.TEXT:
            widget = urwid.Edit(caption=('ui', field.label + ":\n"),
                                edit_text=field.value)
        elif field.type == FieldType.SELECT:
            widget = Select(field.label, field.kwargs['choices'], field.value)
            to_wire_stack.append(widget)
        elif field.type == FieldType.DATE:
            widget = Date(field.label, field.value)
        else:
            raise Exception("Unhandled FieldType %s", field.type)
        form_fields[field.label] = widget

    exit_type = "Cancel"

    def on_button_click(button):
        nonlocal exit_type
        exit_type = button.get_label()
        raise urwid.ExitMainLoop()

    widgets.extend(form_fields.values())
    button = urwid.Button(('ui', "OK"), on_press=on_button_click)
    widgets.append(button)

    pile = NextPile(widgets)
    top = urwid.Filler(pile, valign='top')
    stack = StackMainLoop(top, PALETTE)
    for widget in to_wire_stack:
        widget.set_stack_main_loop(stack)
    stack.run()
    if exit_type == "Cancel":
        return {}
    for label, field in form_fields.items():
        if isinstance(field, Date):
            results[label] = field.get_date()
        elif isinstance(field, Select):
            results[label] = field.value
        else:
            results[label] = field.edit_text
    return results


@db_session
def edit_client(client: Client, new: bool = False):
    """Edit an existing client entity."""
    output = _show_form("Edit client" if not new else "New client", [
        Field(FieldType.TEXT, 'Name', client.name),
        Field(FieldType.TEXT, 'Address', client.address),
        Field(FieldType.TEXT, 'Postal code', client.postal_code),
        Field(FieldType.TEXT, 'City', client.city),
        Field(FieldType.TEXT, 'Country', client.country),
        Field(FieldType.TEXT, 'Telephone', client.tel),
        Field(FieldType.TEXT, 'E-Mail', client.email),
    ])

    for label, value in output.items():
        if label == "Name":
            client.name = value
        elif label == "Address":
            client.address = value
        elif label == "Postal code":
            client.postal_code = value
        elif label == "City":
            client.city = value
        elif label == "Country":
            client.country = value
        elif label == "Telephone":
            client.tel = value
        elif label == "E-Mail":
            client.email = value

    commit()


@db_session
def new_client() -> Client:
    """Create a new client entity and show a form to edit it."""
    client = Client(name="", address="", postal_code="", city="", country="")
    edit_client(client, True)
    return client


@db_session
def edit_bill(bill: Bill, new: bool = False):
    """Edit an existing bill."""
    # Edit basic information (client, date)
    output = _show_form("Edit bill" if not new else "New bill", [
        Field(FieldType.SELECT,
              'Client',
              bill.client.name if bill.client is not None else None,
              choices=select(c.name for c in Client)[:]),
        Field(FieldType.DATE, 'Date', bill.date)
    ])

    for label, value in output.items():
        if label == "Client":
            bill.client = Client.get(name=value)
        elif label == "Date":
            bill.date = value

    commit()


@db_session()
def new_bill() -> Bill:
    """Create a new bill entity and show a form to edit it."""
    bill = Bill(date=date.today())
    edit_bill(bill, True)
    return bill
