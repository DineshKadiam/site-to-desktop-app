application_id = 'net.codelogistics.webapps'

png_dir = join_paths('hicolor', '48x48', 'apps')
install_data(
  join_paths(png_dir, ('@0@.png').format(application_id)),
  install_dir: join_paths(get_option('datadir'), 'icons', png_dir)
)

hi_res_png_dir = join_paths('hicolor', '96x96', 'apps')
install_data(
  join_paths(hi_res_png_dir, ('@0@.png').format(application_id)),
  install_dir: join_paths(get_option('datadir'), 'icons', hi_res_png_dir)
)

scalable_dir = join_paths('hicolor', 'scalable', 'apps')
install_data(
  join_paths(scalable_dir, ('@0@.svg').format(application_id)),
  install_dir: join_paths(get_option('datadir'), 'icons', scalable_dir)
)

symbolic_dir = join_paths('hicolor', 'symbolic', 'apps')
install_data(
  join_paths(symbolic_dir, ('@0@-symbolic.svg').format(application_id)),
  install_dir: join_paths(get_option('datadir'), 'icons', symbolic_dir)
)

install_data(
  join_paths(symbolic_dir, ('background-app-symbolic.svg')),
  install_dir: join_paths(get_option('datadir'), 'icons', symbolic_dir)
)
