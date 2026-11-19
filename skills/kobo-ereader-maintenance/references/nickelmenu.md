# NickelMenu configuration

NickelMenu reads plain-text configuration files from `.adds/nm/` on the mounted `KOBOeReader` volume. Its own `.adds/nm/doc` is the authoritative syntax reference installed on the device.

## Ownership and update rules

- Do not edit `.adds/nm/doc`; updates overwrite it.
- The dashboard installer owns `.adds/nm/kobo-ha` and may rewrite it during **Update**.
- Put personal entries in a separate, uniquely named file such as `.adds/nm/local-custom`.
- Use plain UTF-8 text with Unix line endings and no hidden `.txt` suffix.
- Back up `.adds/nm/` before changes. Never display unrelated command files if they may contain credentials.

## Basic syntax

The common form is:

```text
menu_item :<location> :<label> :<action> :<argument>
```

Labels cannot contain a colon. Spacing around separators is allowed. Lines beginning with `#` are comments. Supported locations, actions, firmware constraints, escaping, conditionals, and chains are documented in `.adds/nm/doc` and the [official upstream document](https://github.com/pgaskin/NickelMenu/blob/master/res/doc).

Safe examples:

```text
# Show the USB connection dialog
menu_item :main :USB connection :nickel_misc :force_usb_connection

# Return to the Kobo home screen
menu_item :main :Kobo home :nickel_misc :home

# Show the kernel version briefly
menu_item :main :Kernel version :cmd_output :500:uname -a
```

For the Home Assistant dashboard, prefer changing the menu name in the dashboard setup tool. A typical generated entry launches `/mnt/onboard/.kobo-ha/launch.sh`; preserve that path unless the installation was deliberately relocated.

## Apply and validate

1. Connect the Kobo and tap **Connect**.
2. Copy `.adds/nm/` to a backup directory on the computer.
3. Edit only the intended custom file.
4. Check each directive against the documentation installed for that NickelMenu version.
5. Safely eject and restart the Kobo.
6. If the syntax is invalid, NickelMenu adds an error item to the main menu. Fix the cited file/line instead of reinstalling blindly.

## Security

Do not add Telnet, FTP, SSH, or unauthenticated network services merely for convenience. Official documentation contains powerful examples, but exposing a root shell on the LAN materially changes the device's security. Only configure remote access when the user explicitly requests and understands it.

Do not place Home Assistant tokens directly in NickelMenu command lines. The dashboard reads its protected configuration from `.kobo-ha/config.yaml`.

## Updates and uninstall

Kobo firmware updates can remove the NickelMenu library while leaving configuration files and the dashboard intact. Re-run the dashboard setup tool to reinstall the compatible NickelMenu package.

To uninstall NickelMenu using its supported mechanism, create an empty `.adds/nm/uninstall` file and restart. Confirm first because this changes device behavior. Removing NickelMenu does not automatically remove `.kobo-ha` or personal configuration.

## Sources

- [NickelMenu official site](https://pgaskin.net/NickelMenu/)
- [NickelMenu official configuration document](https://github.com/pgaskin/NickelMenu/blob/master/res/doc)
- [NickelMenu releases](https://github.com/pgaskin/NickelMenu/releases)

