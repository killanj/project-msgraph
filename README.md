# Project Msgraph

Python module/utility that abstracts away some interactions with Microsoft's Graph API.
Currently includes ways to get sharepoint site IDs with an user-provided domain, get sharepoint drive IDs, generate access tokens with three different scopes,
upload files and send e-mails with attachments.
Before using this utility, make sure your app has user consent through Microsoft, as well as Microsoft Graph permissions. 
For further information, check the following documentation: 

[Microsoft Permissions Consent Overview](https://learn.microsoft.com/en-us/entra/identity-platform/permissions-consent-overview)

[Microsoft Permissions Reference](https://learn.microsoft.com/en-us/graph/permissions-reference)

## Features

- Acquire access tokens for Microsoft Graph, Outlook or custom audiences
- Retrieve SharePoint site and drive IDs
- Upload files to SharePoint document libraries
- Send e-mails through parameters and a function, add N attachments, send to N e-mail addresses.
- Download files from sharepoint folders
- Non-halting error handling: This module will attempt to return an error object instead of raising exceptions. If this is ever not the case, please let me know!

---
## Usage

Install the package via pip, like so:

```bash

pip install msgraph-pywrap

```

Setup the class like so:

```python
from msgraph.msgraph import Msgraph

credentials = {
    "clientid": "foo",
    "tenantid": "bar",
    "clientsecret": "foz",
    "audience": "foo.sharepoint.com",
    "refresh_token": "bazbazbaz"
}

graph = Msgraph(credentials)
```

From here, you'll have access to the rest of the methods.

For example, here's how you'd get an access token with the Graph API scope, with proper handling:

```python
token_response = graph.get_access_token("graph")

if token_response.is_ok:
    token = token_response.unwrap()
else:
    ...
    # Process upon failure goes here:
```

Or, if you're sure all will be fine:

```python
token = graph.get_access_token("graph").data
```

Just remember to either _unwrap_ the response, or get the _data_ property of the success response in order to actually access the data you want to return.

Let's send an e-mail through Outlook!

```python
from msgraph.msgraph import Msgraph

credentials = {
    "clientid": "foo",
    "tenantid": "bar",
    "clientsecret": "foz",
    "audience": "foo.sharepoint.com",
    "refresh_token": "bazbazbaz"
}

graph = Msgraph(credentials)

token_response = graph.get_access_token("outlook")

if token_response.is_ok:
    token = token_response.unwrap()
else:
    ...
    # Process error here:

result_mail = graph.send_email(token, "any subject", "any message", ["target@emails.com"], ["path/to/attachment"])

if result_mail.is_ok:
    print("E-mail sent!")
else:
    ...
    # Process error here:
```

Most functions will follow this pattern, read the docstrings for the parameters required.

Any bugs found, feel free to open an issue.




