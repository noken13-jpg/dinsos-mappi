const SOP_DATA = [
  {
    id: 'bpjs-pbi-jk', field: 'BIDANG PERLINDUNGAN DAN JAMINAN SOSIAL (LINJAMSOS)', category: 'Perlindungan dan Jaminan Sosial',
    title: 'SOP Pelayanan Rekomendasi BPJS / Re-Aktifasi PBI-JK',
    requirements: ['KTP', 'KK', 'Kartu BPJS non-aktif', 'Surat Keterangan Berobat / Surat Rawat Inap dari Rumah Sakit atau Fasilitas Kesehatan asli yang menyatakan pasien sedang dirawat atau membutuhkan penanganan medis segera'],
    time: '20 menit / 1 jam 30 menit', fee: 'Gratis', details: 'Layanan rekomendasi dan re-aktifasi PBI-JK sesuai kelengkapan berkas yang disampaikan.', procedureNote: 'Sesuai Permensos No. 3 Tahun 2026, reaktivasi di SIKS-NG diprioritaskan bagi pasien penyakit kronis/darurat medis dan diproses maksimal 6 bulan sejak tanggal penonaktifan.',
    contact: 'WhatsApp Pengaduan: 0821-3152-1299'
  },
  {
    id: 'peti-jenazah', field: 'BIDANG PERLINDUNGAN DAN JAMINAN SOSIAL (LINJAMSOS)', category: 'Perlindungan dan Jaminan Sosial',
    title: 'SOP Pelayanan Bantuan Peti Jenazah',
    requirements: ['Permohonan keluarga duka', 'KTP', 'Surat Kematian dari Puskesmas/RS/Kampung', 'Foto jenazah/salib'],
    time: '4 jam 30 menit', fee: 'Gratis', details: 'Pelayanan bantuan peti jenazah berdasarkan permohonan dan dokumen pendukung yang tersedia.',
    contact: 'WhatsApp Pengaduan: 0821-3152-1299'
  },
  {
    id: 'bahan-natura-bama', field: 'BIDANG PERLINDUNGAN DAN JAMINAN SOSIAL (LINJAMSOS)', category: 'Perlindungan dan Jaminan Sosial',
    title: 'SOP Pelayanan Bantuan Bahan Natura / Bama',
    requirements: ['Permohonan keluarga duka', 'KTP', 'Surat Kematian dari Puskesmas/RS/Kampung', 'Foto jenazah/salib', 'Berita Acara Serah Terima', 'Pakta Integritas'],
    time: '4 jam 30 menit', fee: 'Gratis', details: 'Pelayanan bantuan bahan natura/bama dengan dokumen pendukung sesuai berkas yang ditetapkan.',
    contact: 'WhatsApp Pengaduan: 0821-3152-1299'
  },
 ];

if (typeof window !== 'undefined') window.SOP_DATA = SOP_DATA;
