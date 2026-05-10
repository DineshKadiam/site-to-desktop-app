pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'webapps')
gnome = import('gnome')

blueprints = custom_target('blueprints',
  input: files(
    # LIST YOUR BLUEPRINT FILES HERE
    'window.blp',
    'web_app_properties.blp',
    'create_web_app_dialog.blp',
    'edit_web_app_dialog.blp',
    'url_dialog.blp',
    'web_app_window.blp',
    'report_broken_dialog.blp',
  ),
  output: '.',
  command: [find_program('blueprint-compiler'), 'batch-compile', '@OUTPUT@', '@CURRENT_SOURCE_DIR@', '@INPUT@'],
)

gnome.compile_resources('webapps',
  'webapps.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
  dependencies: blueprints,
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'webapps.in',
  output: 'webapps',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr--r--'
)

webapps_sources = [
  '__init__.py',
  'legacy_web_app_paths.py',
  'main.py',
  'window.py',
  'web_app_properties.py',
  'create_web_app_dialog.py',
  'edit_web_app_dialog.py',
  'web_app_paths.py',
  'web_app_state.py',
  'web_app_window.py',
  'create_desktop_file.py',
  'exceptions.txt',
  'manifest_html_parser.py',
  'url_dialog.py',
  'parse_manifest.py',
  'parse_webpage.py',
  'report_broken_dialog.py',
]

install_data(webapps_sources, install_dir: moduledir)
