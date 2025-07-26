#!/usr/bin/perl
# download_client.cgi
#
# This script handles the download of generated OpenVPN client archives.

use strict;
use warnings;
use File::Basename;

# Define a version for this script for debugging purposes
my $script_version = "2.4"; 

# Load the module's library which contains necessary Webmin functions and helpers.
require './ovpncreator-lib.pl';

# Initialize Webmin configuration to get the output_base_dir and other globals.
&init_config();

# Declare global variables that are populated by init_config() or ReadParse()
our (%in, %config, %text, $ENV);

# Parse CGI input parameters into %in
&ReadParse();

# Determine if we are in debug mode
my $debug_mode = $in{'debug'} ? 1 : 0;

# --- Read Configuration ---
my $output_base_dir = $config{'output_base_dir'};

# --- Validate Configuration ---
if (!$output_base_dir) {
    # In non-debug mode, just a plain text error
    print "Error: Client output directory not configured.\n";
    exit;
}

# --- Get Filename from URL ---
my $filename = $in{'file'};

# --- Perform Security Checks ---
if (!$filename) {
    print "Error: No file specified for download.\n";
    exit;
}
if ($filename !~ /^[\w\.\-]+$/ || ($filename !~ /\.zip$/i && $filename !~ /\.tgz$/i && $filename !~ /\.tar\.gz$/i)) {
    print "Error: Invalid filename or unsupported file type.\n";
    exit;
}

# Construct the full, secure path to the file
my $full_path = "$output_base_dir/$filename";


# --- NORMAL DOWNLOAD MODE ---

# Verify the File Exists and is Readable
if (! -e $full_path || ! -r $full_path) {
    print "Error: File not found or not readable.\n";
    exit;
}

# Determine content type based on file extension
my ($name, $path, $suffix) = fileparse($filename, qr/\.[^.]*$/);
my $content_type = "application/octet-stream"; # Default
if (lc($suffix) eq '.zip') {
    $content_type = "application/zip";
} elsif (lc($suffix) eq '.tgz' || lc($suffix) eq '.gz') {
    $content_type = "application/x-gzip";
}

# --- REPLACEMENT FOR http_download_header ---
# Send HTTP headers to initiate file download
my $file_size = -s $full_path;
print "Content-Type: $content_type\n";
print "Content-Disposition: attachment; filename=\"$filename\"\n";
print "Content-Length: $file_size\n";
print "\n"; # This blank line is crucial to separate headers from the file content
# --- END REPLACEMENT ---


# Read and print the file contents to stdout
print &read_file_contents($full_path);