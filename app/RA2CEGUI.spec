# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

hidden_imports = ['pandas',
		  'geopandas',
		  'fiona._shim',
		  'fiona.schema',
		  'gdal',
		  'pytest',
          'pyproj',
		  'shapely',
		  'shapely.geometry',
		  'rtree',
		  'xarray',
		  'rasterio.sample',
          'operations.operations',
          'mapbox_map',
          'run_manager',
          'summary_results',
          'run_ra2ce',
          'validate_ra2ce_configuration',
          'flood_map_overlay'
		  ]

a = Analysis(['D:\\GUITools\\app\\run_ra2ceGUI.py'],
             pathex=['D:\\GUITools', 'D:\\GUITools\\app\\operations\\ra2ce'],
             binaries=[],
             datas=[('icons', 'icons'),
			        ('c:\\Users\\groen_fe\\.conda\\envs\\ra2ce_gui\\Lib\\site-packages\\pyproj.libs', 'pyproj.libs')],
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
          debug=True,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True  # False = do not show console.
	  )
