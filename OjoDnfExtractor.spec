# -*- mode: python ; coding: utf-8 -*-
import platform

with open('app/const.py') as io:
    exec(io.read())

datas = []
if platform.system() == 'Windows':
    datas.append(('./app/libs/bass/bass.dll', './app/libs/bass/'))
elif platform.system() == 'Darwin':
    datas.append(('./app/libs/bass/libbass.dylib', './app/libs/bass/'))
else:
    datas.append(('./app/libs/bass/libbass.so', './app/libs/bass/'))

name = f'{Const.project}-{Const.version}-{platform.system()}-{platform.machine()}'

block_cipher = None

a = Analysis(
    ['__main__.py'],
    pathex=['./'],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=name,
)
app = BUNDLE(
    coll,
    name=f'{name}.app',
    icon=None,
    bundle_identifier=None,
)
