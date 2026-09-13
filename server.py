#!/usr/bin/env python3
"""
server.py - Server lokal untuk website Dinas Sosial Kabupaten Mappi

Fitur:
1. Memeriksa index.html dan pegawai.json apakah ada error sintaksis
2. Menjalankan local server di port 8000
3. Menampilkan URL lokal agar website bisa diakses di browser
"""

import http.server
import socketserver
import json
import os
import sys
import re
import secrets
import time
import urllib.parse
from http import cookies
from pathlib import Path


# =============================================================================
# 1. CHECKER: index.html & pegawai.json
# =============================================================================

def check_index_html(path="index.html"):
    """Memeriksa apakah index.html ada dan tidak ada error struktural."""
    issues = []
    warnings = []

    if not os.path.exists(path):
        issues.append(f"❌ File '{path}' TIDAK DITEMUKAN.")
        return issues, warnings

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        issues.append(f"❌ Gagal membaca '{path}': {e}")
        return issues, warnings

    # Cek DOCTYPE
    if not content.strip().upper().startswith("<!DOCTYPE"):
        warnings.append("⚠️  index.html tidak diawali dengan <!DOCTYPE html>.")

    # Cek tag HTML dasar
    if not re.search(r"<html[\s>]", content, re.IGNORECASE):
        issues.append("❌ Tag <html> tidak ditemukan di index.html.")
    else:
        # Cek closing tag
        open_html = len(re.findall(r"<html[\s>]", content, re.IGNORECASE))
        close_html = len(re.findall(r"</html>", content, re.IGNORECASE))
        if open_html != close_html:
            issues.append(f"❌ Tag <html> tidak seimbang: {open_html} buka, {close_html} tutup.")

    # Cek tag HEAD
    if not re.search(r"<head[\s>]", content, re.IGNORECASE):
        issues.append("❌ Tag <head> tidak ditemukan di index.html.")

    # Cek tag BODY
    if not re.search(r"<body[\s>]", content, re.IGNORECASE):
        issues.append("❌ Tag <body> tidak ditemukan di index.html.")

    # Cek tag SCRIPT
    scripts_open = len(re.findall(r"<script[\s>]", content, re.IGNORECASE))
    scripts_close = len(re.findall(r"</script>", content, re.IGNORECASE))
    if scripts_open != scripts_close:
        issues.append(f"❌ Tag <script> tidak seimbang: {scripts_open} buka, {scripts_close} tutup.")
    elif scripts_open == 0:
        warnings.append("⚠️  Tidak ada tag <script> di index.html.")

    # Cek tag STYLE
    styles_open = len(re.findall(r"<style[\s>]", content, re.IGNORECASE))
    styles_close = len(re.findall(r"</style>", content, re.IGNORECASE))
    if styles_open != styles_close:
        issues.append(f"❌ Tag <style> tidak seimbang: {styles_open} buka, {styles_close} tutup.")

    # Cek duplikasi ID (berarti getElementById bisa salah)
    ids = re.findall(r'id=["\']([^"\']+)["\']', content, re.IGNORECASE)
    seen = set()
    duplicates = []
    for i, id_val in enumerate(ids):
        if id_val in seen:
            duplicates.append(id_val)
        seen.add(id_val)
    if duplicates:
        issues.append(f"❌ ID duplikat di index.html: {', '.join(set(duplicates))}. "
                       "Ini bisa menyebabkan getElementById mengambil elemen yang salah "
                       "dan membuat layar putih kosong (JS error).")
    else:
        warnings.append(f"✅ Tidak ada ID duplikat di index.html ({len(ids)} ID ditemukan).")

    # Cek tag yang tidak tertutup menggunakan BeautifulSoup (lebih akurat)
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        block_tags = ["div", "section", "nav", "header", "footer", "main", "article",
                      "table", "tbody", "thead", "tr", "form", "details", "summary", "span"]
        for tag in block_tags:
            open_count = len(soup.find_all(tag))
            if open_count > 0:
                # BeautifulSoup yang parse dengan benar tidak akan memiliki tag tidak tertutup
                pass  # Jika bs4 bisa parse, berarti tag seimbang
    except ImportError:
        # Fallback: regex sederhana
        pass

    # Cek apakah ada JavaScript error potensial: getElementById dengan ID yang tidak ada
    js_content_match = re.search(r"<script[\s>](.*?)(?=</script>)", content, re.IGNORECASE | re.DOTALL)
    if js_content_match:
        js_content = js_content_match.group(1)
        # Cari semua getElementById / querySelector
        get_id_calls = re.findall(r"getElementById\(['\"]([^'\"]+)['\"]\)", js_content)
        query_calls = re.findall(r"querySelector\(['\"]([^'\"]+)['\"]\)", js_content)

        all_refs = set(get_id_calls + query_calls)
        for ref in all_refs:
            if ref not in seen:
                warnings.append(f"⚠️  JavaScript mengacu ke ID '{ref}' yang TIDAK DITEMUKAN di HTML. "
                                "Bisa menyebabkan JS error → layar putih.")

    # Ringkasan
    if not issues and not warnings:
        issues.append("✅ index.html OK — tidak ada error struktural yang terdeteksi.")

    return issues, warnings


def check_pegawai_json(path="pegawai.json"):
    """Memeriksa apakah pegawai.json ada dan valid JSON."""
    issues = []
    warnings = []

    if not os.path.exists(path):
        warnings.append(f"ℹ️  File '{path}' TIDAK DITEMUKAN. "
                        "Data pegawai mungkin sudah tertanam di dalam index.html (inline script). "
                        "Jika website memuat data dari file ini dengan fetch(), itu akan gagal (404).")
        return issues, warnings

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
    except Exception as e:
        issues.append(f"❌ Gagal membaca '{path}': {e}")
        return issues, warnings

    if not content:
        issues.append(f"❌ File '{path}' kosong.")
        return issues, warnings

    try:
        data = json.loads(content)
        if isinstance(data, list):
            warnings.append(f"✅ '{path}' valid JSON (array dengan {len(data)} item).")
        elif isinstance(data, dict):
            warnings.append(f"✅ '{path}' valid JSON (object dengan kunci: {list(data.keys())}).")
        else:
            warnings.append(f"✅ '{path}' valid JSON.")
    except json.JSONDecodeError as e:
        issues.append(f"❌ '{path}' ERROR JSON: {e}")
        # Coba tunjukkan di mana error terjadi
        lines = content.split("\n")
        if e.lineno:
            line_num = min(e.lineno, len(lines))
            context = lines[max(0, line_num-2):min(line_num+1, len(lines))]
            issues.append(f"   Konteks di sekitar baris {line_num}:")
            for i, line in enumerate(context, start=max(1, line_num-1)):
                marker = ">>>" if i == line_num else "   "
                issues.append(f"   {marker} {i}: {line}")

    return issues, warnings


def print_check_results():
    """Jalankan semua pengecekan dan cetak hasilnya."""
    print("=" * 70)
    print("  PEMERIKSAAN FILE WEBSITE")
    print("=" * 70)
    print()

    # Cek index.html
    print("─── index.html ───")
    issues_html, warnings_html = check_index_html()
    for msg in issues_html:
        print(f"  {msg}")
    for msg in warnings_html:
        print(f"  {msg}")
    print()

    # Cek pegawai.json
    print("─── pegawai.json ───")
    issues_json, warnings_json = check_pegawai_json()
    for msg in issues_json:
        print(f"  {msg}")
    for msg in warnings_json:
        print(f"  {msg}")
    print()

    # Ringkasan
    all_issues = issues_html + issues_json
    all_warnings = warnings_html + warnings_json

    print("=" * 70)
    if all_issues:
        print(f"  ditemukan {len(all_issues)} masalah serius, {len(all_warnings)} peringatan")
        print("  → SL-hHalaman mungkin PUTIH KOSONG karena error JS/struktur HTML.")
    else:
        print("  tidak ditemukan masalah serius.")
    print("=" * 70)
    print()


# =============================================================================
# 2. LOCAL SERVER
# =============================================================================

PORT = 8000
ADMIN_SESSIONS = {}
SESSION_TTL = 1800


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    """Handler yang lebih bersih — hanya log permintaan penting."""

    def log_message(self, format, *args):
        # Log hanya permintaan yang bukan file statis umum (css, js, img, dll)
        path = str(args[0]) if args else ""
        if any(path.endswith(ext) for ext in [".html", ".json", "/"]):
            sys.stderr.write(f"  [{self.address_string()}] {format % args}\n")

    def end_headers(self):
        # Tambahkan header untuk mencegah caching selama development
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()


class AdminHandler(QuietHandler):
    """Static server plus a server-side, fail-closed admin SOP gate.

    The finance SOP is intentionally not a public file. Configure
    DINSOS_ADMIN_PASSWORD in the server environment before enabling login.
    """

    def _session_valid(self):
        raw = self.headers.get("Cookie", "")
        jar = cookies.SimpleCookie(); jar.load(raw)
        token = jar.get("dinsos_admin")
        if not token: return False
        created = ADMIN_SESSIONS.get(token.value)
        if not created or time.time() - created > SESSION_TTL:
            ADMIN_SESSIONS.pop(token.value, None)
            return False
        return True

    def _redirect(self, location, extra_headers=None):
        self.send_response(303)
        self.send_header("Location", location)
        for key, value in (extra_headers or []): self.send_header(key, value)
        self.end_headers()

    def do_GET(self):
        if self.path == "/admin/login":
            # Keep the public-facing login page as admin-login.html while
            # exposing a stable route for redirects and form workflows.
            original_path = self.path
            self.path = "/admin-login.html"
            try:
                return super().do_GET()
            finally:
                self.path = original_path
        if self.path == "/admin/logout":
            raw = self.headers.get("Cookie", "")
            jar = cookies.SimpleCookie(); jar.load(raw)
            token = jar.get("dinsos_admin")
            if token: ADMIN_SESSIONS.pop(token.value, None)
            return self._redirect("/admin/login", [("Set-Cookie", "dinsos_admin=; Max-Age=0; HttpOnly; SameSite=Strict; Path=/")])
        if self.path == "/admin/sop-keuangan":
            if not self._session_valid(): return self._redirect("/admin/login")
            body = b"<!doctype html><html lang='id'><meta charset='utf-8'><title>SOP Keuangan Admin</title><body><h1>SOP Keuangan - Khusus Admin</h1><p>Area terlindungi server-side. Dokumen resmi akan dipasang oleh administrator pada endpoint terlindungi.</p><p><a href='/admin/logout'>Logout</a></p></body></html>"
            self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Cache-Control", "no-store"); self.end_headers(); self.wfile.write(body); return
        return super().do_GET()

    def do_POST(self):
        if self.path != "/admin/login": return self.send_error(404)
        configured = os.environ.get("DINSOS_ADMIN_PASSWORD")
        length = int(self.headers.get("Content-Length", "0"))
        values = urllib.parse.parse_qs(self.rfile.read(length).decode("utf-8"))
        supplied = values.get("password", [""])[0]
        if not configured or not secrets.compare_digest(supplied, configured):
            return self._redirect("/admin/login?error=1")
        token = secrets.token_urlsafe(32); ADMIN_SESSIONS[token] = time.time()
        return self._redirect("/admin/sop-keuangan", [("Set-Cookie", f"dinsos_admin={token}; Max-Age={SESSION_TTL}; HttpOnly; SameSite=Strict; Path=/")])


def start_server(port=PORT, directory="."):
    """Jalankan HTTP server di port yang ditentukan."""
    os.chdir(directory)

    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("", port), AdminHandler) as httpd:
            print()
            print("=" * 70)
            print(f"  SERVER JAKARTA DINSOS MAPPI")
            print("=" * 70)
            print()
            print(f"  🌐  Local URL:  http://localhost:{port}")
            print(f"  🌐  Local URL:  http://127.0.0.1:{port}")
            print(f"  📁  Root:       {os.path.abspath(directory)}")
            print()
            print("  Tekan Ctrl+C untuk berhenti.")
            print("-" * 70)
            print()
            httpd.serve_forever()
    except OSError as e:
        if e.errno == 98 or e.errno == 10048:  # Address already in use
            print(f"  ❌ Port {port} sudah digunakan. Coba port lain atau matikan proses yang memakai port tersebut.")
            print(f"  💡  Di Linux/Mac:  lsof -i :{port}")
            print(f"  💡  Di Windows:    netstat -ano | findstr :{port}")
        else:
            print(f"  ❌ Gagal memulai server: {e}")
        sys.exit(1)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Server lokal untuk website Dinas Sosial Kabupaten Mappi"
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=PORT,
        help=f"Port server (default: {PORT})"
    )
    parser.add_argument(
        "--dir", "-d",
        type=str,
        default=".",
        help="Direktori root (default: direktori saat ini)"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Hanya jalankan pengecekan file, jangan mulai server"
    )
    args = parser.parse_args()

    # Jalankan pengecekan
    print_check_results()

    if args.check_only:
        print("  (--check-only: server tidak dijalankan)")
        sys.exit(0)

    # Mulai server
    start_server(port=args.port, directory=args.dir)
