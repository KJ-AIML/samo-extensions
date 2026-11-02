# Samo's extension store

The listings behind the store in [Samo](https://github.com/KJ-AIML/samo): what Samo shows for each extension, and
the signed catalog it trusts. Samo only shows and installs what is in a catalog signed with KJ's key, and checks
every file against the catalog's SHA-256 before using it.

```
extensions/<id>/
  listing.toml        author, description, categories, homepage, what's new, screenshot captions
  icon.png            256 x 256, at most 256 KB
  screenshots/*.png   at most 6; each at most 2560 x 1600 and 2 MB; shown in name order
samo.toml             notes for Samo's own release
scripts/make-icons.py the dot-matrix icons
```

An extension's id, name, version, summary, `min_samo` and "What it changes" are not in `listing.toml`: they come
from the package's own `extension.toml`, so a listing can't say one thing while the package does another.

## Adding an extension

Open a pull request with `extensions/<id>/listing.toml`, an icon and screenshots, and the extension's source or a
link to it. KJ reviews the code and the listing. Screenshots must not show anyone's machine name, user name or
private projects.

## Publishing (KJ)

From the Samo repository, with this repository beside it:

```sh
cargo run -p xtask -- ext-package extensions/claude-sessions
cargo run -p xtask -- ext-package extensions/hello
cargo run -p xtask -- ext-package extensions/shots
# Optionally Samo itself: scripts/bundle-macos.sh, then
#   ditto -c -k --keepParent target/Samo.app target/Samo-<version>-macos-arm64.zip
cargo run -p xtask -- ext-publish --store ../samo-extensions [--samo target/Samo-<version>-macos-arm64.zip]
gh release upload store ../samo-extensions/dist/* -R KJ-AIML/samo-extensions --clobber
```

`ext-publish` signs `catalog.json` with the key in KJ's Keychain (made once by `cargo run -p xtask --
ext-keygen`), then reads `dist/` back and verifies everything exactly as Samo will.

`ext-package` signs a helper that asks macOS for a permission (Shots: Screen Recording) with the "Talvyn Samo
Extensions" identity in KJ's Keychain, made once by `cargo run -p xtask -- ext-codesign-setup`. macOS keeps a
permission for "this identifier, signed by this certificate", so updates keep it; an ad-hoc build would be a new
app every time. Keep a backup of the identity (Keychain Access → export as .p12): a new one makes every user allow
Screen Recording once more.
