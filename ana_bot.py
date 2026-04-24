def pexels_video_indir():
    print("🎬 Pexels'ten video aranıyor...")
    api_key = os.getenv("PEXELS_API_KEY")
    
    if not api_key:
        raise ValueError("❌ HATA: PEXELS_API_KEY bulunamadı! GitHub Secrets kısmını kontrol et.")

    query = random.choice(["nature", "landscape", "mountains", "sea", "forest", "dark nature"])
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=15&orientation=portrait"
    headers = {"Authorization": api_key}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"❌ Pexels API Hatası! Kod: {response.status_code} - Mesaj: {response.text}")

    r = response.json()
    
    if 'videos' not in r or len(r['videos']) == 0:
        raise Exception("❌ Pexels video bulamadı veya API anahtarı yetkisiz.")

    video_data = random.choice(r['videos'])
    video_url = video_data['video_files'][0]['link']
    
    print(f"📥 Video indiriliyor: {query}")
    with open("video.mp4", "wb") as f:
        f.write(requests.get(video_url).content)
    return "video.mp4"
