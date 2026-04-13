import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
from datetime import date
import re

# --- KONFIGURASI HALAMAN & SECURITY ---
st.set_page_config(page_title="E-Perangkat KBC Presisi - MIN 1 CIAMIS", layout="wide", page_icon="🏫")

# --- CSS TAMPILAN (Sudah Diperbaiki & Struktur Tetap Aman) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stSidebar"] { background-color: #14532d; }
    [data-testid="stSidebar"] * { color: white !important; }
    input { color: #000000 !important; }
    .stTextArea textarea { color: #000000 !important; background-color: #ffffff !important; }
    .section-header { color: #166534; font-weight: bold; border-left: 5px solid #166534; padding-left: 10px; margin-top: 20px; }
    .sidebar-brand { text-align: center; padding: 10px; border-bottom: 1px solid #ffffff33; margin-bottom: 20px; }
    /* Kode penyembunyi ikon status pojok kiri bawah */
    [data-testid="stStatusWidget"] { visibility: hidden !important; }
    </style>
    """, unsafe_allow_html=True)

# --- ENGINE AI (LOGIKA MODEL OTOMATIS) ---
@st.cache_resource
def get_model():
    if "GOOGLE_API_KEY" not in st.secrets: return None
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return genai.GenerativeModel(m.name)
        return None
    except: return None

model_ai = get_model()


# --- DATABASE SEMENTARA ---
if 'db_rpp' not in st.session_state: st.session_state.db_rpp = []
if 'config' not in st.session_state:
    # FITUR 4: Tampilan disamarkan (placeholder) dengan nilai awal kosong
    st.session_state.config = {
        "madrasah": "", "guru": "", "nip_guru": "",
        "kepala": "Iim Siti Halimah, S.Ag., M.Pd.",
        "nip_kepala": "197206051997032003", "thn_ajar": ""
    }

# --- SIDEBAR MENU ---
with st.sidebar:
    try:
        st.image("logo kemenag.png", width=80) 
    except:
        st.warning("⚠️ File logo tidak ditemukan!")

    st.markdown("""
    <div style='text-align: center; border-bottom: 1px solid #ffffff33; margin-bottom: 20px; padding-bottom: 10px;'>
        <h2 style='color: white; margin-top:0px; font-size: 1.5em;'>E-Perangkat KBC Presisi</h2>
        <p style='font-size:0.85em; font-style:italic; color:#c8e6c9;'>
        "MIN 1 CIAMIS - Unggul, Maju, Mendunia."
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    menu = st.radio("Menu Utama", ["➕ Buat RPP Baru", "📜 Riwayat RPP", "⚙️ Pengaturan"])
    st.divider()
    st.caption("v13.22 - Full Version Enhanced")

# --- MENU 1: PENGATURAN (FITUR 4: PLACEHOLDER SAMAR) ---
if menu == "⚙️ Pengaturan":
    st.subheader("⚙️ Data Master Madrasah")
    st.info("Isi data ini sekali saja. Nanti otomatis masuk ke setiap RPP.")
    
    st.session_state.config['madrasah'] = st.text_input("Nama Madrasah", value=st.session_state.config['madrasah'], placeholder="Contoh: MIN 1 CIAMIS")
    st.session_state.config['thn_ajar'] = st.text_input("Tahun Pelajaran", value=st.session_state.config['thn_ajar'], placeholder="Contoh: 2025/2026")
    
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.config['guru'] = st.text_input("Nama Guru", value=st.session_state.config['guru'], placeholder="Nama Lengkap & Gelar")
        st.session_state.config['nip_guru'] = st.text_input("NIP Guru", value=st.session_state.config['nip_guru'], placeholder="NIP atau '-'")
    with c2:
        st.session_state.config['kepala'] = st.text_input("Nama Kepala", value=st.session_state.config['kepala'], placeholder="Nama Kepala Madrasah")
        st.session_state.config['nip_kepala'] = st.text_input("NIP Kepala", value=st.session_state.config['nip_kepala'], placeholder="NIP Kepala")
    
    if st.button("Simpan Konfigurasi"):
        st.success("Data berhasil disimpan!")

# --- MENU 2: BUAT RPP BARU ---
elif menu == "➕ Buat RPP Baru":
    st.subheader("➕ Rancang RPP KBC Presisi")
    
    with st.form("form_rpp_presisi"):  
        c_mapel, c_kls, c_sem, c_materi = st.columns(4)
        with c_mapel: mapel = st.text_input("Mata Pelajaran")
        with c_kls: kls_sel = st.selectbox("Kelas", ["1", "2", "3", "4", "5", "6"], index=3) 
        with c_sem: sem_sel = st.selectbox("Semester", ["1 (Ganjil)", "2 (Genap)"])
        with c_materi: materi = st.text_input("Materi Pokok")
        
        # FITUR 1: LOGIKA ALOKASI WAKTU TIGA KOLOM
        st.markdown("<div class='section-header'>WAKTU & PERTEMUAN</div>", unsafe_allow_html=True)
        ca1, ca2, ca3, ca4 = st.columns(4)
        with ca1: inp_jp = st.number_input("Total JP", min_value=1, value=4)
        with ca2: inp_mnt = st.number_input("Menit/JP", min_value=1, value=35)
        with ca3: inp_pt = st.number_input("Jml Pertemuan", min_value=1, value=2)
        with ca4: tgl_rpp = st.date_input("Tanggal RPP", date.today())
        
        alokasi_final = f"{inp_jp} x {inp_mnt} Menit ({inp_pt} Pertemuan)"
        
        st.markdown("<div class='section-header'>KOMPONEN KBC & DEEP LEARNING</div>", unsafe_allow_html=True)
        target_belajar = st.text_area("Tujuan Pembelajaran (TP)", height=100, placeholder="Contoh: Melalui observasi, murid dapat...")
        instruksi_khusus = st.text_input("💡 Instruksi Khusus AI (Opsional)", 
                                    placeholder="Contoh: Tambahkan ice breaking seru atau buat kegiatan luar kelas")
        # FITUR 2: PERUBAHAN MENJADI CHECKBOX
        model_p = st.selectbox("Model Pembelajaran", [
            "Problem Based Learning (PBL)", 
            "Project Based Learning (PjBL)", 
            "Literasi, Orientasi, Kolaborasi, Refleksi (LOK-R)",
            "Inquiry Learning", "Cooperative Learning", "Discovery Learning", "CTL"
        ])
    
        st.write("<b>Pilih Dimensi Profil Lulusan:</b>", unsafe_allow_html=True)
        list_p = ["Keimanan & Ketakwaan", "Kewargaan", "Penalaran Kritis", "Kreativitas", "Kolaborasi", "Kemandirian", "Kesehatan", "Komunikasi"]
        cols_p = st.columns(4)
        profil_sel = [p for i, p in enumerate(list_p) if cols_p[i % 4].checkbox(p, key=f"p_{p}")]
    
        st.write("<b>Pilih Topik KBC (Panca Cinta):</b>", unsafe_allow_html=True)
        list_kbc = ["Cinta kepada Allah/Rasul-Nya", "Cinta Ilmu", "Cinta Diri dan Sesama", "Cinta Lingkungan", "Cinta Tanah Air"]
        cols_k = st.columns(2)
        topik_sel = [k for i, k in enumerate(list_kbc) if cols_k[i % 2].checkbox(k, key=f"k_{k}")]
    
        submitted = st.form_submit_button("🚀 GENERATE RPP SESUAI REFERENSI")
    if submitted:
        if not materi or not target_belajar:
            st.warning("Mohon lengkapi Materi dan Tujuan Pembelajaran.")
        else:
            with st.spinner("⏳ Menyusun RPP KBC Presisi..."):
                try:
                    # Logika Pembagian JP Otomatis
                    jp_per_pt = inp_jp // inp_pt
                    sisa_jp = inp_jp % inp_pt
                    
                    # FITUR 3: INTEGRASI TP DENGAN RUH KBC (MASUK KE PROMPT ASLI)
                    prompt = f"""
                    Berperanlah sebagai Guru MI (Madrasah Ibtidaiyah) Profesional. 
                    WAJIB: Buat RPP untuk MATA PELAJARAN: {mapel} Materi: {materi}
                    UNTUK KELAS {kls_sel} SEMESTER {sem_sel}.
                    DILARANG KERAS memberikan Fase D atau Kelas VII.

                    DATA INPUT (GUNAKAN DATA INI SECARA EKSPLISIT):
                    - Madrasah: {st.session_state.config['madrasah']}
                    - Guru: {st.session_state.config['guru']} (NIP: {st.session_state.config['nip_guru']})
                    - Kepala: {st.session_state.config['kepala']} (NIP: {st.session_state.config['nip_kepala']})
                    - Kelas: {kls_sel}
                    - Semester: {sem_sel}
                    - Tahun: {st.session_state.config['thn_ajar']}
                    - Model: {model_p}
                    - Profil Lulusan: {', '.join(profil_sel)}
                    - Nilai Panca Cinta: {', '.join(topik_sel)}
                    - Tujuan Pembelajaran: {target_belajar}

                    STRUKTUR HTML (WAJIB IKUTI URUTAN INI):
                    Gunakan tag table border='1' style='border-collapse:collapse; width:100%; font-family:Times New Roman;'

                    1. HEADER: Judul PERENCANAAN PEMBELAJARAN KBC, Materi, Nama Madrasah.
                    
                    2. A. IDENTITAS MODUL:
                       Isi: Madrasah, Guru, Mapel, Kelas, Materi, Alokasi ({alokasi_final}), Tahun, Model ({model_p}).

                    3. B. IDENTIFIKASI & KBC:
                       - 1. Kesiapan Murid
                       - 2. Dimensi Profil Lulusan ({', '.join(profil_sel)})
                       - 3. Topik KBC ({', '.join(topik_sel)})
                       - 4. Materi Insersi KBC

                    4. C. DESAIN PEMBELAJARAN:
                       - 1. CP
                       - 2. Lintas Disiplin Ilmu
                       - 3. Tujuan Pembelajaran: Integrasikan narasi "{target_belajar}" dengan nilai "{', '.join(topik_sel)}" sehingga memuat ruh KBC secara harmonis.
                       - 4. Praktik Pedagogis
                       - 5. Kemitraan Pembelajaran
                       - 6. Lingkungan Pembelajaran
                       - 7. Pemanfaatan Digital

                    5. D. PENGALAMAN BELAJAR (Deep Learning):
                       Bagi menjadi {inp_pt} pertemuan. 
                       P1 = {jp_per_pt + (1 if sisa_jp > 0 else 0)} JP, sisanya {jp_per_pt} JP.
                       Setiap pertemuan strukturnya: PENDAHULUAN, INTI (Memahami, Mengaplikasi, Merefleksi), PENUTUP.
                       
                       *WAJIB*: Di setiap pertemuan, sisipkan kotak ini:
                       <div style='background-color:#f0fdf4; border-left:5px solid #166534; padding:15px; margin:10px 0;'>
                         <b>Penguatan Nilai KBC (Panca Cinta):</b> [Narasi penguatan {', '.join(topik_sel)}]
                       </div>

                    6. E. ASESMEN (Awal, Proses, Akhir)

                    7. PENGESAHAN: Tabel tanda tangan di Ciamis, {tgl_rpp.strftime('%d %B %Y')}.

                    8. LAMPIRAN: Rubrik Penilaian (holistik dan analitik), LKPD (Lengkap sesuai mata pelajaran, materi pokok), Instrumen Asesmen (5 Soal PG lengkap dengan Kisi-kisi & Kunci Jawaban, berikan narasi ruh KBC pada naskah soal).

                    HANYA BERIKAN KODE HTML.
                    """
                    raw_response = model_ai.generate_content(prompt).text
                    html_final = re.sub(r'```html|```', '', raw_response).strip()
                    st.session_state.db_rpp.append({"tgl": tgl_rpp, "materi": materi, "file": html_final})
                    st.success("Selesai!")
                    components.html(f"<div style='background:white; color:black; padding:30px; border:1px solid #ccc;'>{html_final}</div>", height=800, scrolling=True)
                    st.download_button("📥 Download Document", html_final, file_name=f"RPP_{materi}.doc")
                except Exception as e:
                    st.error(f"Eror: {e}")

# --- MENU 3: RIWAYAT ---
elif menu == "📜 Riwayat RPP":
    st.subheader("📜 Riwayat Dokumen")
    if not st.session_state.db_rpp: st.info("Belum ada dokumen yang dibuat.")
    for i, item in enumerate(reversed(st.session_state.db_rpp)):
        with st.expander(f"📄 {item['tgl']} - {item['materi']}"):
            components.html(f"<div style='background:white; color:black; padding:20px; font-family:serif;'>{item['file']}</div>", height=500, scrolling=True)
            st.download_button("Unduh Ulang", item['file'], file_name="RPP_Re.doc", key=f"re_{i}")


