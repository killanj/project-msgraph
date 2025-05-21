import os
import requests


class Msgraph:
    def __init__(self, tenantid: str, clientid: str, clientsecret: str, audience: str, refresh_token:str) -> None:
        self.tenantid = tenantid
        self.clientid = clientid  
        self.clientsecret = clientsecret
        self.audience = audience
        self.refresh_token = refresh_token

    def get_access_token(self, mode: str):
        """
        Gets the access token. The "mode" parameter changes the audience scope between the user-specified audience and the Graph API.

        Requires:

        Running mode. "audience" for user-specified audience, "graph" for Graph API.

        This function requires that you declare this class with a valid refresh token and a valid client secret to work.

        Returns:

        Access token as a string.
        """

        match mode:
            case "audience":
                scope = self.audience
            case "graph":
                scope = "https://graph.microsoft.com/.default"
            case _:
                raise Exception("Mode is invalid or not specified. Unable to get a scope. Please specify a mode.")
        
        if not self.refresh_token or self.refresh_token == "":
            raise Exception("Refresh token missing or invalid. Declare this class with a valid refresh token.")
        if not self.clientsecret or self.clientsecret == "":
            raise Exception("Client secret missing or invalid. Declare this class with a valid client secret.")
        
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        r = requests.post(
            url=f'https://login.microsoftonline.com/{self.tenantid}/oauth2/v2.0/token',
            headers=headers,
            data=f'client_id={self.clientid}&scope={scope}&refresh_token={self.refresh_token}&grant_type=refresh_token&client_secret={self.clientsecret}'
        )

        print(r.status_code)
        print(r.json())
        access_token = r.json()["access_token"]
        return access_token

    def get_siteid(self, token: str, site: str) -> str | None:
        """
        Gets the id of the target site within your audience.
        
        Requires:

        Access token with the Graph API scope.

        Target site name

        Returns:

        On success: site id as a string.

        On fail: Nonetype object
        """
        headers = {"Authorization": f"Bearer {token}"}
        r = requests.get(f'https://graph.microsoft.com/v1.0/sites/{self.audience}:/sites/{site}', headers=headers)
        
        if r.ok:
            return r.json().get("id")
        else:
            return None

    def get_driverid(self, token: str, siteid: str):
        """
        Gets the id of the target site id's root drive.

        Requires:

        Access token with the Graph API scope.

        Target site's id.

        Returns:

        On success: drive id as a string.

        On fail: Nonetype object
        """
        headers = {"Authorization": f"Bearer {token}"}
        
        r = requests.get(f"https://graph.microsoft.com/v1.0/sites/{siteid}/drives", headers=headers)
        
        if r.ok:
            return r.json().get("value")[0]['id']
        else:
            return None

    def upload_to_drive(self, token, driveid, filepath, destination, mimetype = ""):
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
        if mimetype == "":
            headers = {
                "Authorization": f"Bearer {token}"
            }
        else:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": mimetype
            }
        
        filename = os.path.basename(filepath)
        
        url = f"https://graph.microsoft.com/v1.0/drives/{driveid}/root:/{destination}/{filename}:/content"
        
        with open(filepath, "rb") as file:
            content = file.read()
        
        response = requests.put(url, headers=headers, data=content)

        return response.status_code
