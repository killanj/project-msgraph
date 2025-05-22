import pytest
import msgraph.msgraph as msgraph
from unittest.mock import patch

# This is the "tests" file for the project
# It's the first time I ever wrote any tests, be advised. Any untested cases, open an issue.


def success_response(*args, **kwargs):
    class MockResponse:
        status_code = 200
        def json(self): return {"access_token": "77777777777777777777777"}
        @property
        def ok(self): return True
    return MockResponse()


def error_response(*args, **kwargs):
    class MockResponse:
        status_code = 400
        text = "Bad Request"
        @property
        def ok(self): return False
    return MockResponse()

@pytest.fixture

def test_creds():
    return {
        "clientid": "1234567890n",
        "clientsecret": "1234567890m",
        "tenantid": "1234567890l",
        "refresh_token": "1234567890k",
        "audience": "test.sharepoint.com"
    }

# ---------------------------------------------------------------------------------
#-------------------------- GET ACCESS TOKEN TESTS --------------------------------

def test_get_access_token(test_creds):
    with patch("requests.post", side_effect=success_response):
        msgraph = msgraph.Msgraph(test_creds)
        response = msgraph.get_access_token("graph")
        assert response.is_ok()
        response = msgraph.get_access_token("audience")
        assert response.is_ok()
        response = msgraph.get_access_token("outlook")
        assert response.is_ok()

def test_get_access_token_failure(test_creds):
    with patch("requests.post", side_effect=error_response):
        msgraph = msgraph.Msgraph(test_creds)
        response = msgraph.get_access_token("invalid_mode")
        assert response.is_err()
    
# ---------------------------------------------------------------------------------
#-------------------------- GET SITE ID TESTS -------------------------------------

def test_get_siteid(test_creds):
    with patch("requests.get", side_effect=success_response):
        msgraph = msgraph.Msgraph(test_creds)
        response = msgraph.get_siteid("77777777777777777777777", "Communications_site")
        assert response.is_ok()

def test_get_siteid_failure(test_creds):
    with patch("requests.get", side_effect=error_response):
        msgraph = msgraph.Msgraph(test_creds)
        response = msgraph.get_siteid("WRONG_TOKEN", "Communications_site")
        assert response.is_err()

# ---------------------------------------------------------------------------------
#-------------------------- GET DRIVE ID TESTS ------------------------------------

def test_get_driveid(test_creds):
    with patch("requests.get", side_effect=success_response):
        msgraph = msgraph.Msgraph(test_creds)
        response = msgraph.get_driveid("77777777777777777777777", "CORRECT_SITE_ID")
        assert response.is_ok()

def test_get_driveid_failure(test_creds):
    with patch("requests.get", side_effect=error_response):
        msgraph = msgraph.Msgraph(test_creds)
        response = msgraph.get_driveid("WRONG_TOKEN", "WRONG_SITE_ID")
        assert response.is_err()

# ---------------------------------------------------------------------------------
#-------------------------- UPLOAD TO DRIVE TESTS ---------------------------------

def test_upload_to_drive(test_creds):
    with patch("requests.post", side_effect=success_response):
        msgraph = msgraph.Msgraph(test_creds)
        response = msgraph.upload_to_drive("77777777777777777777777", "CORRECT_DRIVE_ID", "C:\\Users\\User\\Desktop\\test.txt", "testfolder", "text/plain")
        assert response.is_ok()

def test_upload_to_drive_failure(test_creds):
    with patch("requests.post", side_effect=error_response):
        msgraph = msgraph.Msgraph(test_creds)
        response = msgraph.upload_to_drive("WRONG_TOKEN", "WRONG_DRIVE_ID", "C:\\Users\\User\\Desktop\\test.txt", "testfolder", "text/plain")
        assert response.is_err()

# ---------------------------------------------------------------------------------
#-------------------------- SEND EMAIL TESTS --------------------------------------

def test_send_email(test_creds):
    with patch("requests.post", side_effect=success_response):
        msgraph = msgraph.Msgraph(test_creds)
        response = msgraph.send_email(
            "77777777777777777777777", 
            "About E-mail send tests...", 
            "This e-mail was sent!", 
            ["test@test.com"], 
            ["C:\\Users\\User\\Desktop\\test.txt"]
            )
        assert response.is_ok()

def test_send_email_failure(test_creds):
    with patch("requests.post", side_effect=error_response):
        msgraph = msgraph.Msgraph(test_creds)
        response = msgraph.send_email(
            "WRONG_TOKEN", 
            "About E-mail send tests...", 
            "This e-mail was NOT sent!", 
            ["test@test.com"],
            ["C:\\Users\\User\\Desktop\\test.txt"]
            )
        assert response.is_err()

# ---------------------------------------------------------------------------------
#-------------------------- LIST FILES SHAREPOINT TESTS ---------------------------

def test_list_files_sharepoint(test_creds):
    with patch("requests.get", side_effect=success_response):
        msgraph = msgraph.Msgraph(test_creds)
        response = msgraph.list_files_sharepoint("77777777777777777777777", "CORRECT_SITE_ID", "CORRECT_DRIVE_ID", "testfolder")
        assert response.is_ok()

def test_list_files_sharepoint_failure(test_creds):
    with patch("requests.get", side_effect=error_response):
        msgraph = msgraph.Msgraph(test_creds)
        response = msgraph.list_files_sharepoint("WRONG_TOKEN", "WRONG_SITE_ID", "WRONG_DRIVE_ID", "testfolder")
        assert response.is_err()

# ---------------------------------------------------------------------------------
#-------------------------- DOWNLOAD FILE SHAREPOINT TESTS -----------------------

def test_download_file_sharepoint(test_creds):
    with patch("requests.get", side_effect=success_response):
        msgraph = msgraph.Msgraph(test_creds)
        response = msgraph.download_file_sharepoint("77777777777777777777777", "CORRECT_SITE_ID", "CORRECT_DRIVE_ID", "testfolder", "test.txt", "C:\\Users\\User\\Desktop")
        assert response.is_ok()

def test_download_file_sharepoint_failure(test_creds):
    with patch("requests.get", side_effect=error_response):
        msgraph = msgraph.Msgraph(test_creds)
        response = msgraph.download_file_sharepoint("WRONG_TOKEN", "WRONG_SITE_ID", "WRONG_DRIVE_ID", "testfolder", "test.txt", "C:\\Users\\User\\Desktop")
        assert response.is_err()

# ---------------------------------------------------------------------------------
