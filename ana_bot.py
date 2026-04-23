# --- 5. ANA DÖNGÜ (GÜNLÜK AYARLANMIŞ) ---
if __name__ == "__main__":
    # Paylaşım yapılmasını istediğin saat (Örn: 19:00 için 19 yaz)
    PAYLASIM_SAATI = 19 
    
    print(f"🤖 Otomatik Bot Başlatıldı. Her gün saat {PAYLASIM_SAATI}:00 civarında video gelecek...")
    
    while True:
        try:
            simdi = time.localtime()
            
            # Eğer saat belirlenen saate eşitse paylaşımı başlat
            if simdi.tm_hour == PAYLASIM_SAATI:
                soz = siradaki_sozu_al()
                if not soz: 
                    print("🛑 Söz listesi bitti!")
                    break
                
                video = kurgu_yap(soz)
                if video:
                    youtube_yukle(video, soz)
                    print(f"✅ Günlük video paylaşıldı: {simdi.tm_mday}/{simdi.tm_mon}")
                
                # Aynı saat içinde tekrar paylaşım yapmaması için 1 saat uyut
                print("😴 Günlük görev tamamlandı. Bir sonraki güne kadar bekleniyor...")
                time.sleep(3601) 
            else:
                # Saatin gelip gelmediğini kontrol etmek için 15 dakikada bir uyanır
                print(f"🕒 Saat henüz {PAYLASIM_SAATI}:00 değil (Şu an {simdi.tm_hour}:{simdi.tm_min}). Bekleniyor...")
                time.sleep(900) 
                
        except Exception as e:
            print(f"❌ Kritik Hata: {e}. 5 dk sonra tekrar denenecek...")
            time.sleep(300)