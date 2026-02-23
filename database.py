import sqlite3
import datetime

def veritabani_kur():
    conn = sqlite3.connect('bot_veritabani.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Urunler (
            ilan_id TEXT PRIMARY KEY,
            baslik TEXT,
            link TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Fiyat_Gecmisi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ilan_id TEXT,
            fiyat REAL,
            tarih DATETIME
        )
    ''')
    
    conn.commit()
    conn.close()

def urun_isle_ve_kiyasla(ilan_id, baslik, link, guncel_fiyat):
    # Eğer fiyat 0 geldiyse (okunamadıysa) veritabanını bozmamak için işlemi pas geç
    if guncel_fiyat <= 0:
        return "HATA: Fiyat sıfır."

    conn = sqlite3.connect('bot_veritabani.db')
    cursor = conn.cursor()
    su_an = datetime.datetime.now()
    mesaj_ek_metni = "" 

    # Ürün sistemde var mı?
    cursor.execute("SELECT * FROM Urunler WHERE ilan_id=?", (ilan_id,))
    urun_var_mi = cursor.fetchone()

    if not urun_var_mi:
        cursor.execute("INSERT INTO Urunler (ilan_id, baslik, link) VALUES (?, ?, ?)", (ilan_id, baslik, link))
        mesaj_ek_metni = "🆕 YENİ İLAN SİSTEME EKLENDİ!"
    else:
        # Ürün varsa son fiyatını al
        cursor.execute("SELECT fiyat FROM Fiyat_Gecmisi WHERE ilan_id=? ORDER BY tarih DESC LIMIT 1", (ilan_id,))
        eski_kayit = cursor.fetchone()
        
        if eski_kayit:
            eski_fiyat = eski_kayit[0]
            
            # --- KIYASLAMA VE YÜZDE HESABI BURADA ---
            if guncel_fiyat < eski_fiyat:
                fark = eski_fiyat - guncel_fiyat
                yuzde = (fark / eski_fiyat) * 100
                mesaj_ek_metni = f"🔥 İNDİRİM YAKALANDI! %{yuzde:.1f} DÜŞÜŞ!\n📉 Eski: {eski_fiyat:,.2f} TL -> Yeni: {guncel_fiyat:,.2f} TL (Fark: {fark:,.2f} TL)"
            elif guncel_fiyat > eski_fiyat:
                mesaj_ek_metni = f"📈 Fiyat artmış. (Eski: {eski_fiyat:,.2f} TL)"
            else:
                mesaj_ek_metni = "➖ Fiyat aynı."

    # Yeni fiyatı geçmişe kaydet
    cursor.execute("INSERT INTO Fiyat_Gecmisi (ilan_id, fiyat, tarih) VALUES (?, ?, ?)", (ilan_id, guncel_fiyat, su_an))
    
    conn.commit()
    conn.close()
    return mesaj_ek_metni

if __name__ == "__main__":
    veritabani_kur()
    print("Veritabanı hazır!")