#!/usr/bin/perl
# ovpncreator-lib.pl
#
# This library provides common functions for the OpenVPN Client Creator Webmin module.
# It handles loading Webmin's core libraries, reading/writing module configuration,
# and other utility functions.

use strict;
use warnings;
use File::Basename; # For basename, dirname
use Cwd 'abs_path'; # For absolute paths

# Define a version for this library for debugging purposes
my $lib_version = "1.0.7"; # Increment this version number with significant changes

# Print the library version when it's loaded
print "DEBUG: ovpncreator-lib.pl Version: $lib_version loaded.\n";

# IMPORTANT: Load core Webmin libraries directly.
# web-lib.pl contains functions like ReadParse, init_config, open_lock_file, close_lock_file, etc.
# ui-lib.pl contains functions like ui_print_header, ui_print_footer, ui_textbox, etc.
# Using 'do' for web-lib.pl and 'require' for ui-lib.pl is common in Webmin modules.
# These paths are relative to the Webmin root directory, not the module directory.
# Assuming module is in /usr/share/webmin/ovpncreator/
# So ../web-lib.pl means /usr/share/webmin/web-lib.pl
do '../web-lib.pl';
require '../ui-lib.pl';

# Export necessary global variables that Webmin sets up.
# These are typically populated by init_config() from web-lib.pl
our (%in, %config, %text, $module_name, $module_config_file);

# --- Function: save_module_config_direct ---
# This function directly writes the module's configuration hash to its config file.
# It's a workaround for environments where Webmin's core write_config might not be
# reliably available or correctly namespaced.
#
# Arguments:
#   $config_hash_ref: A reference to the hash containing the configuration to save.
#
sub save_module_config_direct
{
    my ($config_hash_ref) = @_;

    print "DEBUG: Entering save_module_config_direct.\n";
    print "DEBUG: Received configuration values:\n";
    foreach my $key (sort keys %$config_hash_ref) {
        my $value = $config_hash_ref->{$key};
        print "DEBUG:   $key = '" . (defined($value) ? $value : 'NONE') . "'\n";
    }
    print "DEBUG: End of received configuration values.\n";


    # Ensure $module_config_file is defined. It should be set by &init_config().
    if (!defined($module_config_file) || $module_config_file eq '') {
        # Fallback error handling if module_config_file is somehow not set
        # This should ideally not happen if init_config() is called correctly.
        die "ERROR: \$module_config_file is not defined in save_module_config_direct. Cannot save configuration.";
    }

    # Open the configuration file for writing.
    # Use > to truncate and overwrite, as is typical for config files.
    open(my $fh, '>', $module_config_file) or
        die "Failed to open module config file '$module_config_file' for writing: $!";

    # Write each key-value pair from the hash to the file.
    foreach my $key (sort keys %$config_hash_ref) {
        # Escape newlines in values to ensure single-line entries, if needed.
        # For simple key=value pairs, this is usually sufficient.
        my $value = $config_hash_ref->{$key};
        $value =~ s/\n/\\n/g; # Simple escaping for newlines
        print $fh "$key=$value\n";
    }

    close($fh) or die "Failed to close module config file '$module_config_file': $!";

    # Optionally, set permissions (e.g., 0600 for owner-only read/write)
    # This is important for security, as config files can contain sensitive paths.
    chmod 0600, $module_config_file or
        warn "Failed to set permissions on module config file '$module_config_file': $!"; # Use warn instead of die here, as file is already written

    print "DEBUG: Exiting save_module_config_direct.\n";
    return 1; # Indicate success
}

# --- Helper function: read_file_contents ---
# Reads the entire content of a file and returns it as a string.
sub read_file_contents
{
    my ($file) = @_;
    open(my $fh, '<', $file) or die "Cannot open file $file for reading: $!";
    local $/; # Slurp mode
    my $content = <$fh>;
    close($fh);
    return $content;
}

# --- Helper function: write_file_contents ---
# Writes a given string content to a file, overwriting existing content.
sub write_file_contents
{
    my ($file, $content) = @_;
    open(my $fh, '>', $file) or die "Cannot open file $file for writing: $!";
    print $fh $content;
    close($fh);
}

# --- New Function: create_client_archive ---
# Creates a zip or tar.gz archive of the client's .ovpn file.
# Arguments:
#   $client_name: The name of the client (used for filename).
#   $ovpn_file_path: The full path to the generated .ovpn file.
#   $output_dir: The directory where the archive should be created.
# Returns:
#   The full path to the created archive file, or undef on failure.
#
sub create_client_archive
{
    my ($client_name, $ovpn_file_path, $output_dir) = @_;

    print "DEBUG: Entering create_client_archive.\n";
    print "DEBUG: Client Name: $client_name\n";
    print "DEBUG: OVPN File Path: $ovpn_file_path\n";
    print "DEBUG: Output Directory for Archive: $output_dir\n";

    my $archive_cmd;
    my $archive_ext;
    my $archive_full_path;
    my $cmd_output;
    my $exit_code;

    # Determine which archiving tool to use based on configured paths
    # Ensure $config is populated before accessing its keys
    &init_config() if (!%config); # Re-init config if not already done (safety check)
    my $zip_cmd = $config{'zip_cmd'} || "/usr/bin/zip";
    my $tar_cmd = $config{'tar_cmd'} || "/usr/bin/tar";

    # Check for zip command first
    if (-x $zip_cmd) {
        $archive_cmd = $zip_cmd;
        $archive_ext = ".zip";
        $archive_full_path = "$output_dir/$client_name$archive_ext";
        # Change to the directory where the .ovpn file is located for zipping
        my $current_dir = abs_path(Cwd::cwd()); # Get current working directory
        my $ovpn_dir = dirname($ovpn_file_path);
        my $ovpn_filename_only = basename($ovpn_file_path);

        chdir($ovpn_dir) or die "Failed to change directory to $ovpn_dir: $!";
        # Zip command: zip <archive_name> <file_to_add>
        $cmd_output = &backquote_logged("$archive_cmd ".quotemeta($archive_full_path)." ".quotemeta($ovpn_filename_only)." 2>&1");
        $exit_code = $?;
        chdir($current_dir) or die "Failed to change back to $current_dir: $!"; # Change back
    }
    # If zip is not available or failed, try tar
    elsif (-x $tar_cmd) {
        $archive_cmd = $tar_cmd;
        $archive_ext = ".tgz"; # or .tar.gz
        $archive_full_path = "$output_dir/$client_name$archive_ext";
        # Change to the directory where the .ovpn file is located for tarring
        my $current_dir = abs_path(Cwd::cwd()); # Get current working directory
        my $ovpn_dir = dirname($ovpn_file_path);
        my $ovpn_filename_only = basename($ovpn_file_path);

        chdir($ovpn_dir) or die "Failed to change directory to $ovpn_dir: $!";
        # Tar command: tar -czf <archive_name> <file_to_add>
        $cmd_output = &backquote_logged("$archive_cmd -czf ".quotemeta($archive_full_path)." ".quotemeta($ovpn_filename_only)." 2>&1");
        $exit_code = $?;
        chdir($current_dir) or die "Failed to change back to $current_dir: $!"; # Change back
    }
    else {
        print "❌ ERROR: Neither zip ('$zip_cmd') nor tar ('$tar_cmd') command found or executable. Cannot create archive.\n";
        return undef;
    }

    if ($exit_code != 0) {
        print "❌ ERROR: Archiving command failed with exit code ".($exit_code >> 8).". Output:\n$cmd_output\n";
        return undef;
    }
    if (! -e $archive_full_path) {
        print "❌ ERROR: Archiving command reported success, but archive file was NOT created at '$archive_full_path'.\n";
        return undef;
    }

    # Set permissions for the archive file to be readable by others (e.g., web server)
    chmod 0644, $archive_full_path or warn "Could not set permissions on $archive_full_path: $!";
    print "✅ SUCCESS: Archive created at '$archive_full_path' with permissions 0644.\n";
    print "DEBUG: Exiting create_client_archive.\n";

    return $archive_full_path;
}

# Perl modules must return a true value
1;
