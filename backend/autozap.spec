# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

# --- A MÁGICA DA ARTILHARIA PESADA ---
# Isso força o PyInstaller a pegar TUDO do openpyxl: códigos, dados e binários.
datas, binaries, hiddenimports = collect_all('openpyxl')

block_cipher = None

# Adicionamos nossas importações manuais à lista que o collect_all já criou
hiddenimports += [
    'fastapi',
    'pydantic',
    'starlette',
    'uvicorn',
    'sqlalchemy',
    'pandas',
    'selenium',
    'webdriver_manager',
    'psutil',
    'multipart',
    'python-multipart',
    'engine',
    'database',
    'models',
    'schemas',
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'sqlalchemy.sql.default_comparator',
]

# Adicionamos o Site e o Ícone à lista de dados
datas += [
    ('../frontend/dist', 'frontend/dist'),
    ('../frontend/public/logo.ico', '.')
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries, # Usa os binários do openpyxl
    datas=datas,       # Usa os dados combinados
    hiddenimports=hiddenimports, # Usa as importações combinadas
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
    name='AutoZapManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True, 
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='../frontend/public/logo.ico'
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AutoZapManager',
)