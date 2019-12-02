"""
A set of classes and functions to create a terminal ui.
"""

from enum import Enum, auto
from typing import Any, Optional, List, Dict

from pony.orm import commit, db_session
import urwid

from facturier.entities import Client

PALETTE = [('ui', 'light green', 'default')]


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
    form_fields: Dict[str, urwid.Widget] = {}
    widgets = [urwid.Text(('ui', title + "\n"))]

    for field in fields:
        widget: urwid.Widget
        if field.type == FieldType.TEXT:
            widget = urwid.Edit(caption=('ui', field.label + ":\n"),
                                edit_text=field.value)
        else:
            raise Exception("Unhandled FieldType %s", field.type)
        form_fields[field.label] = widget

    exit_type = "Cancel"

    def on_button_click(button):
        exit_type = button.get_label()
        raise urwid.ExitMainLoop()

    widgets.extend(form_fields.values())
    button = urwid.Button(('ui',"OK"), on_press=on_button_click)
    widgets.append(button)

    pile = NextPile(widgets)
    top = urwid.Filler(pile, valign='top')
    urwid.MainLoop(top, PALETTE).run()
    output: Dict[str, Any] = {}
    for label, field in form_fields.items():
        #TODO handle other input types
        output[label] = field.edit_text
    return output


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

    commit()
    return client


@db_session
def new_client() -> Client:
    """Create a new client entity and show a form to edit it."""
    client = Client(name="", address="", postal_code="", city="", country="")
    return edit_client(client, True)
