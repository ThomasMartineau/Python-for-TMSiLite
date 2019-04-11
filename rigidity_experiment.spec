# -*- mode: python -*-

block_cipher = None


a = Analysis(['rigidity_experiment.py'],
             pathex=['C:\\Users\\tlm111\\AppData\\Local\\Programs\\Python\\Python37\\Lib\\site-packages\\PyQt5\\Qt\\bin', 'C:\\Users\\tlm111\\Documents\\PhD year 2\\repository\\Python-for-TMSiLite'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='rigidity_experiment',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='rigidity_experiment')
