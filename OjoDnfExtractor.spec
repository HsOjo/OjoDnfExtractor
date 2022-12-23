# -*- mode: python -*-

block_cipher = None


a = Analysis(['__main__.py'],
             pathex=['./'],
             binaries=[],
             datas=[('./app/lib/bass/bass.dll', './app/lib/bass/'), ('./app/lib/bass/libbass.so', './app/lib/bass/'), ('./app/lib/bass/libbass.dylib', './app/lib/bass/')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='OjoDnfExtractor',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False )
app = BUNDLE(exe,
             name='OjoDnfExtractor.app',
             icon=None,
             bundle_identifier=None)
