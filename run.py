import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

# Load .env
load_dotenv()
WP_API = os.getenv("WP_API")
WP_USER = os.getenv("WP_USER")
WP_PASS = os.getenv("WP_PASS")
WP_PAGE_ID = os.getenv("WP_PAGE_ID")
WP_PAGE_URL = f"{WP_API}/pages/{WP_PAGE_ID}"

def get_next_data():
    with open("list.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
    if not lines:
        print("📭 Tidak ada data jackpot tersisa.")
        return None
    first = lines[0].strip()
    with open("list.txt", "w", encoding="utf-8") as f:
        f.writelines(lines[1:])
    parts = first.split("|")
    if len(parts) != 5:
        print("❌ Format salah:", first)
        return None
    return {
        "judul": parts[0],
        "gambar": parts[1],
        "selamat": parts[2],
        "link": parts[3],
        "tanggal": parts[4]  # tanggal dari list.txt (manual)
    }

def is_already_uploaded(judul):
    if not os.path.exists("uploaded.txt"):
        with open("uploaded.txt", "w", encoding="utf-8") as f:
            pass
        return False
    with open("uploaded.txt", "r", encoding="utf-8") as f:
        uploaded = f.read().splitlines()
    return judul in uploaded

def mark_as_uploaded(judul):
    with open("uploaded.txt", "a", encoding="utf-8") as f:
        f.write(judul + "\n")

def extract_nominal(judul):
    import re
    match = re.search(r"Rp[.\d]+", judul)
    return match.group(0) if match else "Rp.XXX"

def scrape_post_content(data):
    nominal = extract_nominal(data["judul"])
    userid = data["selamat"].split()[-1]

    content = f"""
    <div class="post-jackpot" style="border: 5px solid yellow; padding: 30px; border-radius: 20px; background-color: white; color: black;">
  <h1><strong>{data['judul']}</strong></h1>

   <img src="{data['gambar']}" alt="{data['judul']}" style="max-width:100%; height:auto; margin:20px 0; border-radius: 8px;">

  <p><strong>Selamat kepada User id : {userid}</strong> telah berhasil mendapatkan kemenangan besar pada permainan <strong>{data['judul']}</strong> sebesar <strong>{nominal}</strong>. Proses pencairan dana dilakukan dengan cepat dan tepat waktu.</p>

  <p>Setelah mengisi formulir withdraw dengan kurung waktu hanya 5 – 10 menit pihak MPO0110 sudah melakukan transfer kepada pemilik Userid dan dana sudah dapat dicairkan oleh pemenang. Bukti pembayaran yang kami berikan merupakan bukti pembayaran yang <strong>SAH / VALID</strong> yang langsung didapatkan melalui tanda transfer transaksi dari Bank yang dituju.</p>

  <p>Kami mengucapkan banyak <em>Terima Kasih</em> kepada pemenang karena sudah mempercayakan kami sebagai Bandar Tepercaya yang membayar semua kemenangan member hingga lunas.</p>

  <p>Masih ragu dengan MPO0110 bos? Di mana bandar togel online sekarang yang terpercaya seperti <strong>MPO0110</strong>? Bandar yang mengirimkan kemenangan member tanpa bertele-tele. Jadi… tidak perlu khawatir pada situs MPO0110 karena kemenangan anda berapapun akan dibayarkan hingga lunas kepada pemenang.</p>

  <h2><strong>INFO SEPUTAR MPO0110 YANG WAJIB DI KETAHUI</strong></h2>

  <p><strong>MPO0110</strong> adalah <a href="#">Situs Togel Online &amp; Slot Online</a> di Indonesia. Dengan menyediakan berbagai macam permainan yang seru dan menarik di MPO0110, maka anda tidak perlu ragu lagi untuk bergabung dan bermain bersama kami situs judi online terpercaya yang akan membayar berapapun kemenangan anda. Hanya dengan 1 User ID anda sudah dapat memainkan semua permainan mulai dari togel, Live casino sampai Slot online yang pastinya seru dan menyenangkan.</p>

  <p>Berikut ini merupakan informasi penting tentang situs MPO0110 yang tidak dapat dijumpai pada bandar togel lainnya seperti:</p>

  <ul>
    <li><strong>Minimum Deposit :</strong> Rp. 10.000,-</li>
    <li><strong>Diskon Togel :</strong> 4D = 66.5% | 3D = 59.5% | 2D = 29.5% (Semua Pasaran Togel)</li>
    <li><strong>Minimal Betting Togel :</strong> Rp. 100,-</li>
    <li><strong>Pasaran Togel Terbaik :</strong> Totomacau, Togel Singapore, Togel Sydney, Togel Hongkong</li>
    <li><strong>Pilihan Mata Uang :</strong> Indonesia Rupiah (IDR)</li>
    <li><strong>Pilihan Bank :</strong> BCA, BRI, BNI, DANAMON, MAYBANK, BSI, PERMATA, PANIN, DANA, OVO, LINKAJA, GOPAY</li>
    <li><strong>Platform :</strong> iOS, Android, Windows</li>
  </ul>

  <p>Salah satu layanan judi terbaik yang diunggulkan MPO0110 lewat layanan judinya adalah adanya fitur livechat 24 jam. Livechat sendiri menjadi sebuah fitur yang sangat penting dan pasti selalu disediakan situs penyedia layanan judi online terpercaya seperti MPO0110. Karena dengan livechat 24 jam, para pemain atau member bisa selalu mudah terhubung pada layanan customer service ketika menemukan kendala atau masalah maupun jika ingin mengetahui informasi lebih lengkap terkait dengan layanan judi MPO0110 melalui layanan CS 24 jam.</p>


    """
    return content

def upload_post_to_wordpress(title, content):
    post_data = {
        "title": title,
        "content": content,
        "status": "publish"
    }
    r = requests.post(f"{WP_API}/posts", json=post_data, auth=HTTPBasicAuth(WP_USER, WP_PASS))
    if r.status_code == 201:
        print("✅ Post berhasil diupload:", title)
        return r.json().get("link")
    else:
        print("❌ Gagal upload post:", r.status_code, r.text)
        return None

def generate_card(data):
    return f"""
    <div class="col-lg-3 mb-2">
        <div class="card card-post h-100 mb-3">
            <div class="row g-0">
                <div class="col-md-12">
                    <img src="{data['gambar']}" class="lazy img-post rounded-start h-100" alt="{data['judul']}">
                </div>
                <div class="col-md-12">
                    <div class="card-body">
                        <h5>{data['judul']}</h5>
                        <p class="time-post text-uppercase"><i class="lni lni-timer"></i> {data['tanggal']}</p>
                        <p>{data['selamat']}</p>
                        <div class="d-grid">
                            <a href="{data['link']}" class="btn btn-primary fw-bold text-white text-uppercase rounded-2 d-flex justify-content-center align-items-center gap-1 px-2 py-1" style="font-size: 12px; height:32px;">
                                <i class="lni lni-cash-app" style="font-size: 14px;"></i> Read More
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """

def clean_entry_content_header(soup):
    entry = soup.find("div", class_="entry-content")
    if not entry:
        print("⚠️ Tidak ditemukan .entry-content.")
        return

    removed = 0
    for tag in entry.find_all(recursive=False):
        if tag.name in ["p", "br", "meta"] and not tag.get_text(strip=True):
            tag.decompose()
            removed += 1
        elif tag.name == "div" and not tag.get_text(strip=True) and not tag.find("img") and not tag.find("h5"):
            tag.decompose()
            removed += 1
        else:
            break  # Stop saat ketemu konten penting (logo, grid jackpot, dsb)

    print(f"🧹 Dihapus {removed} elemen kosong/bermasalah di atas konten.")

def update_content_online(new_card_html):
    # Ambil konten dari halaman WordPress
    r = requests.get(WP_PAGE_URL, auth=HTTPBasicAuth(WP_USER, WP_PASS))
    if r.status_code != 200:
        print("❌ Gagal ambil konten halaman:", r.status_code)
        return

    html = r.json().get("content", {}).get("rendered", "")
    soup = BeautifulSoup(html, "html.parser")

    # ✅ Bersihkan elemen sampah di bagian atas .entry-content
    clean_entry_content_header(soup)

    # Cari kontainer card
    container = soup.find(id="all-jackpot")
    if not container:
        print("❌ Tidak ditemukan id='all-jackpot' di halaman.")
        return

    # Tambahkan card baru ke paling atas
    new_card = BeautifulSoup(new_card_html, "html.parser")
    container.insert(0, new_card)

    # Final update ke WordPress
    final_html = str(soup)
    update = {
        "content": final_html,
        "status": "publish"
    }

    r2 = requests.put(WP_PAGE_URL, json=update, auth=HTTPBasicAuth(WP_USER, WP_PASS))
    if r2.status_code == 200:
        print("✅ Card ditambahkan dan elemen atas dibersihkan.")
    else:
        print("❌ Gagal update:", r2.status_code, r2.text)

def clean_entry_content_header(soup):
    entry = soup.find("div", class_="entry-content")
    if not entry:
        print("⚠️ Tidak ditemukan .entry-content.")
        return

    removed = 0
    for tag in entry.find_all(recursive=False):
        # Hapus <p> kosong, <br>, dan <meta> di awal konten
        if tag.name in ["p", "br", "meta"] and not tag.get_text(strip=True):
            tag.decompose()
            removed += 1
        else:
            break  # Stop saat sudah sampai bagian utama (misal: logo atau card)
    print(f"🧹 Dihapus {removed} elemen sampah di awal .entry-content.")


if __name__ == "__main__":
    data = get_next_data()
    if data:
        if is_already_uploaded(data["link"]):
            print(f"⚠️ Post '{data['link']}' sudah pernah diupload. Melewati...")
        else:
            print("📝 Menyusun konten artikel (template custom)...")
            post_html = scrape_post_content(data)

            print("📰 Upload artikel ke WordPress...")
            wp_post_url = upload_post_to_wordpress(data["link"], post_html)

            if wp_post_url:
                data["link"] = wp_post_url
                mark_as_uploaded(data["link"])  # ✅ Tandai sudah di-upload

                print("🧩 Membuat card HTML...")
                card_html = generate_card(data)

                print("📌 Menambahkan card ke homepage...")
                update_content_online(card_html)
