import os
import requests
import base64

class MsgraphError:
    def __init__(self, message: str, status_code: int | None, response_content: str | None):
        self.message = message
        self.status_code = status_code
        self.response_content = response_content
    
    def __str__(self):
        return str({
            "message": self.message,
            "status_code": self.status_code,
            "response_content": self.response_content
        })
        
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.message}, {self.status_code}, {self.response_content})"
    
    def as_dict(self) -> str:
        return {
            "message": self.message,
            "status_code": self.status_code,
            "response_content": self.response_content
        }

class MsgraphResponse:
    def __init__(self, message: str, status_code: int, data: str):
        self.message = message
        self.status_code = status_code
        self.data = data
    
    def __str__(self) -> str:
        return str({
            "message": self.message,
            "status_code": self.status_code,
            "data": self.data
        })
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.message}, {self.status_code}, {self.data})"
    
    def as_dict(self) -> dict:
        return {
            "message": self.message,
            "status_code": self.status_code,
            "data": self.data
        }

class Msgraph:
    def __init__(self, credentials: dict):
        self.tenantid = credentials['tenantid']
        self.clientid = credentials['clientid']
        self.clientsecret = credentials['clientsecret']
        self.audience = credentials['audience']
        self.refresh_token = credentials['refresh_token']

    def get_access_token(self, mode: str) -> MsgraphResponse | MsgraphError:
        """
        Gets the access token. The "mode" parameter changes the audience scope between the user-specified audience, Outlook and the Graph API. 

        Requires:

        Running mode. "audience" for user-specified audience, "graph" for Graph API, "outlook" for, well, Outlook.

        Returns:

        On success: MsgraphResponse object

        On fail: MsgraphError object
        """

        match mode:
            case "audience":
                scope = f"https://{self.audience}/.default"
            case "graph":
                scope = "https://graph.microsoft.com/.default"
            case "outlook":
                scope = "Mail.Read User.Read"
            case _:
                message = "Mode is invalid or not specified. Unable to get a scope. Please specify a mode."
                return MsgraphError(message, None, None)
                
        
        
        if not self.refresh_token or self.refresh_token == "":
            message = "Refresh token missing or invalid. Declare this class with a valid refresh token."
            return MsgraphError(message, None, None)
        if not self.clientsecret or self.clientsecret == "":
            message = "Client secret missing or invalid. Declare this class with a valid client secret."
            return MsgraphError(message, None, None)
        if not self.tenantid or self.tenantid == "":
            message = "Tenant ID missing or invalid. Declare this class with a valid tenant ID."
            return MsgraphError(message, None, None)
        
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        data = {
            "client_id": self.clientid,
            "scope": scope,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token",
            "client_secret": self.clientsecret
        }
        
        response = requests.post(
            url=f'https://login.microsoftonline.com/{self.tenantid}/oauth2/v2.0/token',
            headers=headers,
            data=data
        )

        if response.ok:
            return MsgraphResponse("Token retrieved successfully", response.status_code, response.json()["access_token"])
        else:
            return MsgraphError("Failed to fetch access_token.", response.status_code, response.text)
            

    def get_siteid(self, token: str, site: str) -> MsgraphResponse | MsgraphError:
        """
        Gets the id of the target site within your audience.
        
        Requires:

        Access token with the Graph API scope.

        Target site name

        Returns:

        On success: MsgraphResponse object

        On fail: MsgraphError object
        """
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f'https://graph.microsoft.com/v1.0/sites/{self.audience}:/sites/{site}', headers=headers)
        
        if response.ok:
            return MsgraphResponse("Successfully retrieved site id.", response.status_code, response.json().get("id"))
        else:
            return MsgraphError(f"Failed to fetch siteid for {self.audience}/sites/{site}", response.status_code, response.text)

    def get_driverid(self, token: str, siteid: str) -> MsgraphResponse | MsgraphError:
        """
        Gets the id of the target site id's root drive.

        Requires:

        Access token with the Graph API scope.

        Target site's id.

        Returns:

        On success: MsgraphResponse object.

        On fail: MsgraphError object.
        """
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(f"https://graph.microsoft.com/v1.0/sites/{siteid}/drives", headers=headers)
        
        if response.ok:
            return MsgraphResponse("Successfully retrieved site id.", response.status_code, response.json().get("value")[0]['id'])
        else:
            return MsgraphError(f"Failed to fetch driver id for site id '{siteid}'.", response.status_code, response.text)

    def upload_to_drive(self, token, driveid, filepath, destination, mimetype = "") -> MsgraphResponse | MsgraphError:
        """
        Uploads a file to Sharepoint.

        Requires:

        Access token with the Graph API scope.

        Target site's drive id.

        Path of the target file in your machine.

        Destination folder path within Sharepoint (do NOT end with "/")

        OPTIONAL: Mime-type of the file. Microsoft can handle it in some cases, but other file formats may need their mime-types specified.

        Returns: 

        Status code of response.
        """
        if mimetype:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": mimetype
            }
        else:
            headers = {
                "Authorization": f"Bearer {token}"
            }
        
        filename = os.path.basename(filepath)
        
        url = f"https://graph.microsoft.com/v1.0/drives/{driveid}/root:/{destination}/{filename}:/content"
        
        with open(filepath, "rb") as file:
            content = file.read()
        
        response = requests.put(url, headers=headers, data=content)

        if response.ok:
            MsgraphResponse("File uploaded successfully", response.status_code, response.text)
        else:
            MsgraphError("Failed to upload file.", response.status_code, response.text)
    
    def send_email(self, token: str, subject: str, body: str, target_emails: list[str], attachments: list[str] = None) -> MsgraphResponse | MsgraphError:
        """
        Sends an email to the target user(s), with attachments if specified.
        If attachments are needed to be specified, they must be represented as a list of absolute paths to the files.
        
        Requires:
        
        Access token with the Outlook scope.

        Subject of the email.

        Body of the email.

        List of recipients.

        Returns:
        
        On success: MsgraphResponse object.

        On fail: MsgraphError object.
        """
        
        url = "https://graph.microsoft.com/v1.0/me/sendMail"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }

        body = {
            "subject": subject,
            "body": {
                "content": body
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": email
                    }
                } 
                for email in target_emails
            ]
        }
        
        
        if attachments:
            try:
                body["attachments"] = [
                    {
                        "@odata.type": "#microsoft.graph.fileAttachment",
                        "name": os.path.basename(attachment),
                        "contentBytes": base64.b64encode(open(attachment, 'rb').read()).decode('utf-8')
                    }
                    for attachment in attachments
                ]
            except Exception as e:
                return MsgraphError(f"Failed to attach files: {e}", None, None)

        response = requests.post(url, headers=headers, json=body)

        if response.ok:
            return MsgraphResponse("Email sent successfully", response.status_code, response.json())
        else:
            return MsgraphError("Failed to send email.", response.status_code, response.text)

