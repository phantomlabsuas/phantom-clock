# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Projects\\Utilities\\phantom-clock\\src\\phantom_clock\\server.py'],
    pathex=['C:\\Projects\\Utilities\\phantom-clock\\src\\phantom_clock'],
    binaries=[],
    datas=[('C:\\Projects\\Utilities\\phantom-clock\\resources\\index.html', 'resources'), ('C:\\Projects\\Utilities\\phantom-clock\\config\\config.json', 'config')],
    hiddenimports=['psutil'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PhantomClock',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='C:\\Projects\\Utilities\\phantom-clock\\packager\\win_version_gen.txt',
)
