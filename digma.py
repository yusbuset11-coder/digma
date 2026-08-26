from datetime import datetime
import io
import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials

# Konfigurasi Halaman
st.set_page_config(
    page_title="DIGMA - Digitalisasi Jurnal Mengajar",
    page_icon="📖",
    layout="wide",
)

# ID Master Registry Anda (Sesuai dengan link terbaru Anda)
MASTER_REGISTRY_ID = "1mgN63xzrLt__5b9-gBw8dIWYP3RRgNdagUiTurFZdgg"


def get_gspread_client():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)


@st.cache_resource
def load_master_registry():
    try:
        client = get_gspread_client()
        sh = client.open_by_key(MASTER_REGISTRY_ID)
        worksheet = sh.worksheet("DATABASE_MASTER_REGISTRY")
        return worksheet.get_all_records()
    except Exception as e:
        print(f"❌ ERROR GSPREAD DETAIL: {e}")
        return None


st.title("📖 **DIGMA: Digitalisasi Jurnal Mengajar**")
st.markdown("---")

# Inisialisasi Session State untuk Login Guru
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.guru_nama = ""
    st.session_state.spreadsheet_id = ""

# --- 1. HALAMAN LOGIN / VERIFIKASI GURU ---
if not st.session_state.logged_in:
    st.subheader("🔐 **Verifikasi Akun Guru**")
    st.write(
        "Masukkan **Email** terdaftar atau **Token Unik** Anda untuk mengakses "
        "database jurnal mengajar pribadi."
    )

    with st.form("form_login_digma"):
        input_identifier = st.text_input(
            "**Email / Token Unik**",
            placeholder=(
                "Contoh: yustinussetyanta08@dinas.belajar.id atau TOKEN300869"
            ),
        )
        btn_login = st.form_submit_button("🚀 **Masuk ke Aplikasi DIGMA**")

        if btn_login:
            if input_identifier:
                with st.spinner("Memeriksa data registrasi..."):
                    registry_data = load_master_registry()

                    if registry_data is not None:
                        found = False
                        for row in registry_data:
                            match_email = (
                                str(row.get("Email", "")).strip().lower()
                                == input_identifier.strip().lower()
                            )
                            match_token = (
                                str(row.get("Token_Unik", "")).strip()
                                == input_identifier.strip()
                            )
                            is_active = (
                                str(row.get("Status", "")).strip().upper()
                                == "AKTIF"
                            )

                            if (match_email or match_token) and is_active:
                                st.session_state.logged_in = True
                                st.session_state.guru_nama = row.get(
                                    "Nama_Guru", "Guru"
                                )
                                st.session_state.spreadsheet_id = str(
                                    row.get("Spreadsheet_ID_Guru", "")
                                ).strip()
                                found = True
                                break

                        if found:
                            if (
                                not st.session_state.spreadsheet_id
                                or st.session_state.spreadsheet_id
                                == "(Kosongkan dulu)"
                            ):
                                st.warning(
                                    "⚠️ Akun Anda aktif, namun "
                                    "`Spreadsheet_ID_Guru` di Master Registry "
                                    "masih kosong."
                                )
                                st.session_state.logged_in = False
                            else:
                                st.success(
                                    "Login Berhasil! Selamat datang di modul "
                                    "DIGMA."
                                )
                                st.rerun()
                        else:
                            st.error(
                                "❌ Email/Token tidak ditemukan atau status "
                                "akun tidak AKTIF."
                            )
                    else:
                        st.error(
                            "❌ Gagal terhubung ke Google Spreadsheet Master "
                            "Registry."
                        )
            else:
                st.warning("Mohon masukkan Email atau Token Unik Anda.")

else:
    # --- 2. APLIKASI UTAMA DIGMA SETELAH LOGIN ---
    st.sidebar.success(f"👤 **{st.session_state.guru_nama}**")
    if st.sidebar.button("🚪 **Keluar / Logout**"):
        st.session_state.logged_in = False
        st.session_state.guru_nama = ""
        st.session_state.spreadsheet_id = ""
        st.rerun()


    @st.cache_resource
    def load_guru_database(sheet_id):
        try:
            client = get_gspread_client()
            return client.open_by_key(sheet_id)
        except Exception:
            return None


    sh_guru = load_guru_database(st.session_state.spreadsheet_id)

    if sh_guru is None:
        st.error(
            "Gagal terhubung ke Database Guru Anda. Periksa kembali ID "
            "Spreadsheet di Master Registry."
        )
    else:
        menu = st.sidebar.selectbox(
            "**Pilih Menu DIGMA**",
            [
                "🏠 Beranda",
                "📝 Input Jurnal Harian",
                "📊 Rekapitulasi & Unduh Jurnal",
            ],
        )

        if menu == "🏠 Beranda":
            st.subheader(
                f"Selamat Datang di **DIGMA**, **{st.session_state.guru_nama}**"
            )
            st.write(
                "Modul Digitalisasi Jurnal Mengajar untuk mencatat pelaksanaan "
                "kegiatan pembelajaran harian secara tertib, terstruktur, dan "
                "mudah diakses."
            )

            daftar_sheet = [ws.title for ws in sh_guru.worksheets()]
            st.info(
                f"📑 **Tab Database Anda yang Aktif:** {', '.join(daftar_sheet)}"
            )

        elif menu == "📝 Input Jurnal Harian":
            st.subheader("📝 **Form Pencatatan Jurnal Mengajar Harian**")
            st.write(
                "Catat rincian kegiatan pembelajaran yang Anda laksanakan hari ini."
            )

            try:
                sheet_siswa = sh_guru.worksheet("Data Kelas-Siswa")
                data_siswa = sheet_siswa.get_all_records()
            except Exception:
                data_siswa = []

            if not data_siswa:
                st.warning(
                    "⚠️ Data Kelas-Siswa belum ditemukan di Spreadsheet Anda. "
                    "Pastikan Anda sudah mengisi data siswa melalui aplikasi "
                    "SIPENSIS terlebih dahulu."
                )
                list_sekolah = ["SMK Negeri 2 Bangkalan"]
                list_kelas = ["X TKR-1", "X DKV-1"]
            else:
                df_siswa = pd.DataFrame(data_siswa)
                list_sekolah = (
                    df_siswa["Sekolah"].dropna().unique().tolist()
                    if "Sekolah" in df_siswa.columns
                    else []
                )
                list_kelas = (
                    df_siswa["Kelas"].dropna().unique().tolist()
                    if "Kelas" in df_siswa.columns
                    else []
                )

            with st.form("form_jurnal_harian"):
                col1, col2 = st.columns(2)
                with col1:
                    tanggal_kbm = st.date_input(
                        "**Tanggal Pembelajaran**", datetime.today()
                    )
                    pilih_sekolah = st.selectbox(
                        "**Pilih Sekolah**", list_sekolah
                    )
                with col2:
                    jam_ke = st.text_input(
                        "**Jam Pelajaran Ke-**",
                        placeholder="Contoh: 1 - 2 (07.15 - 08.45)",
                    )
                    pilih_kelas = st.selectbox("**Pilih Kelas**", list_kelas)

                mata_pelajaran = st.text_input(
                    "**Mata Pelajaran**",
                    placeholder="Contoh: Pemrograman Berorientasi Objek",
                )
                materi_pokok = st.text_area(
                    "**Materi / Pokok Bahasan**",
                    placeholder=(
                        "Tuliskan bab atau topik materi yang diajarkan..."
                    ),
                )
                catatan_refleksi = st.text_area(
                    "**Catatan / Refleksi KBM & Hambatan**",
                    placeholder=(
                        "Catat keaktifan siswa, kendala, atau tindak lanjut..."
                    ),
                )
                status_kbm = st.selectbox(
                    "**Status Pelaksanaan KBM**",
                    [
                        "Terlaksana dengan Baik",
                        "Tugas Mandiri / Penugasan",
                        "Jam Kosong / Dispensasi",
                        "Diganti Jadwal Lain",
                    ],
                )

                btn_simpan_jurnal = st.form_submit_button(
                    "💾 **Simpan Jurnal Mengajar**"
                )

                if btn_simpan_jurnal:
                    if not jam_ke or not mata_pelajaran or not materi_pokok:
                        st.error(
                            "⚠️ Mohon lengkapi Jam Pelajaran, Mata Pelajaran, dan Materi Pokok!"
                        )
                    else:
                        with st.spinner("Menyimpan jurnal ke Google Sheets..."):
                            try:
                                sheet_jurnal = sh_guru.worksheet(
                                    "Jurnal Mengajar"
                                )
                            except Exception:
                                sheet_jurnal = sh_guru.add_worksheet(
                                    title="Jurnal Mengajar",
                                    rows="1000",
                                    cols="8",
                                )

                            existing_data = sheet_jurnal.get_all_values()
                            if not existing_data:
                                sheet_jurnal.append_row(
                                    [
                                        "Tanggal",
                                        "Sekolah",
                                        "Kelas",
                                        "Jam_Ke",
                                        "Mapel",
                                        "Materi_Pokok",
                                        "Catatan_Refleksi",
                                        "Status_KBM",
                                    ]
                                )

                            sheet_jurnal.append_row(
                                [
                                    str(tanggal_kbm),
                                    str(pilih_sekolah),
                                    str(pilih_kelas),
                                    str(jam_ke),
                                    str(mata_pelajaran),
                                    str(materi_pokok),
                                    str(catatan_refleksi),
                                    str(status_kbm),
                                ]
                            )

                            st.balloons()
                            st.success(
                                "🎉 Jurnal mengajar berhasil disimpan ke database Anda!"
                            )

        elif menu == "📊 Rekapitulasi & Unduh Jurnal":
            st.subheader("📊 **Rekapitulasi & Unduh Jurnal Mengajar**")
            st.write(
                "Filter dan tinjau riwayat jurnal mengajar berdasarkan "
                "**Sekolah**, **Kelas**, dan **Mata Pelajaran** sebelum "
                "mengunduhnya."
            )

            try:
                sheet_jurnal = sh_guru.worksheet("Jurnal Mengajar")
                data_jurnal = sheet_jurnal.get_all_records()

                if not data_jurnal:
                    st.info(
                        "Belum ada data jurnal mengajar yang tersimpan di tab"
                        " 'Jurnal Mengajar'."
                    )
                else:
                    df_jurnal = pd.DataFrame(data_jurnal)

                    with st.container(border=True):
                        st.markdown(
                            "#### **🔍 Filter Berdasarkan Sekolah, Kelas, &"
                            " Mapel**"
                        )
                        col_f1, col_f2, col_f3 = st.columns(3)

                        schools = (
                            df_jurnal["Sekolah"].dropna().unique().tolist()
                            if "Sekolah" in df_jurnal.columns
                            else []
                        )
                        sel_sch = col_f1.selectbox(
                            "**Pilih Sekolah**", ["Semua Sekolah"] + schools
                        )

                        classes = (
                            df_jurnal["Kelas"].dropna().unique().tolist()
                            if "Kelas" in df_jurnal.columns
                            else []
                        )
                        sel_cls = col_f2.selectbox(
                            "**Pilih Kelas**", ["Semua Kelas"] + classes
                        )

                        mapels = (
                            df_jurnal["Mapel"].dropna().unique().tolist()
                            if "Mapel" in df_jurnal.columns
                            else []
                        )
                        sel_mpl = col_f3.selectbox(
                            "**Pilih Mata Pelajaran**", ["Semua Mapel"] + mapels
                        )

                    df_filtered = df_jurnal.copy()
                    if (
                        sel_sch != "Semua Sekolah"
                        and "Sekolah" in df_filtered.columns
                    ):
                        df_filtered = df_filtered[
                            df_filtered["Sekolah"] == sel_sch
                        ]
                    if sel_cls != "Semua Kelas" and "Kelas" in df_filtered.columns:
                        df_filtered = df_filtered[
                            df_filtered["Kelas"] == sel_cls
                        ]
                    if sel_mpl != "Semua Mapel" and "Mapel" in df_filtered.columns:
                        df_filtered = df_filtered[
                            df_filtered["Mapel"] == sel_mpl
                        ]

                    st.markdown("---")
                    with st.container(border=True):
                        st.dataframe(df_filtered, use_container_width=True)

                    if not df_filtered.empty:
                        output_jurnal = io.BytesIO()
                        with pd.ExcelWriter(
                            output_jurnal, engine="openpyxl"
                        ) as writer:
                            df_filtered.to_excel(
                                writer, index=False, sheet_name="Jurnal_Mengajar"
                            )
                        excel_jurnal_data = output_jurnal.getvalue()

                        st.download_button(
                            label=(
                                "📥 **Download Laporan Jurnal (Excel Sesuai"
                                " Filter)**"
                            ),
                            data=excel_jurnal_data,
                            file_name="Rekap_Jurnal_Mengajar_Terfilter.xlsx",
                            mime=(
                                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            ),
                        )
                    else:
                        st.warning(
                            "Tidak ada data yang sesuai dengan filter yang"
                            " dipilih."
                        )

            except Exception:
                st.info(
                    "Tab 'Jurnal Mengajar' belum tersedia di spreadsheet Anda."
                    " Silakan isi form input jurnal harian terlebih dahulu"
                    " untuk otomatis membuat tab tersebut."
                )