import os

import requests

from fs25_backuper.logger import Logger
from fs25_backuper.error import AuthenticationError, DownloadError


class Downloader:
    logger = Logger().get_logger()

    def __init__(self, config):
        self.__login_payload = {
            "username": config.username,
            "password": config.password,
            "login": "Login",
        }

        self.url = config.url
        self.savegame = config.savegame

        self.session = requests.Session()

        self._authenticate()

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()

    @property
    def _login_payload(self):
        return self.__login_payload

    def _authenticate(self):
        try:
            auth_url = f"{self.url}/index.html?lang=en"
            response = self.session.post(auth_url, data=self._login_payload)

            response.raise_for_status()

            if "Logout" not in response.text:  # TODO: improve login check
                raise AuthenticationError(
                    "Login failed, please check your credentials."
                )

            self.logger.debug("Login successful!")

        except requests.exceptions.ConnectionError as e:
            raise DownloadError(f"Connection error: {str(e)}") from e
        except requests.exceptions.RequestException as e:
            raise AuthenticationError(f"Authentication request failed: {str(e)}") from e

    def get_savegame(self):
        self.logger.info("Downloading savegame...")

        try:
            savegame_response = self.session.get(
                f"{self.url}/{self.savegame}", stream=True
            )
            savegame_response.raise_for_status()
            return savegame_response
        except requests.exceptions.ConnectionError as e:
            raise DownloadError(f"Connection error: {str(e)}") from e
        except requests.exceptions.RequestException as e:
            raise DownloadError(f"Download failed: {str(e)}") from e

    def write_savegame(self, bytes_stream, savegame_path):
        try:
            self.logger.debug(f"Writing savegame to {savegame_path}")

            with open(savegame_path, "wb") as f:
                for chunk in bytes_stream.iter_content(chunk_size=8192):
                    f.write(chunk)
        except OSError as e:
            if os.path.exists(savegame_path):
                os.remove(savegame_path)

            raise DownloadError(f"File system error: {str(e)}") from e
        finally:
            bytes_stream.close()

        self.logger.info(f"Savegame written to {savegame_path}")

    def download_savegame(self, path):
        savegame_data = self.get_savegame()
        self.write_savegame(savegame_data, savegame_path=path)
        self.logger.info("Savegame downloaded and saved successfully.")
