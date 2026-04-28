from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

from config import CLIENT_SECRET_FILE, TOKEN_FILE

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def main() -> None:
    if not CLIENT_SECRET_FILE.exists():
        raise FileNotFoundError(
            "client_secret.json bulunamadı. Google Cloud'dan indirip proje klasörüne koy."
        )

    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_FILE), SCOPES)
    credentials = flow.run_local_server(port=0)

    TOKEN_FILE.write_text(credentials.to_json(), encoding="utf-8")
    print(f"✅ Token oluşturuldu: {TOKEN_FILE}")


if __name__ == "__main__":
    main()
