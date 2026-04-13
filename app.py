import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
from datetime import date
import re
import os
import time

if "last_request_time" not in st.session_state:
    st.session_state.last_request_time = 0

if "is_generating" not in st.session_state:
    st.session_state.is_generating = False

# --- KONFIGURASI HALAMAN & SECURITY ---
st.set_page_config(page_title="APLIKASI RPP KBC - KKG Kecamatan Panjalu", layout="wide", page_icon="🏫")

# --- CSS TAMPILAN ---
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
    [data-testid="stStatusWidget"] { visibility: hidden !important; }
    </style>
""", unsafe_allow_html=True)

# --- MODEL AI ---
@st.cache_resource
def get_model():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return None

    try:
        genai.configure(api_key=api_key)

        for m in genai.list_models():
            if "generateContent" in m.supported_generation_methods:
                return genai.GenerativeModel(m.name)

        return None
    except:
        return None

model_ai = get_model()

# --- DATABASE ---
if "db_rpp" not in st.session_state:
    st.session_state.db_rpp = []

if "config" not in st.session_state:
    st.session_state.config = {
        "madrasah": "",
        "guru": "",
        "nip_guru": "",
        "kepala": "nama_kepala",
        "nip_kepala": "nip_kepala",
        "thn_ajar": ""
    }

# --- SIDEBAR ---
with st.sidebar:
    try:
        st.image("logo kemenag.png", width=80)
    except:
        st.warning("⚠️ Logo tidak ditemukan!")

    st.markdown("""
    <div style='text-align:center; border-bottom:1px solid #ffffff33; margin-bottom:20px; padding-bottom:10px;'>
        <h2 style='color:white;'>GENERAT RPP KBC</h2>
        <p style='font-size:0.85em;color:#c8e6c9;'>
        KKG KECAMATAN PANJALU
        </p>
    </div>
    """, unsafe_allow_html=True)

    menu = st.radio("Menu Utama", ["➕ Buat RPP Baru", "📜 Riwayat RPP", "⚙️ Pengaturan"])
    st.divider()
    st.caption("Copyright: Agus Arifien-@2026")

# =========================
# PENGATURAN
# =========================
if menu == "⚙️ Pengaturan":
    st.subheader("⚙️ Data Master Madrasah")

    st.session_state.config["madrasah"] = st.text_input("Nama Madrasah", value=st.session_state.config["madrasah"])
    st.session_state.config["thn_ajar"] = st.text_input("Tahun Pelajaran", value=st.session_state.config["thn_ajar"])

    c1, c2 = st.columns(2)
    with c1:
        st.session_state.config["guru"] = st.text_input("Nama Guru", value=st.session_state.config["guru"])
        st.session_state.config["nip_guru"] = st.text_input("NIP Guru", value=st.session_state.config["nip_guru"])
    with c2:
        st.session_state.config["kepala"] = st.text_input("Nama Kepala", value=st.session_state.config["kepala"])
        st.session_state.config["nip_kepala"] = st.text_input("NIP Kepala", value=st.session_state.config["nip_kepala"])

    if st.button("Simpan Konfigurasi"):
        st.success("Data berhasil disimpan!")

# =========================
# BUAT RPP
# =========================
if menu == "➕ Buat RPP Baru":
    st.subheader("➕ Rancang RPP KBC Presisi")

    with st.form("form_rpp_presisi"):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            mapel = st.text_input("Mata Pelajaran")
        with c2:
            kls_sel = st.selectbox("Kelas", ["1","2","3","4","5","6"], index=3)
        with c3:
            sem_sel = st.selectbox("Semester", ["1 (Ganjil)", "2 (Genap)"])
        with c4:
            materi = st.text_input("Materi Pokok")

        st.markdown("<div class='section-header'>WAKTU</div>", unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            inp_jp = st.number_input("Total JP", min_value=1, value=4)
        with c2:
            inp_mnt = st.number_input("Menit/JP", min_value=1, value=35)
        with c3:
            inp_pt = st.number_input("Pertemuan", min_value=1, value=2)
        with c4:
            tgl_rpp = st.date_input("Tanggal", date.today())

        target_belajar = st.text_area("Tujuan Pembelajaran")
        instruksi_khusus = st.text_input("Instruksi AI")

        model_p = st.selectbox("Model Pembelajaran", [
            "PBL","PjBL","LOK-R","Inquiry","Cooperative","Discovery","CTL"
        ])

        list_p = ["Keimanan","Kewargaan","Kritis","Kreativitas","Kolaborasi","Mandiri","Kesehatan","Komunikasi"]
        cols = st.columns(4)
        profil_sel = [p for i,p in enumerate(list_p) if cols[i%4].checkbox(p,key=p)]

        list_kbc = ["Cinta Allah","Cinta Ilmu","Cinta Sesama","Cinta Lingkungan","Cinta Tanah Air"]
        cols2 = st.columns(2)
        topik_sel = [k for i,k in enumerate(list_kbc) if cols2[i%2].checkbox(k,key=k)]

        submitted = st.form_submit_button("GENERATE RPP")

    # =========================
    # PROCESS
    # =========================
    if submitted:

        if st.session_state.is_generating:
            st.warning("Masih proses...")
            st.stop()

        st.session_state.is_generating = True

        if not materi or not target_belajar:
            st.warning("Lengkapi data!")
            st.session_state.is_generating = False
            st.stop()

        try:
            with st.spinner("Menyusun RPP..."):

                jp_per_pt = inp_jp // inp_pt
                sisa = inp_jp % inp_pt

                prompt = f"""
                Buat RPP KBC:
                Mapel {mapel}
                Materi {materi}
                Kelas {kls_sel}
                TP {target_belajar}
                Profil {', '.join(profil_sel)}
                KBC {', '.join(topik_sel)}
                """

                model_ai = get_model()

                if model_ai is None:
                    st.error("API KEY tidak valid")
                    st.session_state.is_generating = False
                else:
                    try:
                        raw_response = model_ai.generate_content(prompt).text
                        html_final = re.sub(r'```html|```', '', raw_response).strip()

                        st.session_state.db_rpp.append({
                            "tgl": tgl_rpp,
                            "materi": materi,
                            "file": html_final
                        })

                        st.success("Selesai!")

                        components.html(
                            f"<div style='background:white;padding:20px;color:black'>{html_final}</div>",
                            height=800,
                            scrolling=True
                        )

                        st.download_button(
                            "Download",
                            html_final,
                            file_name=f"RPP_{materi}.doc"
                        )

                    finally:
                        st.session_state.is_generating = False

        except Exception as e:
            st.session_state.is_generating = False
            st.error(f"Error: {e}")

# =========================
# RIWAYAT
# =========================
if menu == "📜 Riwayat RPP":
    st.subheader("Riwayat Dokumen")

    if not st.session_state.db_rpp:
        st.info("Belum ada data")

    for i, item in enumerate(reversed(st.session_state.db_rpp)):
        with st.expander(f"{item['tgl']} - {item['materi']}"):
            components.html(
                f"<div style='background:white;padding:20px;color:black'>{item['file']}</div>",
                height=500
            )
            st.download_button(
                "Unduh Ulang",
                item["file"],
                file_name="RPP_Re.doc",
                key=f"re_{i}"
            )
