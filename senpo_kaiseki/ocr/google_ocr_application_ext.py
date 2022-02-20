from google_drive_ocr.application import GoogleOCRApplication
from google.oauth2 import service_account
import os
import json
import attr
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']


@attr.s
class GoogleOCRApplicationExt(GoogleOCRApplication):
    client_secret: str = attr.ib(default=None)
    upload_folder_id: str = attr.ib(default=None)
    ocr_suffix: str = attr.ib(default='.google.txt')
    temporary_upload: bool = attr.ib(default=True)
    credentials_path: str = attr.ib(default=None, repr=False)
    scopes: str = attr.ib(default=SCOPES)

    def __attrs_post_init__(self):
        if self.upload_folder_id is None:
            self.upload_folder_id = os.environ['GOOGLE_DIR_ID']
        creds = self.get_credentials()
        self.drive_service = build('drive', 'v3', credentials=creds)

    def get_credentials(self):
        """
        Override GoogleOCRApplication.get_credentials()
        """
        service_account_key = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_KEY"])
        nonscoped_creds = service_account.Credentials.from_service_account_info(service_account_key)
        creds = nonscoped_creds.with_scopes(SCOPES)

        return creds
