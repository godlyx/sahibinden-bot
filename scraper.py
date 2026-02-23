import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import re
import threading
import telebot 
from database import veritabani_kur, urun_isle_ve_kiyasla

# --- AYARLAR ---
TOKEN = "8023968347:AAHdnOPqsgLmVePRfeA1X48iB7KDyU7KpRI"
CHAT_ID = "-5204115535"
BEKLEME_SURESI_DAKIKA = 30

# Yeni Filtre ve Hafıza Değişkenleri
MIN_FIYAT = 0
MAKSIMUM_FIYAT = 25000 
SON_FIRSATLAR = [] # /liste komutu için ürünleri hafızada tutacağımız dizi

bot = telebot.TeleBot(TOKEN)

def telegrama_gonder(mesaj):
    try:
        bot.send_message(CHAT_ID, mesaj, parse_mode="HTML", disable_web_page_preview=True)
    except:
        pass

def fiyat_temizle(fiyat_metni):
    try:
        temiz = re.sub(r'[^\d,]', '', fiyat_metni)
        temiz = temiz.replace(',', '.')
        return float(temiz)
    except:
        return 0.0

def vatan_fiyat_avcisi():
    global MIN_FIYAT, MAKSIMUM_FIYAT, SON_FIRSATLAR
    print(f"\n[{time.strftime('%H:%M:%S')}] Vatan Bilgisayar taramaya başlıyor...")
    options = uc.ChromeOptions()
    options.add_argument("--headless") 
    options.add_argument("--window-size=1920,1080")
    
    driver = uc.Chrome(options=options)
    yeni_liste_hafizasi = [] # Bu taramada bulduklarımızı geçici depolayacağımız yer

    try:
        driver.get("https://www.vatanbilgisayar.com/notebook/")
        time.sleep(10) 
        
        urun_kartlari = driver.find_elements(By.CSS_SELECTOR, ".product-list__content")
        islem_goren_sayisi = 0
        bildirim_giden_sayisi = 0

        for kart in urun_kartlari:
            try:
                baslik = kart.find_element(By.CSS_SELECTOR, ".product-list__product-name").text.strip()
                fiyat_metni = kart.find_element(By.CSS_SELECTOR, ".product-list__price").text.strip()
                
                link_elementi = kart.find_element(By.XPATH, "..")
                link = link_elementi.get_attribute("href")
                if not link.startswith("http"): link = "https://www.vatanbilgisayar.com" + link

                sayisal_fiyat = fiyat_temizle(fiyat_metni)

                # MİN VE MAKS ARALIĞI FİLTRESİ
                if MIN_FIYAT <= sayisal_fiyat <= MAKSIMUM_FIYAT:
                    islem_goren_sayisi += 1
                    
                    # /liste komutu için ürünü hafızaya ekliyoruz
                    yeni_liste_hafizasi.append(f"📌 {baslik}\n💰 {sayisal_fiyat} TL\n🔗 <a href='{link}'>Ürüne Git</a>")

                    kiyas_mesaji = urun_isle_ve_kiyasla(ilan_id=link, baslik=baslik, link=link, guncel_fiyat=sayisal_fiyat)

                    if "İNDİRİM YAKALANDI" in kiyas_mesaji or "YENİ İLAN" in kiyas_mesaji:
                        mesaj = f"💻 <b>VATAN BİLGİSAYAR FIRSATI!</b>\n\n📌 <b>Model:</b> {baslik}\n{kiyas_mesaji}\n\n🔗 <a href='{link}'>Ürüne Git</a>"
                        telegrama_gonder(mesaj)
                        bildirim_giden_sayisi += 1
                        time.sleep(1)
            except:
                continue

        # Tarama bitince eski hafızayı silip yeni ürünleri (maksimum 15 adet) kaydediyoruz
        SON_FIRSATLAR = yeni_liste_hafizasi[:15]
        print(f"Tarama bitti: {islem_goren_sayisi} ürün ({MIN_FIYAT}-{MAKSIMUM_FIYAT} TL arası) incelendi, {bildirim_giden_sayisi} fırsat iletildi.")

    finally:
        try:
            driver.quit()
        except:
            pass

# --- TELEGRAM KOMUT DİNLEYİCİLERİ ---
@bot.message_handler(commands=['start', 'yardim'])
def yardim_mesaji(message):
    msg = ("👋 Merhaba patron! Fiyat Avcısı emrine amade.\n\n"
           "<b>Komutlar:</b>\n"
           "/durum - Mevcut ayarları gösterir.\n"
           "/liste - Son taramadaki uygun ürünleri listeler.\n"
           "/fiyat 30000 - Sadece üst sınır belirler (0-30000 TL).\n"
           "/fiyat 15000 30000 - Min ve Max aralık belirler.")
    bot.reply_to(message, msg, parse_mode="HTML")

@bot.message_handler(commands=['fiyat'])
def fiyat_guncelle(message):
    global MIN_FIYAT, MAKSIMUM_FIYAT
    try:
        parametreler = message.text.split()
        if len(parametreler) == 2:
            MIN_FIYAT = 0
            MAKSIMUM_FIYAT = int(parametreler[1])
            bot.reply_to(message, f"✅ Aralık güncellendi: <b>0 TL - {MAKSIMUM_FIYAT} TL</b>", parse_mode="HTML")
        elif len(parametreler) == 3:
            MIN_FIYAT = int(parametreler[1])
            MAKSIMUM_FIYAT = int(parametreler[2])
            bot.reply_to(message, f"✅ Aralık güncellendi: <b>{MIN_FIYAT} TL - {MAKSIMUM_FIYAT} TL</b>", parse_mode="HTML")
        else:
            raise ValueError
        print(f"⚙️ Fiyat sınırı güncellendi: {MIN_FIYAT} - {MAKSIMUM_FIYAT} TL")
    except:
        bot.reply_to(message, "❌ Hatalı kullanım. Şöyle yaz: <code>/fiyat 25000</code> veya <code>/fiyat 15000 30000</code>", parse_mode="HTML")

@bot.message_handler(commands=['liste'])
def listele(message):
    if not SON_FIRSATLAR:
        bot.reply_to(message, "⚠️ Şu an hafızada ürün yok. İlk taramanın bitmesini bekleyin veya belirlediğiniz fiyat aralığında ürün bulunamadı.")
        return
    
    cevap = f"📋 <b>Son Taramadaki Fırsatlar (Max 15)</b>\n\n"
    for urun in SON_FIRSATLAR:
        cevap += urun + "\n\n"
        
    bot.reply_to(message, cevap, parse_mode="HTML", disable_web_page_preview=True)

@bot.message_handler(commands=['durum'])
def durum_bilgisi(message):
    msg = f"📊 <b>Durum Raporu:</b>\n- Tarama: Vatan Bilgisayar\n- Fiyat Aralığı: {MIN_FIYAT} TL - {MAKSIMUM_FIYAT} TL\n- Tarama Aralığı: Her {BEKLEME_SURESI_DAKIKA} dakikada bir.\n- Hafızadaki Ürün Sayısı: {len(SON_FIRSATLAR)}"
    bot.reply_to(message, msg, parse_mode="HTML")

# --- ARKA PLAN TARAMA DÖNGÜSÜ (WORKER THREAD) ---
def tarama_dongusu():
    while True:
        vatan_fiyat_avcisi()
        print(f"⏳ Bot uyku moduna geçti. {BEKLEME_SURESI_DAKIKA} dakika sonra tekrar tarayacak...\n")
        time.sleep(BEKLEME_SURESI_DAKIKA * 60)

# --- ANA ÇALIŞTIRICI ---
if __name__ == "__main__":
    veritabani_kur()
    print("🚀 FİYAT AVCISI BAŞLATILDI! (Aralık Filtresi ve Liste Özelliği Aktif)")
    
    tarama_thread = threading.Thread(target=tarama_dongusu)
    tarama_thread.daemon = True 
    tarama_thread.start()
    
    print("🎧 Telegram dinleyicisi aktif. Komutlar bekleniyor...")
    bot.infinity_polling()