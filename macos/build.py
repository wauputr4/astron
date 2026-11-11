#!/usr/bin/env python3
"""Repeatable CLT-only build; --install backs up an existing app first."""
import datetime
import json
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import sys
import fcntl

# Refuse overlapping builds: signing a changing bundle is not safe.
_lock = open(Path(__file__).resolve().parent / '.build.lock', 'a')
try:
    fcntl.flock(_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError:
    raise SystemExit('Another Astron build is running; inspect it before retrying.')

HERE = Path(__file__).resolve().parent
APP = HERE / 'build/Astron.app'
DEST = Path.home() / 'Applications/Astron.app'
EXT = Path('Contents/PlugIns/AstronWidget.appex')


def run(*args, capture=False):
    return subprocess.run(['rtk', 'proxy', *map(str, args)], check=True,
                          capture_output=capture, text=capture)


def read_plist(path, fallback):
    return plistlib.loads(path.read_bytes()) if path.exists() else fallback


def write_plist(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(plistlib.dumps(value))


base = DEST if DEST.exists() else APP
app_info = read_plist(base / 'Contents/Info.plist', {
    'CFBundleIdentifier': 'com.wauputr4.astron.macos', 'CFBundleExecutable': 'Astron',
    'CFBundleName': 'Astron', 'CFBundleDisplayName': 'Astron', 'CFBundlePackageType': 'APPL',
    'CFBundleShortVersionString': '1.0', 'CFBundleVersion': '1',
    'LSMinimumSystemVersion': '14.0', 'NSHighResolutionCapable': True,
    'CFBundleSupportedPlatforms': ['MacOSX'], 'DTPlatformName': 'macosx',
})
ext_info = read_plist(base / EXT / 'Contents/Info.plist', {
    'CFBundleIdentifier': 'com.wauputr4.astron.macos.widget', 'CFBundleExecutable': 'AstronWidget',
    'CFBundleName': 'AstronWidget', 'CFBundleDisplayName': 'Astron Reflection',
    'CFBundlePackageType': 'XPC!', 'CFBundleShortVersionString': '1.0', 'CFBundleVersion': '1',
    'LSMinimumSystemVersion': '14.0', 'CFBundleSupportedPlatforms': ['MacOSX'],
    'DTPlatformName': 'macosx', 'NSExtension': {'NSExtensionPointIdentifier': 'com.apple.widgetkit-extension'},
})
# Preserve every unrelated registered URL type, adding only the requested scheme.
url_types = list(app_info.get('CFBundleURLTypes', []))
if not any('astron' in x.get('CFBundleURLSchemes', []) for x in url_types):
    url_types.append({'CFBundleURLName': 'com.wauputr4.astron.capture', 'CFBundleURLSchemes': ['astron'], 'CFBundleTypeRole': 'Editor'})
app_info['CFBundleURLTypes'] = url_types
app_info['CFBundleVersion'] = str(int(app_info.get('CFBundleVersion', '1')) + 1)
ext_info['CFBundleVersion'] = app_info['CFBundleVersion']
# Retain the installed widget sandbox entitlements, falling back to source.
widget_entitlements = HERE / 'widget.entitlements'
app_entitlements = None
for bundle, filename in [(base, 'preserved-app.entitlements'), (base / EXT, 'preserved-widget.entitlements')]:
    if bundle.exists():
        result = subprocess.run(['rtk', 'proxy', '/usr/bin/codesign', '-d', '--entitlements', ':-', str(bundle)], capture_output=True)
        raw = result.stdout
        start = raw.find(b'<?xml')
        if start >= 0:
            try:
                ent = plistlib.loads(raw[start:])
                if ent:
                    target = HERE / 'build' / filename
                    write_plist(target, ent)
                    if 'widget' in filename:
                        widget_entitlements = target
                    else:
                        app_entitlements = target
            except plistlib.InvalidFileException:
                raise SystemExit('Cannot preserve existing entitlements; refusing build.')
# Merge newly required, narrowly scoped cache access into preserved entitlements.
entitlements = plistlib.loads(widget_entitlements.read_bytes())
key = 'com.apple.security.temporary-exception.files.home-relative-path.read-only'
entitlements[key] = list(dict.fromkeys([*entitlements.get(key, []), '/Library/Application Support/astron/sky-calendar.json']))
widget_entitlements = HERE / 'build/merged-widget.entitlements'
write_plist(widget_entitlements, entitlements)
if entitlements.get('com.apple.security.app-sandbox') is not True:
    raise SystemExit('Widget sandbox entitlement must remain enabled.')
for path in [APP / 'Contents/MacOS', APP / 'Contents/Resources', APP / EXT / 'Contents/MacOS']:
    path.mkdir(parents=True, exist_ok=True)
write_plist(APP / 'Contents/Info.plist', app_info)
write_plist(APP / EXT / 'Contents/Info.plist', ext_info)
for resource in ('generate.py', 'sky_calendar.py'):
    shutil.copy2(HERE / resource, APP / 'Contents/Resources' / resource)
write_plist(APP / 'Contents/Resources/runtime-paths.plist', {
    'skill': str(HERE.parent),
    'python': os.environ.get('ASTRON_PYTHON', str(Path.home() / '.local/share/astron/venv/bin/python')),
})
sdk = run('/usr/bin/xcrun', '--sdk', 'macosx', '--show-sdk-path', capture=True).stdout.strip()
arch = os.uname().machine
for source, output in [('App.swift', APP / 'Contents/MacOS/Astron'), ('Widget.swift', APP / EXT / 'Contents/MacOS/AstronWidget')]:
    # Classic appex bootstrap must run before WidgetKit's retained Swift main.
    extension_flags = ['-application-extension', '-Xlinker', '-e', '-Xlinker', '_NSExtensionMain',
                       '-Xlinker', '-u', '-Xlinker', '_main'] if source == 'Widget.swift' else []
    run('/usr/bin/xcrun', 'swiftc', '-parse-as-library', '-O', *extension_flags,
        '-sdk', sdk, '-target', f'{arch}-apple-macos14.0', HERE / source, HERE / 'SkyViews.swift', '-o', output)
run('/usr/bin/codesign', '--force', '--sign', '-', '--entitlements', widget_entitlements, APP / EXT)
args = ['/usr/bin/codesign', '--force', '--sign', '-']
if app_entitlements:
    args.extend(['--entitlements', app_entitlements])
run(*args, APP)
run('/usr/bin/codesign', '--verify', '--deep', '--strict', APP)
if '--install' in sys.argv:
    if DEST.exists():
        backup = HERE / 'backups' / ('Astron-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f') + '.app')
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(DEST, backup, symlinks=True)
        print('Backup:', backup)
    DEST.parent.mkdir(parents=True, exist_ok=True)
    run('/usr/bin/ditto', APP, DEST)
    run('/usr/bin/codesign', '--verify', '--deep', '--strict', DEST)
    run('/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister', '-f', DEST)
    run('/usr/bin/pluginkit', '-a', DEST / EXT)
    print('Installed and registered:', DEST)
print('Build verified:', APP)
