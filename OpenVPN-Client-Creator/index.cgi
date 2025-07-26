#!/usr/bin/perl
# index.cgi
#
# This script serves as the main interface for the OpenVPN client creator
# Webmin module. It allows users to input client details (name, password)
# and also configure module-wide settings such as Easy-RSA paths,
# base directories for keys, client output directory, the server's public IP,
# and paths to zipping utilities.
#
# The form submission goes to create_client.cgi, which will be responsible
# for both saving the configuration and generating the client files.

use strict;
use warnings;

# Define a version for this script for debugging purposes
my $script_version = "1.3"; # Increment this version number with significant changes

# Load the module's library and core Webmin functions.
# ovpncreator-lib.pl is now responsible for loading webmin-lib.pl directly.
require './ovpncreator-lib.pl';
our (%text, $module_name); # %text for localization, $module_name is set by init_config()

# Initialize Webmin configuration and read module-specific settings.
# This populates the %config hash with values from /etc/webmin/ovpncreator/config
&init_config();
our %config; # Make %config globally available for this script.

# --- V-- HEADER AND FORM START --V ---
# Print the Webmin header. No header links are needed as config is on this page.
&ui_print_header(undef, $text{'index_title'}, "");

#print "--- Script Version: $script_version ---\n\n"; # Display the script version

# Start the HTML form. This form will submit to create_client.cgi.
# All inputs (client details and module configuration) will be part of this form.
print &ui_form_start("create_client.cgi", "post");

# --- V-- CLIENT CREATION SECTION --V ---
# Table for client-specific inputs (Name and Password)
print &ui_table_start($text{'index_create_client_header'}, "width=100%", 2);

# Input field for the client's name.
print &ui_table_row($text{'index_client_name'},
                    &ui_textbox("client_name", undef, 40));

# Input field for the client's password.
print &ui_table_row($text{'index_client_password'},
                    &ui_password("client_password", undef, 40));

print &ui_table_end(); # End of client creation table.


# --- V-- MODULE CONFIGURATION SECTION --V ---
# Table for module-wide configuration inputs.
# These fields will be pre-populated with values from the %config hash.
print &ui_table_start($text{'index_module_config_header'}, "width=100%", 2);

# Input field for the Easy-RSA path (e.g., /usr/share/easy-rsa).
# Default value is read from $config{'easy_rsa_path'}.
print &ui_table_row($text{'config_easy_rsa_path'},
                    &ui_textbox("easy_rsa_path", $config{'easy_rsa_path'}, 60));

# Input field for the base directory where OpenVPN server keys are stored (e.g., /etc/openvpn/keys/tocobeeusca/).
# Default value is read from $config{'keys_base_dir'}.
print &ui_table_row($text{'config_keys_base_dir'},
                    &ui_textbox("keys_base_dir", $config{'keys_base_dir'}, 60));

# Input field for the output base directory where generated client .ovpn files will be stored (e.g., /root/client-configs).
# Default value is read from $config{'output_base_dir'}.
print &ui_table_row($text{'config_output_base_dir'},
                    &ui_textbox("output_base_dir", $config{'output_base_dir'}, 60));

# Input field for the OpenVPN server's public IP address (e.g., 192.3.105.121).
# Default value is read from $config{'server_public_ip'}.
print &ui_table_row($text{'config_server_public_ip'},
                    &ui_textbox("server_public_ip", $config{'server_public_ip'}, 40));

# --- NEW: Fields for zip/tar command paths ---
print &ui_table_row($text{'config_zip_cmd'},
                    &ui_textbox("zip_cmd", $config{'zip_cmd'} || "/usr/bin/zip", 60));

print &ui_table_row($text{'config_tar_cmd'},
                    &ui_textbox("tar_cmd", $config{'tar_cmd'} || "/usr/bin/tar", 60));
# --- END NEW ---

print &ui_table_end(); # End of module configuration table.


# --- V-- SUBMIT BUTTON AND FORM END --V ---
# Create the submit button. It should be inside the form.
print &ui_submit($text{'index_create_button'}, "create");

# Close the HTML form.
print &ui_form_end();

# Add a welcome message or general information below the form.
print "<p>".$text{'index_welcome'}."</p>\n";

# Print the Webmin footer.
&ui_print_footer();
