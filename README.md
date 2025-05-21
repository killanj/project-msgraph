# Project Msgraph

Python module/utility that abstracts away some interactions with Microsoft's Graph API.
Currently includes ways to get sharepoint site IDs with an user-provided domain, get sharepoint drive IDs, generate access tokens with three different scopes,
upload files and send e-mails with attachments.
Before using this utility, make sure to get user consent through Microsoft. Check this link for further information: https://learn.microsoft.com/en-us/entra/identity-platform/permissions-consent-overview

## Features

- Acquire access tokens for Microsoft Graph or custom audiences
- Retrieve SharePoint site and drive IDs
- Upload files to SharePoint document libraries
- Non-halting error handling: This module will return an error object instead of raising any exceptions. Code accordingly.

---
