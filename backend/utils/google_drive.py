import os
from datetime import datetime
from typing import List, Dict, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io


class GoogleDriveClient:
    """Handle Google Drive OAuth and file operations"""

    def __init__(self, token_record=None):
        self.token_record = token_record
        self.credentials = None

        if token_record:
            self.credentials = Credentials(
                token=token_record.access_token,
                refresh_token=token_record.refresh_token,
                token_uri='https://oauth2.googleapis.com/token',
                client_id=os.getenv('GOOGLE_CLIENT_ID'),
                client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
                scopes=self._get_scopes()
            )

            # Set expiry if available
            if token_record.token_expiry:
                self.credentials.expiry = token_record.token_expiry

    def _get_scopes(self) -> List[str]:
        """Get OAuth scopes"""
        scopes_str = os.getenv('GOOGLE_SCOPES', 'https://www.googleapis.com/auth/drive.readonly')
        return [s.strip() for s in scopes_str.strip("[]'\"").split(',')]

    def get_authorization_url(self) -> str:
        """Get OAuth authorization URL"""
        client_config = {
            "web": {
                "client_id": os.getenv('GOOGLE_CLIENT_ID'),
                "client_secret": os.getenv('GOOGLE_CLIENT_SECRET'),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [os.getenv('GOOGLE_REDIRECT_URI')]
            }
        }

        flow = Flow.from_client_config(
            client_config,
            scopes=self._get_scopes(),
            redirect_uri=os.getenv('GOOGLE_REDIRECT_URI')
        )

        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )

        return auth_url

    def exchange_code(self, code: str) -> Credentials:
        """Exchange authorization code for credentials"""
        client_config = {
            "web": {
                "client_id": os.getenv('GOOGLE_CLIENT_ID'),
                "client_secret": os.getenv('GOOGLE_CLIENT_SECRET'),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [os.getenv('GOOGLE_REDIRECT_URI')]
            }
        }

        flow = Flow.from_client_config(
            client_config,
            scopes=self._get_scopes(),
            redirect_uri=os.getenv('GOOGLE_REDIRECT_URI')
        )

        flow.fetch_token(code=code)

        return flow.credentials

    def _get_service(self):
        """Get Google Drive service"""
        if not self.credentials:
            raise Exception("Not authenticated with Google Drive")

        return build('drive', 'v3', credentials=self.credentials)

    def list_pdf_files(self, max_results: int = 100) -> List[Dict]:
        """
        List PDF files from Google Drive
        Returns list of dicts: {id, name, size, modified_time}
        """
        try:
            service = self._get_service()

            # Query for PDF files
            query = "mimeType='application/pdf' and trashed=false"

            results = service.files().list(
                q=query,
                pageSize=max_results,
                fields="files(id, name, size, modifiedTime, mimeType)",
                orderBy="modifiedTime desc"
            ).execute()

            files = results.get('files', [])

            return [
                {
                    'id': file['id'],
                    'name': file['name'],
                    'size': int(file.get('size', 0)),
                    'modified_time': file.get('modifiedTime'),
                    'mime_type': file.get('mimeType')
                }
                for file in files
            ]

        except Exception as e:
            raise Exception(f"Error listing Google Drive files: {str(e)}")

    def download_file(self, file_id: str, download_folder: str) -> Dict:
        """
        Download file from Google Drive
        Returns: {name, path, size}
        """
        try:
            service = self._get_service()

            # Get file metadata
            file_metadata = service.files().get(
                fileId=file_id,
                fields="name, size, mimeType"
            ).execute()

            file_name = file_metadata['name']
            file_size = int(file_metadata.get('size', 0))

            # Ensure filename is safe
            from werkzeug.utils import secure_filename
            safe_filename = secure_filename(file_name)

            # Add timestamp to avoid conflicts
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{safe_filename}"
            file_path = os.path.join(download_folder, unique_filename)

            # Download file
            request = service.files().get_media(fileId=file_id)
            file_handle = io.BytesIO()

            downloader = MediaIoBaseDownload(file_handle, request)
            done = False

            while not done:
                status, done = downloader.next_chunk()

            # Write to disk
            with open(file_path, 'wb') as f:
                f.write(file_handle.getvalue())

            return {
                'name': file_name,
                'path': file_path,
                'size': file_size
            }

        except Exception as e:
            raise Exception(f"Error downloading file from Google Drive: {str(e)}")

    def get_file_info(self, file_id: str) -> Dict:
        """Get file metadata"""
        try:
            service = self._get_service()

            file_metadata = service.files().get(
                fileId=file_id,
                fields="id, name, size, mimeType, modifiedTime"
            ).execute()

            return {
                'id': file_metadata['id'],
                'name': file_metadata['name'],
                'size': int(file_metadata.get('size', 0)),
                'mime_type': file_metadata.get('mimeType'),
                'modified_time': file_metadata.get('modifiedTime')
            }

        except Exception as e:
            raise Exception(f"Error getting file info: {str(e)}")
