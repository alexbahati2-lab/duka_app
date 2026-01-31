# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

# Collect Streamlit and its dynamic imports
streamlit_datas, streamlit_binaries, streamlit_hidden = collect_all("streamlit")

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=streamlit_binaries,
    datas=streamlit_datas + [
        ('assets', 'assets'),
        ('database', 'database'),
        ('modules', 'modules'),
    ],
    hiddenimports=streamlit_hidden + [
        'pkg_resources',
        'importlib_metadata',
    ],
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
    name='DukaApp',
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
    icon='assets\\duka_icon.ico',
)
