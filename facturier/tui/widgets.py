"""
Some widgets used in the tui.
"""
from enum import auto, IntFlag
from typing import Any, Callable, Tuple

import urwid


class StackMainLoop(urwid.MainLoop):
    """A MainLoop wrapper that has a stack of widgets to push/pop."""
    def __init__(self, widget: urwid.Widget, *args, **kwargs):
        super().__init__(widget, *args, **kwargs)
        self.stack = [widget]

    def push_widget(self, widget: urwid.Widget):
        """Make the pushed widget the current one."""
        self.stack.append(widget)
        self.widget = widget

    def pop_widget(self):
        """Pop the current widget, and exit the loop when empty."""
        if not self.stack:
            raise Exception("Empty view stack.")
        self.stack.pop()
        if not self.stack:
            raise urwid.ExitMainLoop("View stack emptied.")
        self.widget = self.stack[-1]


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


class CallbackEditType(IntFlag):
    """Types of callbacks handled by the CallbackEdit widget."""
    CANCELED = auto()
    VALIDATED = auto()
    CHANGED = auto()
    UP = auto()
    DOWN = auto()


class CallbackEdit(urwid.Edit):
    """An Edit widget with a callback on text change."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.callbacks: Tuple[Callable[[], Any], CallbackEditType] = []

    def call_callbacks(self, cbtype):
        """Call any callback matching the given cbtype."""
        for callback, cbtype_cb in self.callbacks:
            if cbtype in cbtype_cb:
                callback(cbtype)

    def register_callback(self, callback: Callable[[], Any],
                          cbtype: CallbackEditType):
        """Add a function to call when the value changed."""
        self.callbacks.append((callback, cbtype))

    def keypress(self, size, key):
        """Call the callbacks when the value changes."""
        if key == 'esc':
            self.call_callbacks(CallbackEditType.CANCELED)
            return None
        if key == 'enter':
            self.call_callbacks(CallbackEditType.VALIDATED)
            return None
        if key == 'up':
            self.call_callbacks(CallbackEditType.UP)
            return None
        if key == 'down':
            self.call_callbacks(CallbackEditType.DOWN)
            return None
        old = self._edit_text
        output = super().keypress(size, key)
        new = self._edit_text
        if old != new:
            self.call_callbacks(CallbackEditType.CHANGED)
            return None
        return output


class Select(urwid.Button):
    """An Edit widget with options to choose from."""
    def __init__(self, name, options, value, *args, **kwargs):
        super().__init__(('ui', "Select a {} [{}]".format(name, value)), *args,
                         **kwargs)
        self.options = options
        self.value = value
        self.stack_main_loop = None
        self.name = name
        self.search = CallbackEdit(caption=('ui', self.name + ": "),
                                   edit_text=self.value or '')
        self.search.register_callback(self.set_results,
                                      CallbackEditType.CHANGED)
        self.search.register_callback(self.cancel_select,
                                      CallbackEditType.CANCELED)
        self.search.register_callback(self.validate_select,
                                      CallbackEditType.VALIDATED)
        self.search.register_callback(
            self.up_down_select, CallbackEditType.UP | CallbackEditType.DOWN)
        self.pile = urwid.Pile([])
        self.select_index = 0
        urwid.connect_signal(self, 'click', self.show_popup)
        self.set_results()

    def cancel_select(self, cbtype):
        """Called when the CallbackEdit widget is canceled."""
        raise Exception("Canceled")

    def validate_select(self, cbtype):
        """Called when the CallbackEdit widget is validated."""
        raise Exception("Validated")

    def up_down_select(self, cbtype):
        """Called when arrow up or down is pressed."""
        raise Exception("Up-Downed.", cbtype)

    def set_stack_main_loop(self, stack_main_loop: StackMainLoop):
        """Set the StackMainLoop to show the 'popup' in."""
        self.stack_main_loop = stack_main_loop

    def set_results(self, cbtype=None):
        """Update the pile's results given the search input."""
        results = []
        search = self.search.edit_text.lower()
        options = self.pile.options(height_type='pack', height_amount=None)
        index = 0
        for option in self.options:
            if search in option.lower():
                results.append((urwid.Text(option), options))
        self.pile.contents = results

    def show_popup(self, target):
        """Show the popup."""
        if self.stack_main_loop is None:
            raise Exception("Please set StackMainLoop for this widget.")
        self.stack_main_loop.push_widget(
            urwid.Frame(self.pile, self.search, None, 'header'))
