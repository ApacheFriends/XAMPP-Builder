
# This is CPAN.pm's systemwide configuration file. This file provides
# defaults for users, and the values can be changed in a per-user
# configuration file. The user-config file is being looked for as
# ~/.cpan/CPAN/MyConfig.pm.

$CPAN::Config = {
  'auto_commit' => q[0],
  'build_cache' => q[100],
  'build_dir' => q[/Applications/XAMPP/xamppfiles/var/perl/cpan/build],
  'cache_metadata' => q[1],
  'commandnumber_in_prompt' => q[1],
  'cpan_home' => q[/Applications/XAMPP/xamppfiles/var/perl/cpan],
  'ftp_passive' => q[1],
  'ftp_proxy' => q[],
  'http_proxy' => q[],
  'inactivity_timeout' => q[0],
  'index_expire' => q[1],
  'inhibit_startup_message' => q[0],
  'keep_source_where' => q[/Applications/XAMPP/xamppfiles/var/perl/cpan/sources],
  'make_arg' => q[],
  'make_install_arg' => q[],
  'make_install_make_command' => q[],
  'makepl_arg' => q[],
  'mbuild_arg' => q[],
  'mbuild_install_arg' => q[UNINST=1],
  'mbuild_install_build_command' => q[./Build],
  'mbuildpl_arg' => q[],
  'no_proxy' => q[],
  'prerequisites_policy' => q[follow],
  'scan_cache' => q[atstart],
  'show_upload_date' => q[0],
  'term_ornaments' => q[1],
  'urllist' => [],
  'use_sqlite' => q[0],
};
1;
__END__
