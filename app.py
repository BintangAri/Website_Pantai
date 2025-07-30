import os
import base64
import time
import numpy as np
import streamlit as st
import tensorflow as tf
from PIL import Image
from tensorflow.keras.preprocessing import image
from supabase import create_client, Client
from postgrest.exceptions import APIError  

# ======== Setup Supabase ========
supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(supabase_url, supabase_key)

# ======== Lokasi Pantai & Deskripsi ========
lokasi_pantai = {
    'Pantai Sanur': [-8.6972, 115.2625],
    'Pantai Nusa Dua': [-8.8089, 115.2250],
    'Pantai Pandawa': [-8.8485, 115.1889],
    'Pantai Uluwatu': [-8.8296, 115.0884],
    'Pantai Padang Padang': [-8.8055, 115.0914],
    'Pantai Keramas': [-8.5795, 115.3527],
    'Pantai Amed': [-8.3346, 115.6783],
    'Pantai Tulamben': [-8.2735, 115.6111],
    'Pantai Blue Lagoon': [-8.5157, 115.5195]
}

penjelasan_pantai = {
    "Pantai Sanur": "Pantai Sanur terkenal dengan suasana tenang, cocok untuk piknik keluarga dan memiliki jalur pejalan kaki yang nyaman.",
    "Pantai Nusa Dua": "Pantai ini memiliki fasilitas lengkap, ombak tenang, dan sering menjadi tujuan liburan keluarga.",
    "Pantai Pandawa": "Pantai tersembunyi di balik tebing, cocok untuk keluarga dengan akses mudah dan pemandangan indah.",
    "Pantai Uluwatu": "Terkenal dengan ombak besar dan tebing tinggi, Uluwatu adalah surga bagi peselancar profesional.",
    "Pantai Padang Padang": "Pantai kecil dengan ombak menantang, populer di kalangan peselancar dan wisatawan asing.",
    "Pantai Keramas": "Pantai ini menawarkan ombak tinggi dan sering digunakan untuk kompetisi surfing internasional.",
    "Pantai Amed": "Terkenal dengan air jernih dan kapal karam Jepang. Cocok untuk snorkeling dan melihat biota laut.",
    "Pantai Tulamben": "Daya tarik utama adalah bangkai kapal USAT Liberty dan terumbu karang yang indah untuk snorkeling.",
    "Pantai Blue Lagoon": "Air biru jernih, spot ikan tropis, dan perairan tenang membuat pantai ini ideal untuk snorkeling pemula."
}

# ======== Fungsi Autentikasi ========
def register_user(username, password):
    try:
        response = supabase.table("users").insert({"username": username, "password": password}).execute()
        return True
    except APIError as e:
        if e.message and "duplicate key value" in e.message:
            return False
        else:
            raise e  # biar error selain duplikat tetap muncul


def validate_login(username, password):
    result = supabase.table("users").select("*").eq("username", username).eq("password", password).execute()
    return len(result.data) > 0


# ======== Utils ========
def img_to_base64(file_path):
    with open(file_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# ======== Halaman Login ========
def halaman_login():
    kiri_base64 = img_to_base64("gapurakiri.png")
    kanan_base64 = img_to_base64("gapurakanan.png")

    st.markdown("""
        <style>
        .container-gapura {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: 20px;
        }
        .gapura-img {
            transition: transform 1.5s ease-in-out;
            width: 100%;
            max-width: 150px;
        }
        .gapura-kiri.geser { transform: translateX(-300px); }
        .gapura-kanan.geser { transform: translateX(300px); }
        .login-box { text-align: center; padding: 20px; }
        </style>
    """, unsafe_allow_html=True)

    if "gapura_open" not in st.session_state:
        st.session_state["gapura_open"] = False

    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        st.markdown(f"""<div class="container-gapura">
            <img src="data:image/png;base64,{kiri_base64}" class="gapura-img gapura-kiri {'geser' if st.session_state['gapura_open'] else ''}">
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.title("🔐 Login")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):
            if validate_login(username, password):
                st.session_state["gapura_open"] = True
                st.session_state["username_temp"] = username
                st.experimental_rerun()  # dulu: st.experimental_rerun()
            else:
                st.error("❌ Username atau password salah!")

        st.markdown("Belum punya akun?")
        if st.button("➡️ Daftar Sekarang"):
            st.session_state["page"] = "register"
            st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown(f"""<div class="container-gapura">
            <img src="data:image/png;base64,{kanan_base64}" class="gapura-img gapura-kanan {'geser' if st.session_state['gapura_open'] else ''}">
        </div>""", unsafe_allow_html=True)

# ======== Halaman Registrasi ========
def halaman_registrasi():
    st.title("📝 Registrasi")
    new_user = st.text_input("Buat Username", key="reg_user")
    new_pass = st.text_input("Buat Password", type="password", key="reg_pass")
    if st.button("Registrasi"):
        if register_user(new_user, new_pass):
            st.success("✅ Registrasi berhasil! Silakan login.")
            st.session_state["page"] = "login"
            st.experimental_rerun()
        else:
            st.warning("⚠️ Username sudah digunakan.")
    st.markdown("Sudah punya akun?")
    if st.button("⬅️ Kembali ke Login"):
        st.session_state["page"] = "login"
        st.experimental_rerun()

# ======== Halaman Utama ========
def halaman_utama():
    st.title("🌴 Selamat Datang di Aplikasi Rekomendasi Pantai Bali 🏖️")
    st.markdown("""
        <div style="text-align: justify; font-size: 18px;">
            Aplikasi ini menggunakan teknologi <b>Artificial Intelligence</b> untuk merekomendasikan kategori pantai
            berdasarkan gambar yang Anda unggah. Setelah itu, Anda akan mendapatkan informasi dan rekomendasi tempat pantai
            terbaik di Bali sesuai dengan kategori tersebut.
        </div>
    """, unsafe_allow_html=True)

# ======== Halaman Klasifikasi Pantai ========
def halaman_klasifikasi():
    st.title("🏖️ Rekomendasi Pantai dari Foto")

    @st.cache_resource
    def load_model():
        model_path = "modeljadi_1_lr0.0001_drop0.3.h5"
        gdrive_id = "1iBRcD_IGIJy6jG9J09zp4-8NkW_LbVyD"
        url = f"https://drive.google.com/uc?id={gdrive_id}"

    if not os.path.exists(model_path):
        gdown.download(url, model_path, quiet=False)
    
    return tf.keras.models.load_model(model_path, compile=False)
    class_names = ['Pantai Family', 'Pantai Surfing', 'Pantai Snorkeling']
    rekomendasi_tempat = {
        'Pantai Family': ['Pantai Sanur', 'Pantai Nusa Dua', 'Pantai Pandawa'],
        'Pantai Surfing': ['Pantai Uluwatu', 'Pantai Padang Padang', 'Pantai Keramas'],
        'Pantai Snorkeling': ['Pantai Amed', 'Pantai Tulamben', 'Pantai Blue Lagoon']
    }

    uploaded_file = st.file_uploader("Upload foto pantai", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        if uploaded_file.size > 5 * 1024 * 1024:
            st.error("❌ Ukuran gambar terlalu besar! Maksimal 5MB.")
            return
        img = Image.open(uploaded_file).convert("RGB")
        st.image(img, caption="🖼️ Foto yang Diunggah", use_column_width=True)
        img = img.resize((224, 224))
        img_array = image.img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        prediction = model.predict(img_array)[0]
        label = class_names[np.argmax(prediction)]
        st.subheader("📌 Kategori Pantai:")
        st.success(label)
        st.subheader("📍 Rekomendasi Tempat di Bali:")
        for pantai in rekomendasi_tempat[label]:
            st.markdown(f"### {pantai}")
            st.write(penjelasan_pantai.get(pantai, "Tidak ada deskripsi."))
            url = f"https://www.google.com/maps/search/?api=1&query={pantai.replace(' ', '+')}"
            st.markdown(f"""<a href="{url}" target="_blank">
                <button style="background:#444;color:white;padding:6px 12px;border:none;border-radius:5px;">
                📍 Cari {pantai} di Google Maps</button></a>""", unsafe_allow_html=True)
# ======== Halaman Penjelasan ========
def halaman_penjelasan():
    st.title("📚 Kategori Pantai di Bali")
    if "kategori_terpilih" not in st.session_state:
        st.session_state["kategori_terpilih"] = None
    gambar_dict = {
        "Pantai Family": {
            "file": "family.png",
            "caption": "👨‍👩‍👧‍👦 Family",
            "deskripsi": ("Pantai dalam kategori ini sangat cocok untuk liburan keluarga. "
            "Ciri khasnya adalah ombak yang tenang sehingga aman untuk anak-anak "
            "bermain di tepi laut. Selain itu, pantai-pantai ini biasanya dilengkapi "
            "dengan berbagai fasilitas umum seperti taman bermain, toilet umum, tempat makan, "
            "area piknik, hingga penyewaan alat bermain air seperti banana boat atau pelampung. "
            "Suasana yang bersih dan nyaman menjadikan pantai jenis ini favorit bagi keluarga "
            "yang ingin bersantai sambil menikmati panorama laut yang damai."
            )
        },
        "Pantai Surfing": {
            "file": "surfing.png",
            "caption": "🏄 Surfing",
            "deskripsi":( "Pantai-pantai dalam kategori ini memiliki ombak besar dan kuat, "
            "sehingga sangat cocok untuk olahraga surfing. Biasanya memiliki arus laut "
            "yang menantang, dan sering dijadikan lokasi favorit peselancar profesional "
            "maupun pemula. Tersedia juga penyewaan papan selancar serta komunitas surfer "
            "yang aktif di sekitar area pantai."
            )
        },
        "Pantai Snorkeling": {
            "file": "snorkeling.png",
            "caption": "🤿 Snorkeling",
            "deskripsi": ("Pantai snorkeling memiliki air laut yang jernih, dasar laut dangkal, serta "
            "keanekaragaman hayati bawah laut yang indah. Cocok untuk aktivitas menyelam ringan, "
            "melihat terumbu karang dan ikan warna-warni. Biasanya tersedia penyewaan alat snorkeling "
            "dan pemandu lokal untuk menjelajahi spot terbaik." 
            )
        }
    }

    if st.session_state["kategori_terpilih"] is None:
        st.markdown("### Pilih kategori pantai untuk melihat penjelasannya:")
        for kategori, info in gambar_dict.items():
            base64_img = img_to_base64(info["file"])
            with st.form(key=kategori):
                st.markdown(
                    f"""
                    <div style="text-align: center; margin-bottom: 10px;">
                        <img src="data:image/png;base64,{base64_img}"
                             style="border: 4px solid #555; border-radius: 8px;
                             width: 300px; height: 200px; object-fit: cover;" />
                    </div>
                    """, unsafe_allow_html=True)
                if st.form_submit_button(info["caption"]):
                    st.session_state["kategori_terpilih"] = kategori
                    st.experimental_rerun()
    else:
        kategori = st.session_state["kategori_terpilih"]
        info = gambar_dict[kategori]
        st.subheader(info["caption"])
        st.image(info["file"], use_column_width=True)
        st.write(info["deskripsi"])
        if st.button("⬅️ Kembali"):
            st.session_state["kategori_terpilih"] = None
# ======== Routing Utama ========
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "page" not in st.session_state:
    st.session_state["page"] = "login"
if "gapura_open" not in st.session_state:
    st.session_state["gapura_open"] = False

if st.session_state["gapura_open"]:
    st.empty()
    st.markdown("<h2 style='text-align:center;'>✨ Selamat Datang di Bali! ✨</h2>", unsafe_allow_html=True)
    time.sleep(2)
    st.session_state["logged_in"] = True
    st.session_state["username"] = st.session_state["username_temp"]
    st.session_state["page"] = "main"
    st.session_state["gapura_open"] = False
    st.experimental_rerun()

if st.session_state["logged_in"]:
    with st.sidebar:
        st.markdown(f"👤 **{st.session_state['username']}**")
        halaman = st.radio("Navigasi", ["🏠 Beranda", "📷 Klasifikasi"])
        if st.button("🚪 Logout"):
            st.session_state["logged_in"] = False
            st.session_state["username"] = ""
            st.session_state["page"] = "login"
            st.experimental_rerun()
    if halaman == "🏠 Beranda":
        halaman_utama()
    elif halaman == "📷 Klasifikasi":
        halaman_klasifikasi()
else:
    if st.session_state["page"] == "login":
        halaman_login()
    elif st.session_state["page"] == "register":
        halaman_registrasi()
