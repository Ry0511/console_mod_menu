from __future__ import annotations

from dataclasses import dataclass, field

from mods_base import (
    EInputEvent,
    KeybindOption,
    raw_keybinds,
    remove_next_console_line_capture,
)
from ui_utils import show_hud_message
from unrealsdk.hooks import Block

from console_mod_menu.draw import draw
from console_mod_menu.key_matching import KNOWN_KEYS, suggest_key

from . import (
    AbstractScreen,
    _handle_interactive_input,  # pyright: ignore[reportPrivateUsage]
    draw_standard_commands,
    handle_standard_command_input,
    pop_screen,
    push_screen,
)
from .option import OptionScreen


@dataclass
class InvalidNameScreen(AbstractScreen):
    name: str = field(init=False)
    parent: KeybindOptionScreen

    invalid_key: str
    suggested_key: str | None = field(init=False)

    def __post_init__(self) -> None:
        self.name = self.parent.option.display_name
        self.suggested_key = suggest_key(self.invalid_key)

    def draw(self) -> None:  # noqa: D102
        msg = f"'{self.invalid_key}' is not a known key name."
        if self.suggested_key is not None:
            msg += f" Did you mean '{self.suggested_key}'?"
        draw(msg)
        draw("")
        draw("[1] Discard changes")
        draw(f"[2] Use '{self.invalid_key}'")
        if self.suggested_key is not None:
            draw(f"[3] Use '{self.suggested_key}'")

    def handle_input(self, line: str) -> bool:  # noqa: D102
        valid_input = False

        if line == "1":
            valid_input = True
        elif line == "2":
            self.parent.update_value(self.invalid_key)
            valid_input = True
        elif line == "3" and self.suggested_key is not None:
            self.parent.update_value(self.suggested_key)
            valid_input = True

        if valid_input:
            pop_screen()
            return True

        return False


@dataclass
class RebindNameScreen(AbstractScreen):
    name: str = field(init=False)
    parent: KeybindOptionScreen

    def __post_init__(self) -> None:
        self.name = self.parent.option.display_name

    def draw(self) -> None:  # noqa: D102
        draw("Enter the name of the Key to bind to.")

    def handle_input(self, line: str) -> bool:  # noqa: D102
        pop_screen()
        if line in KNOWN_KEYS:
            self.parent.update_value(line)
        else:
            push_screen(InvalidNameScreen(self.parent, line))

        return True


@dataclass
class RebindPressScreen(AbstractScreen):
    name: str = field(init=False)
    parent: KeybindOptionScreen

    is_bind_active: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        self.name = self.parent.option.display_name

    def draw(self) -> None:  # noqa: D102
        draw(
            "Close console, then press the key you want to bind to. This screen will automatically"
            " close after being bound.",
        )
        draw_standard_commands()

        if self.is_bind_active:
            raw_keybinds.pop()
        raw_keybinds.push()

        # Closing console only triggers a release event
        @raw_keybinds.add(None, EInputEvent.IE_Pressed)
        def key_handler(key: str) -> type[Block]:  # pyright: ignore[reportUnusedFunction]
            self.parent.update_value(key)

            self.is_bind_active = False
            raw_keybinds.pop()

            show_hud_message(
                "Console Mod Menu",
                f"'{self.parent.option.display_name}' bound to '{key}'",
            )

            # Bit of hackery to inject back into the menu loop
            # Submit a B to close this menu
            remove_next_console_line_capture()
            _handle_interactive_input("B")

            return Block

    def handle_input(self, line: str) -> bool:  # noqa: D102
        return handle_standard_command_input(line)

    def on_close(self) -> None:  # noqa: D102
        if self.is_bind_active:
            self.is_bind_active = False
            raw_keybinds.pop()


@dataclass
class KeybindOptionScreen(OptionScreen[KeybindOption, str | None]):
    def draw_option(self) -> None:  # noqa: D102
        if self.option.is_rebindable:
            draw("[1] Rebind by key name")
            draw("[2] List known key names", indent=1)
            draw("[3] Rebind using key press")
            draw("[4] Unbind")

        draw_standard_commands()

    def handle_input(self, line: str) -> bool:  # noqa: D102
        if handle_standard_command_input(line):
            return True
        if not self.option.is_rebindable:
            return False

        if line == "1":
            push_screen(RebindNameScreen(self))
        elif line == "2":
            draw("Known Keys:")
            draw(", ".join(sorted(KNOWN_KEYS)))
            draw("")
        elif line == "3":
            push_screen(RebindPressScreen(self))
        elif line == "4":
            self.update_value(None)
        else:
            return False
        return True
