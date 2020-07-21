#!/usr/bin/perl

use strict;
use warnings;
use Cwd 'abs_path';
use 5.010;

my $arg_size = @ARGV;
die "Usage: prepare_bag path/to/bag_directory [dest]" unless $arg_size == 1 || $arg_size == 2;

my $dest = $ARGV[1] || '.';

my $source = abs_path($ARGV[0]);
#print "source='" . $source . "'\n";
$source =~ /^(.+)\/([^\/]+)\/?$/;
$source = $1;
my $filename = $2;
#print "source='" . $source . "'\n";
#print "filename='" . $filename . "'\n";

chdir abs_path($dest);

#say "Tarring file";
my $error = `7z -ttar a $filename.tar $source/$filename 2>&1`;
die "Cannot create tar file:\n$error" unless $? == 0;
my $size = (stat "$filename.tar")[7];
rename "$filename.tar", "$filename.$size.tar";
#say "Zipping tar file";
$error = `7z -tbzip2 a -aoa $filename.$size.tar.bz2 $filename.$size.tar`;
die "Cannot zip tar file:\n$error" unless $? == 0;
