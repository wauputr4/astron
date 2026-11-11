# Astron macOS companion and widget

Local SwiftUI/WidgetKit app built with Apple's Command Line Tools; full Xcode is not required. No network service, paid dependency, or automatic journal/profile creation.

## Build and install

```sh
rtk proxy /usr/bin/python3 build.py
rtk proxy /usr/bin/python3 build.py --install
```

The installer preserves existing bundle metadata/entitlements, backs up the installed application under `backups/`, signs the extension before the app, verifies both, and registers Launch Services and WidgetKit. Build from the `macos/` directory in this repository. The build records its parent skill checkout and the local Python interpreter inside the installed app. Keep that checkout in place, or rebuild after moving it. Set `ASTRON_PYTHON` at build time if your tested environment is not `~/.local/share/astron/venv/bin/python`. The build wrapper uses `rtk`, Swift compiler and Apple Command Line Tools. Ad-hoc signatures are for this local installation, not notarized public distribution.

## Connect a journal

1. Open `~/Applications/Astron.app`, then **Buka refleksi → Hubungkan jurnal** (or the gear).
2. Choose an existing consented **self** profile. The app deliberately uses generic numbered labels, not aliases. If there is no profile, create one with Astron after granting storage consent; the app never invents one.
3. Check the private journal directory (default `~/Library/Application Support/astron`), then **Terapkan**. Use **Muat ulang** after externally creating a profile. An alternate directory must already contain `journal.sqlite3` and belong to the current user with mode 0700.
4. Enter an experience, explicitly check local storage consent, then **Simpan**. Opening `astron://capture` only opens the form; it never saves automatically. Companion captures conservatively record exposure as unknown/already exposed, not blind.
5. **Pelajaran** privately shows approved active contextual lessons; expired or superseded evidence is excluded. **Perbarui widget** refreshes the safe cache. Choose **Generik — tanpa profil** and apply to disconnect without deleting the journal.

Add **Astron — Refleksi Hari Ini** from macOS's Edit Widgets gallery. Small size shows a generic question and **Catat pengalaman**. Medium also shows a generic action and lesson-availability reference. WidgetKit decides refresh timing. Compilation and pluginkit registration alone do not prove desktop rendering.

## Privacy

`widget-settings.json` and `widget-reflections.json` are local 0600 files under the private Astron directory. Settings contain the selected profile ID; the widget cache contains only allowlisted generic text, never profile IDs, aliases, journal entries, or raw lesson text. The extension resolves the owner's home rather than its sandbox container and uses the retained read-only sandbox exception. The companion reads lessons only on explicit private UI request. Reflections are symbolic prompts, not scientific validation or consequential advice.

## Tests

```sh
rtk proxy /usr/bin/python3 test_bridge.py
```

Tests use synthetic temporary journals and never read or write the owner's actual profiles. They cover explicit self selection/consent, safe cache, capture, approved lessons, directory permissions, settings merge, and symlink rejection. UI rendering and widget placement require separate desktop verification.


## Langit & Kamu — sky calendar

A second widget, alongside the original reflection widget:

- **Small:** month grid, with dots on calculated event dates.
- **Medium:** calendar on the left; next event/time and symbolic interpretation on the right.
- **Large:** the same plus the next three events in the selected month.
- Click a date to open event details. The app supports month selection, IANA timezone (default Asia/Jakarta), all-date/day filtering and a capture shortcut.

Open **Langit & Kamu**, choose `YYYY-MM` and timezone, then **Hitung / perbarui**. The calculation is offline. Missing dependencies produce an error, not a made-up calendar. Core setup from the repository root:

```sh
rtk proxy python3 -m venv ~/.local/share/astron/venv
rtk proxy ~/.local/share/astron/venv/bin/python -m pip install -r requirements.txt
rtk proxy ~/.local/share/astron/venv/bin/python -m unittest discover -s macos -p 'test_*.py' -v
```

The default is a **general** sky calendar. Personal interpretation requires an explicitly selected, consented self journal profile with a birth object containing date, known local time, timezone and verified latitude/longitude. Existing standalone birth profiles are not silently migrated. In the sky panel, enable **Izinkan kontak natal pribadi tampil di desktop**, then calculate. This separate choice allows visible natal contacts, but never exports names, birth details or journal text. Anyone looking at the desktop may see those contacts. **Hapus cache / cabut tampilan personal** removes the calendar cache immediately. Selecting another journal profile/root also removes the previous cache. Do not use someone else's profile here.

Personal links use event-time positions and a 2° aspect orb, not exact personal-transit timing. Interpretation is a symbolic prompt and a tentative chart-derived domain, not a promise that something will happen. General coverage includes lunations, selected aspects between Sun/Mercury/Venus/Mars/Jupiter/Saturn, and stations of Mercury/Venus/Mars/Jupiter/Saturn. No eclipse/visibility forecast or exhaustive astronomical calendar. The source/method, local timezone, UTC and update timestamp are retained. The cache is 0600 in the private Astron data directory and is not encrypted.

Refresh manually when the month changes; old-month widget data shows a refresh prompt, never masquerades as current. WidgetKit decides rendering and update timing. No automation or external AI service is installed. Direct CLI (from repo root):

```sh
rtk proxy ~/.local/share/astron/venv/bin/python macos/sky_calendar.py <<<'{"month":"2026-11","timezone":"Asia/Jakarta"}'
```

Do not commit cache files or build/backups. The source-only GitHub package is not a notarized binary release. An installed/registered extension still requires separate desktop-render verification.
