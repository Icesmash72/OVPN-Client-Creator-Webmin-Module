#!/usr/bin/perl
# index.cgi
#
# This script serves as the main interface for the OpenVPN client creator
# Webmin module.

use strict;
use warnings;

# Define a version for this script for debugging purposes
my $script_version = "1.4"; # Version updated to include email field

# Load the module's library and core Webmin functions.
require './ovpncreator-lib.pl';
our (%text, $module_name);

# Initialize Webmin configuration
&init_config();
our %config;

# --- V-- HEADER AND FORM START --V ---
&ui_print_header(undef, $text{'index_title'}, "");

#print "--- Script Version: $script_version ---\n\n";

# Start the HTML form that submits to create_client.cgi
print &ui_form_start("create_client.cgi", "post");

# --- V-- CLIENT CREATION SECTION --V ---
print &ui_table_start($text{'index_create_client_header'}, "width=100%", 2);

# Input field for the client's name.
print &ui_table_row($text{'index_client_name'},
                    &ui_textbox("client_name", undef, 40));

# Input field for the client's password.
print &ui_table_row($text{'index_client_password'},
                    &ui_password("client_password", undef, 40));

# --- NEW: Optional Client Email Field ---
# This field captures the client's email address. It is not required.
# The 'create_client.cgi' script will need to handle this new 'client_email' input.
# The "||" provides a default label if 'index_client_email' isn't in your language file.
print &ui_table_row($text{'index_client_email'} || "Client's Email (Optional)",
                    &ui_textbox("client_email", undef, 40));
# --- END NEW ---

print &ui_table_end();


# --- V-- MODULE CONFIGURATION SECTION --V ---
print &ui_table_start($text{'index_module_config_header'}, "width=100%", 2);

# Input field for the Easy-RSA path
print &ui_table_row($text{'config_easy_rsa_path'},
                    &ui_textbox("easy_rsa_path", $config{'easy_rsa_path'}, 60));

# Input field for the keys base directory
print &ui_table_row($text{'config_keys_base_dir'},
                    &ui_textbox("keys_base_dir", $config{'keys_base_dir'}, 60));

# Input field for the output base directory
print &ui_table_row($text{'config_output_base_dir'},
                    &ui_textbox("output_base_dir", $config{'output_base_dir'}, 60));

# Input field for the server's public IP address
print &ui_table_row($text{'config_server_public_ip'},
                    &ui_textbox("server_public_ip", $config{'server_public_ip'}, 40));

# ... (inside the MODULE CONFIGURATION SECTION table) ...

# --- NEW: Field for Sender Email Address ---
print &ui_table_row("Sender Email Address",
                    &ui_textbox("sender_email", $config{'sender_email'}, 60));
# --- END NEW ---

# Fields for zip/tar command paths
print &ui_table_row($text{'config_zip_cmd'},
                    &ui_textbox("zip_cmd", $config{'zip_cmd'} || "/usr/bin/zip", 60));

print &ui_table_row($text{'config_tar_cmd'},
                    &ui_textbox("tar_cmd", $config{'tar_cmd'} || "/usr/bin/tar", 60));

print &ui_table_end();


# --- V-- SUBMIT BUTTON AND FORM END --V ---
print &ui_submit($text{'index_create_button'}, "create");

print &ui_form_end();

print "<p>".$text{'index_welcome'}."</p>\n";

&ui_print_footer();