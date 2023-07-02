pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
windowsdir = join_paths(pkgdatadir, 'apx_ide/windows')

sources = [
  '__init__.py',
  'main_window.py',
  'create_subsystem.py',
]

install_data(sources, install_dir: windowsdir)