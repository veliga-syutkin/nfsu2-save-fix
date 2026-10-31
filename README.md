# nfsu2-save-fix

Fix the error **"`<name>` cannot be restored: the name inside, "...", is not one the game makes (1 to 7 letters and digits)"** when importing a *Need for Speed: Underground 2* PC save on [nfsu2.xyz](https://nfsu2.xyz).

The profile name is stored *inside* the save file and covered by three checksums, so renaming the file is not enough. This script rewrites the name and recomputes the checksums. It always works on a copy: your original file is never modified.

It helps with saves whose internal name is not 1 to 7 plain letters/digits: profiles made by third-party tools (for example with underscores in the name) and saves from other-language releases whose name contains non-ASCII bytes (see [th0mk/nfsu2-web#47](https://github.com/th0mk/nfsu2-web/issues/47)).

Not affiliated with nfsu2.xyz, its author, or Electronic Arts.

## Option 1: in the browser (nothing to install)

Open **https://veliga-syutkin.github.io/nfsu2-save-fix/** (or double-click `index.html` from a download), drop your profile file on the page, pick a new name, and download the fixed copy. Everything runs locally in your browser: nothing is uploaded.

## Option 2: command line

Python 3 is required, nothing else (standard library only). On Windows, use `py` (or `python`) instead of `python3`.

```
python3 nfsu2_rename_save.py check  MYPROFILE
python3 nfsu2_rename_save.py rename MYPROFILE NEWNAME
```

- `check` shows the name stored inside the file and verifies its checksums.
- `rename SAVE NEWNAME [-o OUTDIR]` writes `OUTDIR/NEWNAME/NEWNAME` (default `OUTDIR` is the current directory) and refuses to overwrite an existing file.

`NEWNAME` must be 1 to 7 ASCII letters or digits. Then import the resulting file on nfsu2.xyz.

## Bonus: keep a copy of a save

Renaming always produces a *copy*, so the same tool can duplicate a save, for example to try a risky approach without losing your progress. nfsu2.xyz identifies profiles by the name stored inside the file (and skips a profile whose name is already taken, ignoring capitals), so import the copy under a **different** name and you get two separate profiles. This works even if the original's name was already valid.

Only the profile file itself is copied.

## What it accepts

Standard PC profiles: exactly 54,966 bytes, starting with the magic `20CM`. Anything else is rejected with a message instead of being modified.

The layout comes from the public client code of nfsu2.xyz: 36-byte header, name at offset 53797 (32 bytes, NUL-terminated), three little-endian CRC32/MPEG-2 values at offsets 16, 20 and 24.

## Status

Tested on a real profile from the PC game (imported fine on nfsu2.xyz, and the game then ran normally). Saves from other-language releases are handled the same way (the whole name field is overwritten) but have only been tested on a simulated non-ASCII name. The page and the script produce byte-identical output, and the page's drag-and-drop has been tried in a real browser (Chrome on Linux); other browsers and Windows are untested, so please report problems. Issues and pull requests are welcome.

## License

MIT, see [LICENSE](LICENSE).
