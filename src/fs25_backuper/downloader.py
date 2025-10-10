import os
from pathlib import Path

import requests

from fs25_backuper.config import Config
from fs25_backuper.error import AuthenticationError, DownloadError
from fs25_backuper.logger import Logger


class Downloader:
    def __init__(self, config: Config) -> None:
        self.logger = Logger().get_logger(config.log_level)
        self.__login_payload = {
            "username": config.login.get_secret_value(),
            "password": config.password.get_secret_value(),
            "login": "Login",
        }

        self.url = config.url
        self.savegame = config.savegame

        self.session = requests.Session()

        self._authenticate()

    def __enter__(self) -> "Downloader":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:  # type: ignore
        self.session.close()
        self.cleanup()

    @property
    def _login_payload(self) -> dict:
        return self.__login_payload

    def _authenticate(self) -> None:
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

    def get_savegame(self) -> requests.Response:
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

    def write_savegame(
        self, savegame_response: requests.Response, savegame_path: Path
    ) -> None:
        try:
            self.logger.debug(f"Writing savegame to {savegame_path}")

            with open(savegame_path, "wb") as f:
                for chunk in savegame_response.iter_content(chunk_size=8192):
                    f.write(chunk)

            self._savedgame_path = savegame_path
        except OSError as e:
            if os.path.exists(savegame_path):
                os.remove(savegame_path)

            raise DownloadError(f"File system error: {str(e)}") from e
        finally:
            savegame_response.close()

        self.logger.info(f"Savegame written to {savegame_path}")

    def download_savegame(self, path: Path) -> None:
        savegame_data = self.get_savegame()
        self.write_savegame(savegame_data, savegame_path=path)
        self.logger.info("Savegame downloaded and saved successfully.")

    def cleanup(self) -> None:
        self.logger.debug("Cleaning up downloaded savegame")
        if hasattr(self, "_savedgame_path") and os.path.exists(self._savedgame_path):
            try:
                os.remove(self._savedgame_path)
                self.logger.debug(
                    f"Temporary savegame file {self._savedgame_path} deleted."
                )
            except OSError as e:
                self.logger.error(f"Failed to delete temporary savegame file: {str(e)}")
