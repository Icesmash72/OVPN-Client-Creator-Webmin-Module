# **OpenVPN Client Creator for Webmin**

A simple Webmin module to create OpenVPN client configuration files (.ovpn) through an easy-to-use web interface. This module automates the process of generating client keys, signing certificates, and bundling everything into a single, downloadable .zip archive.

It's designed for system administrators who want to quickly issue new client profiles without needing to use the command line for every new user.

---

## **Features**

* **Web-Based Interface**: Create clients directly from the Webmin dashboard.  
* **Secure Key Generation**: Creates a new password-protected 2048-bit RSA private key for each client.  
* **Automatic Signing**: Signs the new client certificate against your existing OpenVPN Certificate Authority (CA).  
* **All-in-One Profile**: Bundles the CA, client certificate, client key, and TLS-Auth key into a single .ovpn file.  
* **Easy Distribution**: Compresses the final .ovpn file into a .zip archive and provides a direct download link.  
* **Fully Configurable**: All essential paths (keys directory, output directory, server IP, etc.) can be configured from the module's UI.

---

## **Requirements**

Before installing this module, ensure you have the following set up on your server:

* A working **Webmin** installation.  
* An **OpenVPN server** that is already configured and running.  
* An existing **OpenVPN Certificate Authority**. Specifically, you need access to:  
  * ca.crt (Your CA's public certificate)  
  * ca.key (Your CA's private key)  
  * ta.key (Your TLS-Auth key)  
* The zip or tar command-line utility must be installed.

---

## **Installation**

You can install the module in two ways: directly from a release file via the Webmin interface (easiest method) or manually from the source code.

### **Method 1: Install from Webmin Interface** 

This is the easiest method for users not familiar with the command line.

1. Download the latest release file (ovpncreator.wbm.gz) from the project's releases page.  
2. Log in to your Webmin panel.  
3. Navigate to **Webmin** \> **Webmin Configuration** \> **Webmin Modules**.  
4. Under "Install Module", select the **From uploaded file** radio button and use the file browser to select the ovpncreator.wbm.gz file you downloaded.  
5. Click the **Install Module** button.

### **Method 2: Install from Source (Manual)**

1. Clone the GitHub repository or download the source code as a ZIP file.  
2. Copy the entire ovpncreator module directory to your Webmin installation path (e.g., /usr/share/webmin/).  
   Bash  
   sudo cp \-r ovpncreator /usr/share/webmin/

3. Log in to Webmin, navigate to **Webmin** \> **Refresh Modules**, and click the "Refresh Modules" button.

---

## 

## 

## 

## **Configuration**

The first time you use the module, you must configure it to point to your server's specific file locations.

1. Navigate to the **OpenVPN Client Creator** module in Webmin.  
2. Fill out the fields in the **Module Configuration** section:  
   * **Easy-RSA Path**: The path to your Easy-RSA installation (e.g., /usr/share/easy-rsa). This field is present but not actively used in the current version's openssl commands, though it's good practice to set it.  
   * **OpenVPN Keys Base Directory**: **This is the most important path.** It's the directory where your ca.key and ta.key files are stored (e.g., /etc/openvpn/server/keys). The module needs read access to these files.  
   * **Client Output Directory**: A directory where the final client .zip archives will be stored. The Webmin user (often root) needs write permissions here (e.g., /root/client-configs).  
   * **Server Public IP**: The public IP address or domain name that clients will use to connect to your OpenVPN server.  
3. Click the **Create Client & Save Config** button to save these settings (you can fill in dummy client info the first time if you just want to save the config).

---

## **How to Use**

1. Navigate to the **OpenVPN Client Creator** module in Webmin.  
2. In the **Create New Client** section, enter a unique **Client Name** (no spaces or special characters).  
3. Enter a strong **Client Password**. This password encrypts the client's private key.  
4. Ensure the paths in the **Module Configuration** section are correct.  
5. Click the **Create Client & Save Config** button.  
6. The page will reload with a log of the creation process. If successful, a download link for the client's .zip file will appear at the bottom.

---

## **File Structure Map**

Here is the structure of the module's files and a description of their roles.

ovpncreator/  
├── index.cgi           \# The main user interface page.  
├── create\_client.cgi     \# The backend script that handles client creation.  
├── download\_client.cgi   \# Handles the secure download of the generated .zip archive.  
├── ovpncreator-lib.pl  \# A shared library containing helper functions.  
├── module.info         \# The core Webmin file that defines the module.  
└── lang/  
    └── en              \# The English language localization file.

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

## **Disclaimer**

This software is provided "as is," without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and non-infringement. In no event shall the authors or copyright holders be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the software or the use or other dealings in the software.

---

## **Credits**

Developed by Po Hung Chiang

