#!/usr/bin/perl
# successful.cgi
#
# This script displays a generic success message to the user after an
# email has been sent or a download has been initiated, then provides
# a link back to the main module page.

use strict;
use warnings;

# Load the module's library for Webmin UI functions
require './ovpncreator-lib.pl';

# Declare global variables
our (%in, %text);

# Initialize Webmin configuration and UI
&init_config();
&ReadParse();

# Determine which message to show
my $action = $in{'action'};
my $heading = "✅ Success!";
my $message = "The action was completed successfully."; # Default message

if ($action eq 'email_sent') {
    $heading = "📧 Email Sent!";
    my $recipient = &html_escape($in{'to'});
    if ($recipient) {
        $message = "The client configuration has been successfully sent to <strong>$recipient</strong>.";
    } else {
        $message = "The client configuration has been successfully sent.";
    }
}
# Note: The download action streams directly, so this page is primarily for email.
# A future enhancement could use this page for downloads as well.

# Print the Webmin header
&ui_print_header(undef, "Action Successful", "");

print "<h2>$heading</h2>\n";
print "<p>$message</p>\n";

# Print the Webmin footer with a link back to the main page
&ui_print_footer("index.cgi", "Return to Main Page");