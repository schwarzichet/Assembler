# -*- mode: python -*-

block_cipher = None


a = Analysis(['ide.py'],
             pathex=['C:\\Users\\DFZ\\AppData\\Roaming\\Python\\Python35\\site-packages\\PyQt5\\Qt\\bin', 'C:\\Users\\DFZ\\AppData\\Local\\Programs\\Python\\Python35', 'C:\\Users\\DFZ\\PycharmProjects\\Assembler'],
             binaries=[],
             datas=[('icon.ico', '.')],
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
          name='ide',
          debug=False,
          strip=False,
          upx=True,
          console=False , icon=('icon.ico', 'icon.ico'))
