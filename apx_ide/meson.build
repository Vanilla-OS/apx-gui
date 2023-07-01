pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'apx_ide')
gnome = import('gnome')

gnome.compile_resources('apx_ide',
  'apx-ide.gresource.xml',
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
  input: 'apx-ide.in',
  output: 'apx-ide',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

subdir('core')
subdir('widgets')
subdir('windows')

apx_ide_sources = [
  '__init__.py',
  'main.py',
]

install_data(apx_ide_sources, install_dir: moduledir)
