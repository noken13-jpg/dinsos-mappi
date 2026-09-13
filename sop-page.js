(() => {
  const data = window.SOP_DATA || [];
  const results = document.getElementById('sop-results');
  const filters = document.getElementById('sop-filters');
  const search = document.getElementById('sop-search');
  if (!results || !filters) return;
  const fields = ['Semua bidang', ...new Set(data.map(item => item.field))];
  let active = fields[0];
  const esc = value => String(value).replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  filters.innerHTML = fields.map((field, i) => `<button class="sop-filter ${i === 0 ? 'is-active' : ''}" type="button" role="tab" aria-selected="${i === 0}" data-field="${esc(field)}">${esc(field)}</button>`).join('');
  const render = () => {
    const query = (search.value || '').trim().toLowerCase();
    const visible = data.filter(item => (active === fields[0] || item.field === active) && (!query || `${item.title} ${item.field} ${item.category}`.toLowerCase().includes(query)));
    const groups = [...new Set(visible.map(item => item.field))];
    results.innerHTML = visible.length ? groups.map(field => `<section class="sop-group"><div class="section-heading"><p class="eyebrow">${esc(field)}</p><h2>${esc(field.includes('LINJAMSOS') ? 'Perlindungan dan Jaminan Sosial' : 'Manajemen, Perencanaan & Keuangan Internal')}</h2></div><div class="sop-grid">${visible.filter(item => item.field === field).map(item => `<article class="glass-card sop-card"><div class="sop-card-top"><span class="sop-icon" aria-hidden="true">▦</span><span class="tag">${esc(item.category)}</span></div><h3>${esc(item.title)}</h3><p>${esc(item.details)}</p><div class="sop-meta"><div><small>Waktu pelayanan</small><strong>${esc(item.time)}</strong></div><div><small>Biaya/tarif</small><strong>${esc(item.fee)}</strong></div></div><details><summary>Persyaratan dan informasi layanan</summary>${item.requirements.length ? `<ul class="check-list">${item.requirements.map(req => `<li>${esc(req)}</li>`).join('')}</ul>` : '<p class="muted">Persyaratan belum tersedia dalam bahan sumber.</p>'}<p class="contact-line">${esc(item.contact)}</p>${item.procedureNote ? `<p class="procedure-note"><strong>Catatan alur prosedur:</strong> ${esc(item.procedureNote)}</p>` : ''}</details></article>`).join('')}</div></section>`).join('') : '<div class="glass-card empty-state"><h2>SOP tidak ditemukan</h2><p>Ubah kata kunci atau pilih bidang lain.</p></div>';
  };
  filters.addEventListener('click', event => { const button = event.target.closest('button[data-field]'); if (!button) return; active = button.dataset.field; filters.querySelectorAll('button').forEach(item => { const on = item === button; item.classList.toggle('is-active', on); item.setAttribute('aria-selected', String(on)); }); render(); });
  search.addEventListener('input', render);
  render();
})();
