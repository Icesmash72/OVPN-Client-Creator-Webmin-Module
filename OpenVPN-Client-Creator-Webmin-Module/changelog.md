\# Changelog

All notable changes to this project will be documented in this file.

The format is based on \[Keep a Changelog\](https://keepachangelog.com/en/1.0.0/),  
and this project adheres to \[Semantic Versioning\](https://semver.org/spec/v2.0.0.html).

\---

\#\# \[1.1\] \- 2025-07-27

This version introduces major new features focused on user experience and flexible delivery of client configuration files.

\#\#\# Added

\-   **\*\*Email Delivery:\*\*** Users can now send the generated client archive as an email attachment directly from the success page.  
\-   **\*\*Configurable Sender Address:\*\*** Added a "Sender Email Address" field to the module configuration, allowing administrators to set a custom "From" address for emails.  
\-   **\*\*Dedicated Success Page:\*\*** Created a new confirmation page (\`successful.cgi\`) to provide clear feedback to the user after an email is sent.  
\-   **\*\*Optional Client Email Field:\*\*** Added an optional field on the client creation form to pre-fill the recipient's email address on the delivery page.

\#\#\# Changed

\-   **\*\*Improved UI Flow:\*\*** The client creation success page now presents two clear options: "Download Directly" or "Deliver by Mail."  
\-   **\*\*Robust Redirect Handling:\*\*** Replaced the silent redirect after sending an email with a redirect to the new, user-friendly success page.

\#\#\# Fixed

\-   Resolved a server redirect loop (Post/Redirect/Get issue) that occurred after sending an email.  
\-   Corrected variable scope errors (\`Global symbol requires explicit package name\`) that occurred during script execution.  
\-   Fixed an issue where the form for emailing a client was being submitted with an empty filename.

---

---

**Changelog for OpenVPN Client Creator Webmin Module**

### **Version 1.1.1 \- 2025-07-27 (or today's date)**

**Bug Fixes:**

* **Resolved Hostname Duplication in .ovpn Files:** Fixed an issue where the server hostname would appear twice (e.g., remote yourdomain.comnulyourdomain.com) in the generated .ovpn client configuration files. This was caused by a duplicate input field definition for the server public IP/hostname in the main interface.  
* **Eliminated NULL Characters in Hostname:** Addressed a bug that could cause "NULL" or other unprintable characters to appear within the server hostname in the .ovpn file. The server IP/hostname is now properly sanitized during client file generation to prevent such corruption.

