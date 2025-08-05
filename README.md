# **OVPN Client Creator for Webmin**

A simple Webmin module to create OpenVPN client configuration files (.ovpn) through an easy-to-use web interface. This module automates the process of generating client keys, signing certificates, and bundling everything into a single archive, ready for distribution via **direct download or email**.

It's designed for system administrators who want to quickly issue new client profiles without needing to use the command line for every new user.

## **Features ✨**

* **Web-Based Interface:** Create clients directly from the Webmin dashboard.  
* **Flexible Delivery Options:**  
  * **Direct Download:** Immediately download the client archive (.zip or .tar.gz).  
  * **Email Delivery:** Send the archive as an attachment directly from the success page.  
* **Configurable Email Sender:** Set a custom "From" address for emails sent by the module.  
* **Secure Key Generation:** Creates a new password-protected 2048-bit RSA private key for each client.  
* **Automatic Signing:** Signs the new client certificate against your existing OpenVPN Certificate Authority (CA).  
* **All-in-One Profile:** Bundles the CA, client certificate, client key, and TLS-Auth key into a single .ovpn file.  
* **Fully Configurable:** All essential paths, server details, and the sender email can be configured from the module's UI.

## **Requirements**

Before installing this module, ensure you have the following set up on your server:

* A working **Webmin** installation.  
* An **OpenVPN server** that is already configured and running.  
* An existing **OpenVPN Certificate Authority**. Specifically, you need read access to:  
  * ca.crt (Your CA's public certificate)  
  * ca.key (Your CA's private key)  
  * ta.key (Your TLS-Auth key)  
* The **zip** or **tar** command-line utility must be installed.  
* **Perl MIME::Lite module** for sending emails. Install it with one of these commands:  
  Bash  
  \# For Debian/Ubuntu  
  sudo apt-get install libmime-lite-perl

  \# For CentOS/RHEL/Fedora  
  sudo yum install perl-MIME-Lite

## **Installation**

You can install the module using your preferred method.

#### **Method 1: Install from Webmin Interface (Recommended)**

1. Download the latest release file (ovpncreator.wbm.gz) from the project's **Releases** page.  
2. Log in to your Webmin panel.  
3. Navigate to **Webmin** \> **Webmin Configuration** \> **Webmin Modules**.  
4. Under "Install Module", select the **From uploaded file** radio button and select the ovpncreator.wbm.gz file you downloaded.  
5. Click the **Install Module** button.

#### **Method 2: Install from Source (Manual)**

1. Clone this repository or download the source code as a ZIP file.  
2. Copy the entire ovpncreator module directory to your Webmin installation path (e.g., /usr/share/webmin/).  
   Bash  
   sudo cp \-r path/to/ovpncreator /usr/share/webmin/

3. In Webmin, navigate to **Webmin** \> **Refresh Modules**.

## **Configuration**

The first time you use the module, you must configure it to point to your server's specific file locations.

Navigate to the **OpenVPN Client Creator** module in Webmin. Fill out the fields in the **Module Configuration** section:

* **Sender Email Address:** The email address that will appear in the "From" field of sent emails (e.g., noreply@yourdomain.com).  
* **OpenVPN Keys Base Directory:** This is the most important path. It's the directory where your ca.key and ta.key files are stored (e.g., /etc/openvpn/server/keys).  
* **Client Output Directory:** A directory where the final client .zip archives will be stored. The Webmin user needs write permissions here (e.g., /root/client-configs).  
* **Server Public IP:** The public IP address or domain name that clients will use to connect to your OpenVPN server.

Click the **Create Client** button to save these settings (you can fill in dummy client info the first time if you only want to save the configuration).

## **How to Use**

1. Navigate to the **OpenVPN Client Creator** module in Webmin.  
2. In the **Create New Client** section, enter:  
   * A unique **Client Name** (no spaces or special characters).  
   * A strong **Client Password**. This password encrypts the client's private key.  
   * **Client's Email (Optional)**. If you enter an email here, it will be pre-filled on the delivery page.  
3. Ensure the paths and details in the **Module Configuration** section are correct.  
4. Click the **Create Client** button.  
5. The page will reload with a log of the creation process. If successful, you will see two options at the bottom:  
   * **Option 1: Download Directly:** Click the button to download the client's .zip file immediately.  
   * **Option 2: Deliver by Mail:** Enter an email address and click "Send Email" to have the archive sent as an attachment.

---

## **File Structure Map**

/OpenVPN-Client-Creator-Webmin-Module/  
├── .git/                     \<-- Git version control directory  
├── changelog.md              \<-- Documents changes for each version  
├── create\_client.cgi         \<-- Script to create the client and .ovpn file  
├── download\_client.cgi       \<-- Script to handle file download or email  
├── images/                   \<-- Folder for module icons (optional)  
│   └── icon.gif  
├── index.cgi                 \<-- The main user interface and settings page  
├── lang/                     \<-- Folder for language/translation files (optional)  
│   └── en.lang  
├── module.info               \<-- Webmin module information file  
├── ovpncreator-lib.pl        \<-- The shared library with helper functions  
├── readme.md                 \<-- The main project documentation  
└── successful.cgi            \<-- The new page that confirms success

#### **⬆️ How to Update from V1.0**

You have two options to update from v1.0 version.

#### **Method 1: Clean Install (Recommended)**

This is the safest and easiest way to ensure everything is set up correctly.

1. In Webmin, go to **Webmin** \-\> **Webmin Configuration** \-\> **Webmin Modules**.  
2. Select your old "OpenVPN Client Creator" module from the list and use the **Delete** button to uninstall it completely.  
3. Download the ovpncreatorv1.1.1.wbm.gz file from this release page (see the "Assets" section below).  
4. From the Webmin Modules page, choose to install a module **From uploaded file** and select the .zip file you just downloaded.  
5. After installation, go to the module's main page and re-enter your configuration settings.

#### **Method 2: Manual File Update**

If you prefer to update the files manually:

1. **Install Dependency:** If you haven't already, install the required Perl module.  
   Bash  
   \# On Debian/Ubuntu  
   sudo apt-get install libmime-lite-perl

2. **Update Files:** In your module directory (/usr/share/webmin/ovpncreator/), do the following:  
   * **REPLACE** these 3 files with the new versions from this release:  
     * index.cgi  
     * create\_client.cgi  
     * download\_client.cgi  
   * **ADD** this new file:  
     * successful.cgi  
   * **(Optional)** Replace README.md and CHANGELOG.md as well.  
3. Go to **Webmin** \-\> **Refresh Modules**.

## **Contributing**

Contributions are welcome\! If you have ideas for improvements, bug fixes, or new features, please:

1. Fork the repository.  
2. Create a new branch (git checkout \-b feature/your-feature-name).  
3. Make your changes.  
4. Commit your changes (git commit \-m 'Add new feature').  
5. Push to the branch (git push origin feature/your-feature-name).  
6. Open a Pull Request.

---

## **License**

This project is licensed under the MIT License \- see the LICENSE file for details.

---

## 
## Disclaimer

<<<<<<< Updated upstream
This project is an independent piece of software and is not affiliated with, sponsored by, or endorsed by OpenVPN Inc. or the developers of Webmin.

All product names, logos, and brands are property of their respective owners.

* **OpenVPN** is a registered trademark of OpenVPN Inc.
* **Webmin** is a registered trademark of its respective owners.
* 
=======

## **Credits**

Developed by Po Hung Chiang

