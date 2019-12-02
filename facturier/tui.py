"""
A set of classes and functions to create a terminal ui.
"""

from enum import Enum, auto
from typing import Any, Optional, List, Dict

from pony.orm import db_session
import urwid

from entities import Client


class FieldType(Enum):
    """Types of fields handled by the forms."""
    TEXT = auto()


class Field:
    """A field for a form."""
    def __init__(self,
                 ftype: FieldType,
                 label: str,
                 value: Optional[Any] = None):
        self.type = ftype
        self.label = label
        self.value = value


class NextPile(urwid.Pile):
    """
    A pile that selects the next widget when pressing return or tab.

    It also allows going back by pressing shift+tab, and closes when pressing
    esc.
    """
    def keypress(self, size, key):
        """On any keypress."""
        if key == 'esc':
            raise urwid.ExitMainLoop()
        if key == 'tab' or key == 'enter' and isinstance(
                self.focus_item, urwid.Edit):
            try:
                self.focus_position += 1
            except IndexError:
                pass
            return None
        if key == 'shift tab':
            try:
                if self.focus_position > 1:
                    self.focus_position -= 1
            except IndexError:
                pass
            return None
        return super().keypress(size, key)


def _show_form(title: str, fields: List[Field]) -> Dict[str, Any]:
    """Show a form and return all the fields and their values."""
    results: Dict[str, Any] = {}
    form_fields: List[urwid.Widget] = [urwid.Text(title + "\n")]

    for field in fields:
        widget: urwid.Widget
        if field.type == FieldType.TEXT:
            widget = urwid.Edit(caption=field.label + ":\n",
                                edit_text=field.value)
        else:
            raise Exception("Unhandled FieldType %s", field.type)
        form_fields.append(widget)

    exit_type = "Cancel"

    def on_button_click(button):
        exit_type = button.get_label()
        raise urwid.ExitMainLoop()

    button = urwid.Button("OK", on_press=on_button_click)

    form_fields.append(button)
    pile = NextPile(form_fields)
    top = urwid.Filler(pile, valign='top')
    urwid.MainLoop(top).run()
    return {}


@db_session
def edit_client(client: Client, new: bool = False) -> Client:
    """Edit an existing client entity."""
    output = _show_form("Edit client" if new else "New client", [
        Field(FieldType.TEXT, 'Name', client.name),
        Field(FieldType.TEXT, 'Address', client.address),
        Field(FieldType.TEXT, 'Postal code', client.postal_code),
        Field(FieldType.TEXT, 'City', client.city),
        Field(FieldType.TEXT, 'Country', client.country),
    ])
    #TODO treat output
    return client


@db_session
def new_client() -> Client:
    """Create a new client entity and show a form to edit it."""
    client = Client(name="", address="", postal_code="", city="", country="")
    return edit_client(client, True)
