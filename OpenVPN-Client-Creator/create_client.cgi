#!/usr/bin/perl
# create_client.cgi
#
# This script processes the form submission from index.cgi,
# saves the module configuration, generates OpenVPN client keys and certificates,
# assembles the .ovpn configuration file, creates a compressed archive of it,
# and provides a download link to the archive.
#
# Debugging has been enhanced with 'ls -l' commands to show directory contents
# and file permissions at various stages.
# Also includes debug prints for module configuration path variables.

use strict;
use warnings;
use File::Basename;
use File::Path qw(make_path remove_tree); # For robust directory creation/deletion

# Define a version for this script for debugging purposes
my $script_version = "1.9"; # Increment this version number with significant changes

# Load the module's library which now includes the direct config saving function
# and the file helper functions (read_file_contents, write_file_contents, create_client_archive).
# ovpncreator-lib.pl is responsible for loading WebminCore and other globals.
require './ovpncreator-lib.pl'; # This will also print the ovpncreator-lib.pl version.

# Initialize Webmin configuration. This MUST be called early to set up %config,
# $module_name, $module_config_file, and other globals.
&init_config();

# Declare global variables that are populated by init_config() or ReadParse()
our (%in, %config, %text, $module_name, $module_config_file);

# Print the page header
&ui_print_header(undef, "Creating OpenVPN Client", undef);

# --- 1. Read Inputs and Validate Submission ---
&ReadParse(); # Parse CGI input parameters into %in

# --- FIX: Check for Form Submission ---
# This script is a form handler. If it's accessed directly without the
# required form data, it should not proceed. We check for a key field
# like 'client_name'. If it's missing, we show a graceful error instead of crashing.
if (!defined($in{'client_name'}) || $in{'client_name'} eq '') {
    print "<h1>❌ Error: Missing Information</h1>\n";
    print "<p>This script must be called from the client creation form. It appears you have accessed it directly or the form was not submitted correctly.</p>\n";
    print "<p>Please <a href='index.cgi'>return to the main page</a> to create a client.</p>\n";
    &ui_print_footer();
    exit; # Stop execution gracefully
}
# --- END FIX ---


print "<h1>Client Creation Process Log</h1>";
print "<pre>\n"; # Use <pre> for formatted output of the log.

print "--- Script Version: $script_version ---\n\n"; # Display the script version

print "--- Step 1: Reading Inputs and Saving Configuration ---\n";

# Extract client-specific inputs
my $client_name = $in{'client_name'};
my $client_pass = $in{'client_password'};

# Validate essential client inputs
if (!$client_name) {
    die "❌ Error: Client name is required.";
}
if (!$client_pass) {
    die "❌ Error: Client password is required.";
}

# --- Debugging module config path ---
print "DEBUG: \$module_name = '$module_name'\n";
print "DEBUG: \$module_config_file = '$module_config_file'\n";
if (!defined($module_name) || $module_name eq '') {
    die "❌ FATAL ERROR: \$module_name is not defined or empty. This indicates a core Webmin module setup issue.";
}
if (!defined($module_config_file) || $module_config_file eq '') {
    die "❌ FATAL ERROR: \$module_config_file is not defined or empty. This indicates a core Webmin module setup issue.";
}
print "DEBUG: Module configuration path appears correctly set.\n\n";
# --- End Debugging ---

# Lock the configuration file to prevent race conditions during write
&lock_file($module_config_file);

# --- MODIFIED: Manually update %config and use &save_module_config_direct ---
# Update the %config hash with the new values from the form
$config{'easy_rsa_path'} = $in{'easy_rsa_path'};
$config{'keys_base_dir'} = $in{'keys_base_dir'};
$config{'output_base_dir'} = $in{'output_base_dir'};
$config{'server_public_ip'} = $in{'server_public_ip'};
$config{'zip_cmd'} = $in{'zip_cmd'}; # Save new zip command path
$config{'tar_cmd'} = $in{'tar_cmd'}; # Save new tar command path

# Save the updated %config hash to the module's configuration file using our direct function
# This function is defined in ovpncreator-lib.pl
&save_module_config_direct(\%config);
# --- END MODIFIED ---

# Unlock the configuration file
&unlock_file($module_config_file);

# --- NEW DEBUG STEP: Display config file contents after saving ---
print "--- DEBUG: Contents of '$module_config_file' after saving ---\n";
system("cat ".quotemeta($module_config_file));
print "------------------------------------------------------------\n\n";
# --- END NEW DEBUG STEP ---

# Use the (potentially updated) configuration values
my $easy_rsa_path = $config{'easy_rsa_path'};
my $keys_base_dir = $config{'keys_base_dir'};
my $output_base_dir = $config{'output_base_dir'};
my $server_ip = $config{'server_public_ip'};

# Basic validation for configuration paths
if (!$easy_rsa_path || !-d $easy_rsa_path) {
    die "❌ Error: Easy-RSA Directory Path is not set or does not exist: '$easy_rsa_path'. Please configure it.";
}
if (!$keys_base_dir || !-d $keys_base_dir) {
    die "❌ Error: OpenVPN Keys Base Directory is not set or does not exist: '$keys_base_dir'. Please configure it.";
}
if (!$output_base_dir) { # Output dir might not exist yet, so only check if set
    die "❌ Error: Client Output Directory is not set. Please configure it.";
}
if (!$server_ip) {
    die "❌ Error: Server Public IP Address is not set. Please configure it.";
}

print "Configuration saved and loaded:\n";
print "Easy-RSA Path: $easy_rsa_path\n";
print "Keys Base Directory: $keys_base_dir\n";
print "Output Base Directory: $output_base_dir\n";
print "Server IP: $server_ip\n\n";


# --- 2. Auto-Setup Output Directory ---
print "--- Step 2: Preparing Output Directory ---\n";
# Create the main output directory if it doesn't exist.
# Using make_path for robustness, with mode 0700 for owner-only access.
if (!-d $output_base_dir) {
    print "Output directory '$output_base_dir' not found. Creating it...\n";
    make_path($output_base_dir, { mode => 0700 }) or die "Failed to create directory $output_base_dir: $!";
    print "✅ Created '$output_base_dir' with permissions 0700.\n";
} else {
    print "Output directory '$output_base_dir' already exists.\n";
}
print "Current contents of $output_base_dir:\n";
system("ls -ld ".quotemeta($output_base_dir)); # Show directory itself
system("ls -l ".quotemeta($output_base_dir)); # Show contents
print "✅ Output directory is ready.\n\n";

# Define client-specific output directory
my $client_outdir = "$output_base_dir/$client_name";
if (-e $client_outdir) { # Check if it exists as file or dir
    die "❌ Error: Client directory or file '$client_outdir' already exists. Please choose a different client name or remove the existing one.";
}
make_path($client_outdir, { mode => 0700 }) or die "Failed to create client directory $client_outdir: $!";
print "✅ Created client-specific directory '$client_outdir' with permissions 0700.\n";
print "Current contents of $client_outdir:\n";
system("ls -ld ".quotemeta($client_outdir)); # Show directory itself
system("ls -l ".quotemeta($client_outdir)); # Show contents
print "\n";


# --- 3. Define all paths for temporary files ---
# These files will be generated inside the client's dedicated directory
my $key_file = "$client_outdir/$client_name.key";
my $csr_file = "$client_outdir/$client_name.csr";
my $crt_file = "$client_outdir/$client_name.crt";
my $ovpn_file = "$output_base_dir/$client_name.ovpn"; # Final .ovpn in the main output dir

print "--- Step 3: Defining File Paths ---\n";
print "Client Key will be at: $key_file\n";
print "Client CSR will be at: $csr_file\n";
print "Client Cert will be at: $crt_file\n";
print "Final OVPN will be at: $ovpn_file\n\n";

# Subject string for the CSR
my $subj_string = "/C=TW/ST=Taiwan/L=Taipei/O=PanadaWorkshop/OU=Clients/CN=$client_name/emailAddress=postmaster\@tocobee.tw";


# --- 4. Execute OpenSSL Commands with Robust Error Checking ---
print "-> Running: openssl genpkey...\n";
my $cmd1 = "openssl genpkey -algorithm RSA -aes256 -pass pass:".quotemeta($client_pass)." -out ".quotemeta($key_file)." -pkeyopt rsa_keygen_bits:2048";
my $exit_code1 = system($cmd1);
if ($exit_code1 != 0) {
    die "❌ FAILED to generate private key. Exit code: " . ($exit_code1 >> 8) . ".\nCommand: $cmd1";
}
if (! -e $key_file) {
    die "❌ FAILED: OpenSSL reported success, but the key file was NOT created at '$key_file'. This is likely a permissions or environment error.";
}
# Set restrictive permissions for the private key
chmod 0600, $key_file or warn "Could not set permissions on $key_file: $!";
print "✅ SUCCESS: Private key created at '$key_file' with permissions 0600.\n";
print "Current contents of $client_outdir after key generation:\n";
system("ls -l ".quotemeta($client_outdir));
print "\n";


# Generate CSR
print "-> Running: openssl req...\n";
my $cmd2 = "openssl req -new -key ".quotemeta($key_file)." -out ".quotemeta($csr_file)." -passin pass:".quotemeta($client_pass)." -subj ".quotemeta($subj_string);
my $exit_code2 = system($cmd2);
if ($exit_code2 != 0) {
    die "❌ FAILED to generate CSR. Exit code: " . ($exit_code2 >> 8) . ".\nCommand: $cmd2";
}
if (! -e $csr_file) {
    die "❌ FAILED: OpenSSL reported success, but the CSR file was NOT created at '$csr_file'.";
}
print "✅ SUCCESS: CSR created at '$csr_file'\n";
print "Current contents of $client_outdir after CSR generation:\n";
system("ls -l ".quotemeta($client_outdir));
print "\n";


# Sign Certificate
my $ca_cert = "$keys_base_dir/ca.crt";
my $ca_key = "$keys_base_dir/ca.key"; # Assuming ca.key is directly in keys_base_dir

# Validate CA files existence
if (!-e $ca_cert) {
    die "❌ Error: CA Certificate not found at '$ca_cert'. Please ensure it exists and is readable.";
}
if (!-e $ca_key) {
    die "❌ Error: CA Key not found at '$ca_key'. Please ensure it exists and is readable.";
}

print "-> Running: openssl x509 (Signing with CA key: $ca_key)...\n";
my $cmd3 = "openssl x509 -req -in ".quotemeta($csr_file)." -CA ".quotemeta($ca_cert)." -CAkey ".quotemeta($ca_key)." -CAcreateserial -out ".quotemeta($crt_file)." -days 3650 -sha256";
my $exit_code3 = system($cmd3);
if ($exit_code3 != 0) {
    die "❌ FAILED to sign certificate. Exit code: " . ($exit_code3 >> 8) . ". This is likely a permissions error reading '$ca_key' or writing to '$crt_file'.\nCommand: $cmd3";
}
if (! -e $crt_file) {
    die "❌ FAILED: OpenSSL reported success, but the certificate file was NOT created at '$crt_file'.";
}
print "✅ SUCCESS: Certificate signed and created at '$crt_file'\n";
print "Current contents of $client_outdir after certificate generation:\n";
system("ls -l ".quotemeta($client_outdir));
print "\n";


# --- 5. Assemble the final .ovpn file ---
print "--- Step 5: Assembling $client_name.ovpn ---\n";
my $ca_content = &read_file_contents($ca_cert);
my $crt_content = &read_file_contents($crt_file);
my $key_content = &read_file_contents($key_file);

# --- NEW: Read ta.key content ---
my $ta_key_file = "$keys_base_dir/ta.key";
if (!-e $ta_key_file) {
    die "❌ Error: TLS Auth Key (ta.key) not found at '$ta_key_file'. This is required for the .ovpn configuration.";
}
my $ta_key_content = &read_file_contents($ta_key_file);
# --- END NEW ---

my $ovpn_content = "client
dev tun
proto udp
remote $server_ip 1194
resolv-retry infinite
nobind
persist-key
persist-tun
cipher AES-256-GCM
auth SHA256
remote-cert-tls server
verb 3

<ca>
$ca_content
</ca>

<cert>
$crt_content
</cert>

<key>
$key_content
</key>

<tls-auth>
$ta_key_content
</tls-auth>
key-direction 1
"; # Added key-direction 1 based on working .sh script

&write_file_contents($ovpn_file, $ovpn_content);
# Set permissions for the .ovpn file to be readable by others (e.g., web server)
chmod 0644, $ovpn_file or warn "Could not set permissions on $ovpn_file: $!";
print "✅ SUCCESS: Final .ovpn file created at '$ovpn_file' with permissions 0644.\n";
print "Current contents of $output_base_dir after OVPN file creation:\n";
system("ls -l ".quotemeta($output_base_dir));
print "\n";

# --- NEW: Create archive of the .ovpn file ---
print "--- Step 5.5: Creating Client Archive ---\n";
my $archive_file_path = &create_client_archive($client_name, $ovpn_file, $output_base_dir);

if (!defined($archive_file_path)) {
    die "❌ FATAL ERROR: Failed to create client archive. Check previous debug messages for details.";
}
print "✅ SUCCESS: Client archive created at '$archive_file_path'.\n\n";
# --- END NEW ---


# --- 6. Clean up temporary files and provide download link ---
print "--- Step 6: Cleaning up temporary files ---\n";
# Remove the temporary client-specific directory and its contents
print "Contents of $client_outdir before cleanup:\n";
system("ls -l ".quotemeta($client_outdir));
remove_tree($client_outdir) or warn "Failed to remove temporary directory '$client_outdir': $!";
print "✅ Cleanup complete: Removed temporary directory '$client_outdir'.\n";

# Remove the .ovpn file now that it's in the archive
if (-e $ovpn_file) {
    unlink($ovpn_file) or warn "Failed to remove .ovpn file '$ovpn_file' after archiving: $!";
    print "✅ Removed original .ovpn file '$ovpn_file'.\n";
} else {
    print "DEBUG: Original .ovpn file '$ovpn_file' not found for removal (might have been moved/removed by archive command).\n";
}
print "Contents of $output_base_dir after cleanup:\n";
system("ls -l ".quotemeta($output_base_dir)); # Show main output dir after client dir is removed
print "\n";


# Generate the download URL for the client archive.
# The download_client.cgi script will need to be updated to serve the archive.
my $download_url = "/ovpncreator/download_client.cgi?file=" . &urlize(basename($archive_file_path));
# FIX: Construct the success message explicitly to ensure the link is correct.
my $success_message = "Client $client_name created successfully! <a href=\"$download_url\">Download client configuration</a>";
print "<h3>$success_message</h3>";

print "</pre>"; # Close the <pre> tag
&ui_print_footer();
