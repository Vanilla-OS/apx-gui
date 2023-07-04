pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'apx_gui')
gnome = import('gnome')

gnome.compile_resources('apx_gui',
  'apx-gui.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'apx-gui.in',
  output: 'apx-gui',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

subdir('core')
subdir('widgets')
subdir('windows')
subdir('utils')

apx_gui_sources = [
  '__init__.py',
  'main.py',
]

install_data(apx_gui_sources, install_dir: moduledir)
