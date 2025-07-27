#!/usr/bin/perl
# create_client.cgi
#
# This script processes the form submission from index.cgi, saves the configuration,
# generates client files, creates a compressed archive, and presents a success
# page with options to download the archive or have it emailed.

use strict;
use warnings;
use File::Basename;
use File::Path qw(make_path remove_tree);

# Define a version for this script for debugging purposes
my $script_version = "2.1"; # Corrected variable scope and added verification

# Load the module's library
require './ovpncreator-lib.pl';

# Initialize Webmin configuration
&init_config();

# Declare global variables
our (%in, %config, %text, $module_name, $module_config_file);

# Print the page header
&ui_print_header(undef, "Creating OpenVPN Client", undef);

# --- 1. Read Inputs and Validate Submission ---
&ReadParse();

if (!defined($in{'client_name'}) || $in{'client_name'} eq '') {
    print "<h1>❌ Error: Missing Information</h1>\n";
    print "<p>Please <a href='index.cgi'>return to the main page</a> to create a client.</p>\n";
    &ui_print_footer();
    exit;
}

print "<h1>Client Creation Process Log</h1>";
print "<pre>\n";

print "--- Script Version: $script_version ---\n\n";

print "--- Step 1: Reading Inputs and Saving Configuration ---\n";

# Extract client-specific inputs
my $client_name = $in{'client_name'};
my $client_pass = $in{'client_password'};
my $client_email = $in{'client_email'} || ''; # Default to empty string if not provided

# Validate essential client inputs
die "❌ Error: Client name is required." unless $client_name;
die "❌ Error: Client password is required." unless $client_pass;

# --- Configuration saving logic ---
&lock_file($module_config_file);
$config{'easy_rsa_path'} = $in{'easy_rsa_path'};
$config{'keys_base_dir'} = $in{'keys_base_dir'};
$config{'output_base_dir'} = $in{'output_base_dir'};
$config{'server_public_ip'} = $in{'server_public_ip'};
# --- NEW: Save the sender email address ---
$config{'sender_email'} = $in{'sender_email'};
# --- END NEW ---
$config{'zip_cmd'} = $in{'zip_cmd'};
$config{'tar_cmd'} = $in{'tar_cmd'};
&save_module_config_direct(\%config);
&unlock_file($module_config_file);

my $easy_rsa_path = $config{'easy_rsa_path'};
my $keys_base_dir = $config{'keys_base_dir'};
my $output_base_dir = $config{'output_base_dir'};
my $server_ip = $config{'server_public_ip'};

# --- 2. Auto-Setup Output Directory ---
print "--- Step 2: Preparing Output Directory ---\n";
make_path($output_base_dir, { mode => 0700 }) unless -d $output_base_dir;
print "✅ Output directory '$output_base_dir' is ready.\n\n";

my $client_outdir = "$output_base_dir/$client_name";
die "❌ Error: Client directory or file '$client_outdir' already exists." if -e $client_outdir;
make_path($client_outdir, { mode => 0700 }) or die "Failed to create client directory $client_outdir: $!";
print "✅ Created client-specific directory '$client_outdir'.\n\n";

# --- 3. Define all paths for temporary files ---
my $key_file = "$client_outdir/$client_name.key";
my $csr_file = "$client_outdir/$client_name.csr";
my $crt_file = "$client_outdir/$client_name.crt";
# --- THIS IS THE IMPORTANT DECLARATION ---
my $ovpn_file = "$output_base_dir/$client_name.ovpn";

print "--- Step 3: Defining File Paths ---\n";
print "Final OVPN will be at: $ovpn_file\n\n";
my $subj_string = "/C=TW/ST=Taiwan/L=Taipei/O=PanadaWorkshop/OU=Clients/CN=$client_name/emailAddress=postmaster\@tocobee.tw";

# --- 4. Execute OpenSSL Commands ---
print "--- Step 4: Generating Keys and Certificates ---\n";
my $cmd1 = "openssl genpkey -algorithm RSA -aes256 -pass pass:".quotemeta($client_pass)." -out ".quotemeta($key_file)." -pkeyopt rsa_keygen_bits:2048";
die "❌ FAILED to generate private key." if system($cmd1) != 0;
chmod 0600, $key_file;
print "✅ Private key created.\n";

my $cmd2 = "openssl req -new -key ".quotemeta($key_file)." -out ".quotemeta($csr_file)." -passin pass:".quotemeta($client_pass)." -subj ".quotemeta($subj_string);
die "❌ FAILED to generate CSR." if system($cmd2) != 0;
print "✅ CSR created.\n";

my $ca_cert = "$keys_base_dir/ca.crt";
my $ca_key = "$keys_base_dir/ca.key";
die "❌ Error: CA Certificate not found at '$ca_cert'." unless -e $ca_cert;
die "❌ Error: CA Key not found at '$ca_key'." unless -e $ca_key;

my $cmd3 = "openssl x509 -req -in ".quotemeta($csr_file)." -CA ".quotemeta($ca_cert)." -CAkey ".quotemeta($ca_key)." -CAcreateserial -out ".quotemeta($crt_file)." -days 3650 -sha256";
die "❌ FAILED to sign certificate." if system($cmd3) != 0;
print "✅ Certificate signed.\n\n";

# --- 5. Assemble the final .ovpn file ---
print "--- Step 5: Assembling $client_name.ovpn ---\n";
my $ca_content = &read_file_contents($ca_cert);
my $crt_content = &read_file_contents($crt_file);
my $key_content = &read_file_contents($key_file);
my $ta_key_file = "$keys_base_dir/ta.key";
die "❌ Error: TLS Auth Key (ta.key) not found at '$ta_key_file'." unless -e $ta_key_file;
my $ta_key_content = &read_file_contents($ta_key_file);

my $ovpn_content = "client\ndev tun\nproto udp\nremote $server_ip 1194\nresolv-retry infinite\nnobind\npersist-key\npersist-tun\ncipher AES-256-GCM\nauth SHA256\nremote-cert-tls server\nverb 3\n\n<ca>\n$ca_content\n</ca>\n\n<cert>\n$crt_content\n</cert>\n\n<key>\n$key_content\n</key>\n\n<tls-auth>\n$ta_key_content\n</tls-auth>\nkey-direction 1\n";
&write_file_contents($ovpn_file, $ovpn_content);
chmod 0644, $ovpn_file;
print "✅ Final .ovpn file created at '$ovpn_file'.\n\n";

# --- Step 5.4: Verifying .ovpn file before archiving ---
print "--- Step 5.4: Verifying .ovpn file before archiving ---\n";
if (-e $ovpn_file && -r $ovpn_file && -s $ovpn_file) {
    print "✅ Verification PASSED: File exists, is readable, and is not empty at '$ovpn_file'.\n";
} else {
    my $error_reason = !-e $ovpn_file ? "it does NOT exist." : !-r $ovpn_file ? "it is NOT readable." : "it is EMPTY.";
    die("❌ FATAL ERROR: Cannot archive the .ovpn file because $error_reason Path: '$ovpn_file'");
}

# --- Step 5.5: Creating Client Archive ---
print "--- Step 5.5: Creating Client Archive ---\n";
my $archive_file_path = &create_client_archive($client_name, $ovpn_file, $output_base_dir);
die "❌ FATAL ERROR: Failed to create client archive." unless defined($archive_file_path);
print "✅ SUCCESS: Client archive created at '$archive_file_path'.\n\n";

# --- Step 6: Cleaning up temporary files ---
print "--- Step 6: Cleaning up temporary files ---\n";
remove_tree($client_outdir) or warn "Failed to remove temporary directory '$client_outdir': $!";
print "✅ Removed temporary directory '$client_outdir'.\n";
unlink($ovpn_file) or warn "Failed to remove .ovpn file '$ovpn_file' after archiving: $!";
print "✅ Removed original .ovpn file '$ovpn_file'.\n\n";

# --- FINAL STEP: Generate Success Page with Options ---
print "</pre>"; # Close the log output

# Prepare variables for the HTML output
my $archive_filename = basename($archive_file_path);
my $download_url = "/ovpncreator/download_client.cgi?file=" . &urlize($archive_filename);

# HTML-escape variables to prevent XSS
my $escaped_client_name = &html_escape($client_name);
my $escaped_email = &html_escape($client_email);
# This is the corrected line:
my $escaped_archive_filename = &html_escape($archive_filename);

# Print the final HTML success page
print << "HTML";
<hr>
<style>
    .success-container { padding: 15px; border: 1px solid #d4d4d4; border-radius: 5px; background-color: #f9f9f9; }
    .option-box { margin-top: 15px; padding: 10px; border: 1px solid #ccc; }
    .option-box h4 { margin-top: 0; }
    input[type="email"], button { padding: 8px; margin-top: 5px; }
</style>
<div class="success-container">
    <h2>✅ Client '$escaped_client_name' Created Successfully!</h2>
    <p>The configuration archive <strong>$escaped_archive_filename</strong> is ready.</p>
    <div class="option-box">
        <h4>Option 1: Download Directly ⬇️</h4>
        <a href="$download_url" class="btn btn-primary">Download Client Configuration</a>
    </div>
    <div class="option-box">
        <h4>Option 2: Deliver by Mail 📧</h4>
        <form action="/ovpncreator/download_client.cgi" method="POST">
            <input type="hidden" name="file" value="$escaped_archive_filename">
            <input type="hidden" name="action" value="send_email">
            <label for="email_to"><b>Recipient's Email:</b></label><br>
            <input type="email" name="email_to" id="email_to" required placeholder="you\\\@example.com" size="40" value="$escaped_email">
            <br>
            <button type="submit" class="btn btn-success">Send Email</button>
        </form>
    </div>
</div>
HTML

&ui_print_footer();;
