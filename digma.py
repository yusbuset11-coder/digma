"""
Modul: DIGMA (Digitalisasi Jurnal Mengajar)
Pengembang: Yustinus Budi Setyanta - Pengawas Sekolah Cabdin Bangkalan
"""

import streamlit as st
import pandas as pd
from datetime import date

def render_digma_module():
    st.markdown("### 📚 DIGMA: Digitalisasi Jurnal Mengajar")
    st.write("Catat dan pantau pelaksanaan jurnal kegiatan mengajar guru secara digital.")

    # Pembagian Tab untuk Navigasi DIGMA
    tab1, tab2, tab3 = st.tabs([
        "✍️ Isi Jurnal Mengajar", 
        "📖 Lihat Riwayat Jurnal", 
        "📊 Rekap & Ekspor Laporan"
    ])

    with tab1:
        st.markdown("#### Form Input Jurnal Mengajar Harian")
        col1, col2 = st.columns(2)
        with col1:
            tanggal_jurnal = st.date_input("📅 Tanggal Mengajar", value=date.today(), key="tgl_jurnal")
            kelas_jurnal = st.selectbox("📚 Pilih Kelas:", ["Kelas X", "Kelas XI", "Kelas XII"], key="kelas_jurnal")
            jam_ke = st.text_input("⏰ Jam Pelajaran Ke-", "1 - 3")
        with col2:
            nama_guru = st.text_input("👨‍🏫 Nama Guru", value=st.session_state.get("user_nama", ""), key="guru_jurnal")
            mata_pelajaran = st.text_input("📖 Mata Pelajaran", value="Pendidikan Pancasila", key="mapel_jurnal")

        materi_pokok = st.text_area("📝 Materi / Kompetensi Dasar yang Diajarkan", "Contoh: Nilai-nilai Pancasila dalam Kehidupan Berbangsa")
        catatan_kejadian = st.text_area("📌 Catatan / Kejadian Penting di Kelas (Opsional)", "Kondisi kelas kondusif, seluruh siswa hadir dan aktif.")

        if st.button("💾 Simpan Jurnal Mengajar", type="primary"):
            st.success("✅ Jurnal mengajar berhasil disimpan ke database!")

    with tab2:
        st.markdown("#### Riwayat Jurnal Mengajar")
        st.info("Daftar jurnal mengajar yang telah dimasukkan oleh guru.")
        
        # Data dummy riwayat jurnal
        df_dummy_jurnal = pd.DataFrame({
            "Tanggal": ["2026-08-16", "2026-08-15"],
            "Kelas": ["Kelas X", "Kelas XI"],
            "Mata Pelajaran": ["Pendidikan Pancasila", "Sejarah"],
            "Materi": ["Pancasila Dasar Negara", "Pergerakan Nasional"]
        })
        st.dataframe(df_dummy_jurnal, use_container_width=True)

    with tab3:
        st.markdown("#### Rekap & Ekspor Laporan Jurnal")
        st.write("Unduh rekapitulasi jurnal mengajar dalam format Excel atau laporan cetak.")
        if st.button("📥 Download Rekap Jurnal (Excel)"):
            st.info("Fitur unduh laporan sedang diproses...")