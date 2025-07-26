#!/usr/bin/perl
# config.cgi (Revised for compatibility)
use strict;
use warnings;

require './ovpncreator-lib.pl';
our (%in, %config, %text, $module_config_file);

&ReadParse();
if ($in{'save'}) {
    &lock_file($module_config_file);
    # V-- REVISED LINE FOR BETTER COMPATIBILITY --V
    # Explicitly list the variables to save from the form. This is a safer way.
    my @vars_to_save = ('easy_rsa_path', 'keys_base_dir', 'output_base_dir', 'server_public_ip');
    &save_module_config(\%in, \@vars_to_save);
    # A-------------------------------------------A
    &unlock_file($module_config_file);
    &webmin_log("config");
    &redirect(""); # Reload the page to show changes
}

# Use the safe header call
&ui_print_header(undef, $text{'config_title'}, undef);

print &ui_form_start("config.cgi");
print &ui_table_start($text{'config_header'}, "width=100%", 2);

print &ui_table_row($text{'config_easy_rsa_path'},
    &ui_textbox("easy_rsa_path", $config{'easy_rsa_path'}, 60));

print &ui_table_row($text{'config_keys_base_dir'},
    &ui_textbox("keys_base_dir", $config{'keys_base_dir'}, 60));

print &ui_table_row($text{'config_output_base_dir'},
    &ui_textbox("output_base_dir", $config{'output_base_dir'}, 60));

print &ui_table_row($text{'config_server_public_ip'},
    &ui_textbox("server_public_ip", $config{'server_public_ip'}, 60));

print &ui_table_end();
print &ui_form_end([ { 'name' => 'save', 'value' => 'Save' } ]);
&ui_print_footer();