import sqlite3
import datetime

def veritabani_kur():
    # Veritabanı dosyası yoksa oluşturur, varsa bağlanır
    conn = sqlite3.connect('bot_veritabani.db')
    cursor = conn.cursor()

    # Ürünler Tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Urunler (
            ilan_id TEXT PRIMARY KEY,
            baslik TEXT,
            link TEXT
        )
    ''')

    # Fiyat Geçmişi Tablosu (ilan_id, Urunler tablosu ile ilişkili)
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
    conn = sqlite3.connect('bot_veritabani.db')
    cursor = conn.cursor()
    
    su_an = datetime.datetime.now()
    mesaj_ek_metni = "" # Eğer fiyat değiştiyse buraya yazacağız

    # 1. Ürün daha önce kaydedilmiş mi kontrol et
    cursor.execute("SELECT * FROM Urunler WHERE ilan_id=?", (ilan_id,))
    urun_var_mi = cursor.fetchone()

    if not urun_var_mi:
        # Ürün ilk defa görülüyor, Urunler tablosuna ekle
        cursor.execute("INSERT INTO Urunler (ilan_id, baslik, link) VALUES (?, ?, ?)", (ilan_id, baslik, link))
        mesaj_ek_metni = "🆕 Yeni İlan!"
    else:
        # Ürün zaten var, eski fiyatını bulalım
        cursor.execute("SELECT fiyat FROM Fiyat_Gecmisi WHERE ilan_id=? ORDER BY tarih DESC LIMIT 1", (ilan_id,))
        eski_kayit = cursor.fetchone()
        
        if eski_kayit:
            eski_fiyat = eski_kayit[0]
            if guncel_fiyat < eski_fiyat:
                fark = eski_fiyat - guncel_fiyat
                mesaj_ek_metni = f"📉 FİYAT DÜŞTÜ! (Eski: {eski_fiyat} TL - İndirim: {fark} TL)"
            elif guncel_fiyat > eski_fiyat:
                mesaj_ek_metni = f"📈 Fiyat artmış. (Eski: {eski_fiyat} TL)"
            else:
                mesaj_ek_metni = "➖ Fiyat aynı."

    # 2. Güncel fiyatı her halükarda geçmişe kaydet
    cursor.execute("INSERT INTO Fiyat_Gecmisi (ilan_id, fiyat, tarih) VALUES (?, ?, ?)", (ilan_id, guncel_fiyat, su_an))
    
    conn.commit()
    conn.close()
    
    return mesaj_ek_metni


# Bu dosyayı doğrudan çalıştırdığımızda tablolar kurulsun
if __name__ == "__main__":
    veritabani_kur()
    print("Veritabanı ve tablolar başarıyla oluşturuldu!")