# YouTube Otomatik Video Botu

Bu proje:
1. `data/rusca_sozler.txt` içinden sıradaki sözü alır.
2. `assets/background.mp4` üzerine yazı olarak basar.
3. İstersen `assets/music.mp3` müziğini videoya ekler.
4. `data/youtube_basliklari.txt` ve `data/youtube_aciklamalari.txt` içinden aynı sıradaki başlık/açıklamayı alır.
5. Videoyu YouTube'a yükler.
6. Sırayı `state.json` içine kaydeder.

## Dosya yapısı

```text
youtube_bot_sifirdan/
  main.py
  auth.py
  config.py
  requirements.txt
  data/
    rusca_sozler.txt
    youtube_basliklari.txt
    youtube_aciklamalari.txt
  assets/
    background.mp4
    music.mp3
  output/
```

## Kurulum

```bash
pip install -r requirements.txt
```

## İlk OAuth token alma

Google Cloud Console'dan YouTube Data API v3 aktif et.
OAuth istemci dosyasını indirip proje klasörüne `client_secret.json` adıyla koy.

Sonra yerelde çalıştır:

```bash
python auth.py
```

Bu işlem `token.json` üretir. Bu dosyayı GitHub'a direkt koyma.

## Çalıştırma

```bash
python main.py
```

## GitHub Actions için secrets

Repo Settings > Secrets and variables > Actions kısmına şunları ekle:

- `CLIENT_SECRET_JSON`: `client_secret.json` dosyasının içeriği
- `TOKEN_JSON`: `token.json` dosyasının içeriği

Sonra workflow her gün otomatik çalışabilir.
