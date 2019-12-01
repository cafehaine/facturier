from enum import Enum, auto
from typing import Any, Optional, List, Dict

from pony.orm import db_session
import urwid

from .entities import Client


class FieldType(Enum):
    TEXT = auto()


class Field:
    def __init__(self,
                 type: FieldType,
                 label: str,
                 value: Optional[Any] = None):
        self.type = type
        self.label = label
        self.value = value


def _show_form(title: str, fields: List[Field]) -> Dict[str, Any]:
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

    buttons = urwid.Columns([
        urwid.Button("Cancel", on_press=on_button_click),
        urwid.Button("OK", on_press=on_button_click),
    ])

    form_fields.append(buttons)
    pile = urwid.Pile(form_fields)
    top = urwid.Filler(pile, valign='top')
    urwid.MainLoop(top).run()


@db_session
def edit_client(client: Client, new: bool = False) -> Client:
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
    client = Client(name="", address="", postal_code="", city="", country="")
    return edit_client(client, True)
