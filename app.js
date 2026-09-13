const $ = (s, root=document) => root.querySelector(s);
const $$ = (s, root=document) => [...root.querySelectorAll(s)];
const mobileToggle = $('.mobile-toggle');
const mobileMenu = $('.mobile-menu');
mobileToggle?.addEventListener('click', () => { const open = mobileMenu.classList.toggle('open'); mobileToggle.setAttribute('aria-expanded', String(open)); });
$$('.mobile-menu a').forEach(a => a.addEventListener('click', () => mobileMenu?.classList.remove('open')));
const sections = $$('main section[id]');
const links = $$('.nav-links a');
const observer = new IntersectionObserver(entries => entries.forEach(entry => { if(entry.isIntersecting){ links.forEach(l => l.classList.toggle('active', l.getAttribute('href') === `#${entry.target.id}`)); }}), {rootMargin:'-35% 0px -55%'});
sections.forEach(s => observer.observe(s));
const reveal = new IntersectionObserver(entries => entries.forEach(e => {if(e.isIntersecting){e.target.style.opacity='1';e.target.style.transform='none';reveal.unobserve(e.target)}}),{threshold:.08});
$$('.reveal').forEach(e=>{e.style.opacity='0';e.style.transform='translateY(18px)';e.style.transition='opacity .7s ease,transform .7s ease';reveal.observe(e)});
const grid = $('.employee-grid');
let employees=[];
function initials(name){return name.split(/\s+/).slice(0,2).map(x=>x[0]).join('').toUpperCase()}
function renderEmployees(){
 const q=($('#employee-search')?.value||'').toLowerCase().trim();
 const result=employees.filter(e=>`${e.nama} ${e.nip} ${e.jabatan}`.toLowerCase().includes(q));
 if(grid) grid.innerHTML=result.map(e=>`<article class="employee-card reveal"><div class="avatar">${initials(e.nama)}</div><h3>${e.nama}</h3><p class="nip">NIP ${e.nip}</p><p class="role">${e.jabatan}</p></article>`).join('') || '<p class="notice">Data pegawai tidak ditemukan.</p>';
 const count=$('#employee-count'); if(count) count.textContent=`Menampilkan ${result.length} dari ${employees.length} pegawai`;
}
fetch('pegawai.json').then(r=>{if(!r.ok)throw Error('pegawai.json gagal dimuat');return r.json()}).then(data=>{employees=data;renderEmployees();const total=$('#total-employees');if(total)total.textContent=data.length}).catch(()=>{if(grid)grid.innerHTML='<p class="notice">Data pegawai belum dapat dimuat.</p>'});
$('#employee-search')?.addEventListener('input',renderEmployees);
$('#back-top')?.addEventListener('click',()=>scrollTo({top:0,behavior:'smooth'}));
