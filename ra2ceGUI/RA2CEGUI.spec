# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

hidden_imports = ['pandas',
		  'geopandas',
		  'fiona._shim',
		  'fiona.schema',
		  'gdal',
		  'pytest',
		  'shapely',
		  'shapely.geometry',
		  'numba',
		  'rtree',
		  'past',
		  'future',
		  'past.utils',
		  'xarray',
          'operations',
          'mapbox_map',
          'operations.ra2ce'
          'operations.ra2ce.run_manager',
          'operations.ra2ce.summary_results',
          'operations.ra2ce.run_ra2ce',
          'operations.ra2ce.validate_ra2ce_configuration',
          'operations.ra2ce.modify_ra2ce_configuration',
          'operations.ra2ce.run_manager'
		  ]

a = Analysis(['D:\\GUITools\\ra2ceGUI\\run_ra2ceGUI.py'],
             pathex=['D:\\GUITools'],
             binaries=[],
             datas=[('icons', 'icons')],
             hiddenimports=hidden_imports,
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
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='RA2CE',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True  # False = do not show console.
	  )
