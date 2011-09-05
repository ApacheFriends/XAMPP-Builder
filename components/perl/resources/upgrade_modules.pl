# Many thanks to BinGOs from #perl on freenode.net for this script :)

use strict;
use warnings;
use CPANPLUS::Backend;

$ENV{PERL_MM_USE_DEFAULT} = 1; # despite verbose setting
$ENV{PERL_EXTUTILS_AUTOINSTALL} = '--defaultdeps';

my $cb = CPANPLUS::Backend->new();
my $conf = $cb->configure_object;

$conf->set_conf( 'prereqs' => 1, 'skiptest' => 1 );

my @list = $cb->installed();

my @rv; my %seen;
for my $mod (@list) {
  ### skip this mod if it's up to date ###
  next if $mod->is_uptodate;
  ### skip this mod if it's core ###
  next if $mod->package_is_perl_core;

  if( !$seen{$mod->package}++ ) {
        push @rv, $mod;
  }
}

@rv = sort { $a->module cmp $b->module } @rv;

$_->install() for @rv;