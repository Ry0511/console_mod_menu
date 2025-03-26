# Console Mod Menu
A console-based mod menu for [pyunrealsdk](https://github.com/bl-sdk/pyunrealsdk/) following the
[mods_base](https://github.com/bl-sdk/mods_base/) layout.

Should be entirely game agnostic, so useful during development before having made a proper,
gui-based mod menu.

### Optional Extra Modules
If some extra modules are available, the menu enables a few extra features. These are optional, the
menu will gracefully degrade if they are not available.

If the `keybinds.raw_keybinds` module is present, allows binding a key from a raw key press. See
the implementation in
[oak-mod-manager](https://github.com/bl-sdk/oak-mod-manager/blob/master/src/keybinds/raw_keybinds.py)
for what interface this is expected to have.

If the function `ui_utils.show_hud_message` is present, it is used to notify when a key has been
bound from one of the raw presses from above. This function should take a title as the first arg and
a message as the second (both positionally), and show them in a temporary message on screen.

# Changelog

### v1.5
- Support host-only coop support value
- Linting fixes

### v1.4
- Improved suggestions when trying to bind a key by name, and misspelling it.
- Swap known controller key names between UE3/UE4 versions, based on game.
- Grouped options with no visible children no longer show their header.
  
### Older
Versions 1.0 through 1.3 were developed as part of the
[oak-mod-manager](https://github.com/bl-sdk/oak-mod-manager/blob/master/changelog.md#v14), see it
for a full changelog.
