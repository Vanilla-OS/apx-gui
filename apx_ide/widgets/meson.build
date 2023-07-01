pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
widgetsdir = join_paths(pkgdatadir, 'apx_ide/widgets')

sources = [
  '__init__.py',
  'tab_subsystem.py',
  'entry_subsystem.py',
]

install_data(sources, install_dir: widgetsdir)