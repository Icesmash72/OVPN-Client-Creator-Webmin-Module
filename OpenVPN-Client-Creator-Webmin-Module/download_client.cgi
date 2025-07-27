#!/usr/bin/perl
# download_client.cgi
#
# This script handles the download OR emailing of generated OpenVPN client archives.

use strict;
use warnings;
use File::Basename;
use MIME::Lite;

# Define a version for this script for debugging purposes
my $script_version = "3.3"; # Redirects to a dedicated success page

# Load the module's library
require './ovpncreator-lib.pl';

# Initialize Webmin configuration
&init_config();

# Declare global variables
our (%in, %config, %text, $ENV);

# Parse CGI input parameters
&ReadParse();

# --- Configuration & Validation ---
my $output_base_dir = $config{'output_base_dir'};
&error("Error: Client output directory not configured.") unless $output_base_dir;

my $filename = $in{'file'};
&error("Error: No file specified for download.") unless $filename;

if ($filename =~ /\.\./ || $filename !~ /^[\w.\-]+\.(zip|tgz|tar\.gz)$/i) {
    &error("Error: Invalid filename or unsupported file type.");
}

my $full_path = "$output_base_dir/$filename";
&error("Error: File not found or not readable.") unless (-e $full_path && -r $full_path);

# --- Action Router ---
my $action = $in{'action'} || 'download';

if ($action eq 'send_email') {
    &perform_send_email();
}
else {
    &perform_download();
}

exit;

# ==============================================================================
# SUBROUTINES
# ==============================================================================

sub perform_download {
    my ($name, $path, $suffix) = fileparse($filename, qr/\.[^.]*$/);
    my $content_type = "application/octet-stream";
    if (lc($suffix) eq '.zip') { $content_type = "application/zip"; }
    elsif (lc($suffix) eq '.tgz' || lc($suffix) eq '.gz') { $content_type = "application/x-gzip"; }

    print "Content-Type: $content_type\n";
    print "Content-Disposition: attachment; filename=\"$filename\"\n";
    print "Content-Length: " . (-s $full_path) . "\n\n";
    print &read_file_contents($full_path);
}

sub perform_send_email {
    my $email_to = $in{'email_to'};
    unless ($email_to && $email_to =~ /^[a-zA-Z0-9._%+-]+\@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/) {
        &error("Error: A valid email address is required.");
    }
    
    # --- NEW: Use configured sender email, with a fallback ---
    my $from_address = $config{'sender_email'};
    # If no sender is configured, create a default one.
    unless ($from_address) {
        my $hostname = $ENV{'SERVER_NAME'} || 'localhost';
        $from_address = "noreply@" . $hostname;
    }

    my $subject = "OpenVPN client file from " . ($ENV{'SERVER_NAME'} || 'this site');
    my $body = "Hi,\n\nThis is your OpenVPN file from " . ($ENV{'SERVER_NAME'} || 'this site') . ".\n\nPlease extract and import the file to your OpenVPN client.\n\nThank you!!";

    eval {
        my $msg = MIME::Lite->new(
            From    => $from_address, # Use the new variable here
            To      => $email_to,
            Subject => $subject,
            Type    => 'text/plain',
            Data    => $body
        );
        # ... (rest of the subroutine is the same) ...
        $msg->attach(
            Type     => 'application/octet-stream',
            Path     => $full_path,
            Filename => $filename
        );
        $msg->send('sendmail');
    };
    
    if ($@) {
        &error("Failed to send email: " . &html_escape($@));
    } else {
        # --- THIS IS THE CHANGE ---
        # On success, redirect to our new success page with parameters
        my $encoded_recipient = &urlize($email_to);
        print "Location: successful.cgi?action=email_sent&to=$encoded_recipient\n\n";
    }
}