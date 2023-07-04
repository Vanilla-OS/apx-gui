pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
coredir = join_paths(pkgdatadir, 'apx_gui/core')

sources = [
  '__init__.py',
  'run_async.py',
  'apx.py',
  'apx_entities.py',
]

install_data(sources, install_dir: coredir)