# Architectural & Technical Design Document (TDD)
## SilatTrack: DATH Stack & Material Design 3 Architecture

- **Stack**: **DATH** (Django 5.x + Alpine.js 3.x + Tailwind CSS 3.x + HTMX 2.x)
- **Paradigma**: HTML-over-the-Wire / Modern Monolith
- **UI Framework**: Google Material Design 3 (M3) Design Tokens via Tailwind CSS
- **Status**: Production Blueprint

---

## 1. Arsitektur DATH Stack & Prinsip HTML-over-the-Wire

```
   ┌────────────────────────────────────────────────────────┐
   │             Browser Client (Mobile / PWA)              │
   │  ┌─────────────────────────┐  ┌─────────────────────┐  │
   │  │   Alpine.js (Client)    │  │     HTMX Engine     │  │
   │  │ - Kamera Barcode Scan   │  │ - HTML-over-the-Wire│  │
   │  │ - Client Timer / UI     │  │ - Instant Partial   │  │
   │  │ - Modal / Dialog        │  │   DOM Swaps         │  │
   │  └────────────┬────────────┘  └──────────▲──────────┘  │
   │               │                          │             │
   │               ▼ (DOM Events / Fetch)     │ (HTML)      │
   └───────────────┼──────────────────────────┼─────────────┘
                   │                          │
        HTTP Request / CSRF Token             │ Hypermedia Response (HTML snippets)
                   │                          │
   ┌───────────────▼──────────────────────────┴─────────────┐
   │                Django Application Server               │
   │  ┌──────────────────────────────────────────────────┐  │
   │  │             Django URL Routing / Views           │  │
   │  │   - Full Page Views (First Load / Direct URL)    │  │
   │  │   - HTMX Partial Fragment Views (hx-target)      │  │
   │  └───────────────────────┬──────────────────────────┘  │
   │                          │                             │
   │  ┌───────────────────────▼──────────────────────────┐  │
   │  │                 Django Template Engine           │  │
   │  │   - Material Design 3 Template Components        │  │
   │  │   - Atomic Partials (`partials/_row_pesilat.html`)│ │
   │  └───────────────────────┬──────────────────────────┘  │
   │                          │                             │
   │  ┌───────────────────────▼──────────────────────────┐  │
   │  │      Django ORM & Business Logic Services        │  │
   │  │   - QR Token Hash Generator (HMAC-SHA256)        │  │
   │  │   - Geolocation Haversine Calculator             │  │
   │  │   - Attendance Streak & UKT Eligibility Engine   │  │
   │  └───────────────────────┬──────────────────────────┘  │
   └──────────────────────────┼─────────────────────────────┘
                              │
                    PostgreSQL / SQLite Database
```

### Mengapa DATH Stack untuk Aplikasi Ini?
1. **Zero JavaScript Build Fatigue**: Tidak memerlukan Node.js server, bundler rumit (Webpack/Vite), atau state management terpisah (Redux/Pinia).
2. **Kinerja Instan**: Django merender HTML di server; HTMX hanya menukar potongan DOM yang relevan (*Hypermedia as the Engine of Application State* - HATEOAS).
3. **Mobile-First UX**: Alpine.js menangani micro-interactions sisi klien (kamera pemindai QR code, dialog bottom sheet, countdown timer rotasi QR) dengan overhead < 15KB.
4. **Keamanan Bawaan**: Django menyediakan proteksi bawaan CSRF, Clickjacking, SQL Injection, dan ORM yang aman.

---

## 2. Pola Interaksi HTMX & Alpine.js

### 2.1 Pola Dynamic Rolling QR Code (Anti-Replay Attack)
Pelatih menampilkan QR Code pada layar. Untuk mencegah siswa mengirim screenshot QR ke temannya di luar tempat latihan, QR Code diperbarui otomatis setiap 15 detik menggunakan polling HTMX.

```html
<!-- Container QR Code pada Dashboard Pelatih -->
<div 
  id="qr-container"
  hx-get="{% url 'attendance:get_session_qr' sesi.id %}"
  hx-trigger="every 15s"
  hx-swap="innerHTML transition:true"
  class="flex flex-col items-center justify-center p-6 bg-surface-container-low rounded-3xl"
>
  <!-- Fragment parsial yang di-render ulang -->
  {% include 'attendance/partials/_qr_display.html' %}
</div>
```

### 2.2 Pola Quick Toggle Presensi oleh Pelatih (Zero Page Reload)
Daftar absensi anggota di meja pelatih dapat diubah statusnya (Hadir -> Sakit -> Izin -> Alpa) dengan sekali sentuh menggunakan HTMX inline swap dan out-of-band updates untuk statistik counter.

```html
<!-- Baris Pesilat -->
<tr id="pesilat-row-{{ item.id }}" class="border-b border-outline-variant">
  <td class="py-3 px-4 font-medium">{{ item.anggota.user.get_full_name }}</td>
  <td class="py-3 px-4">
    <div class="inline-flex rounded-full p-1 bg-surface-container-high">
      <button 
        hx-post="{% url 'attendance:toggle_status' sesi.id item.anggota.id %}?status=HADIR"
        hx-target="#pesilat-row-{{ item.id }}"
        hx-swap="outerHTML"
        class="px-3 py-1 text-xs rounded-full {% if item.status == 'HADIR' %}bg-primary text-on-primary{% else %}text-on-surface-variant{% endif %}">
        Hadir
      </button>
      <button 
        hx-post="{% url 'attendance:toggle_status' sesi.id item.anggota.id %}?status=IZIN"
        hx-target="#pesilat-row-{{ item.id }}"
        hx-swap="outerHTML"
        class="px-3 py-1 text-xs rounded-full {% if item.status == 'IZIN' %}bg-secondary text-on-secondary{% else %}text-on-surface-variant{% endif %}">
        Izin
      </button>
    </div>
  </td>
</tr>

<!-- Out-of-Band Update Counter (di-render di dalam partial yang sama) -->
<div id="counter-hadir-badge" hx-swap-oob="true" class="badge-m3">
  Total Hadir: {{ sesi.total_hadir }}
</div>
```

### 2.3 Pola Alpine.js HTML5 QR Scanner
Siswa membuka modul scan melalui kamera browser tanpa native app:

```html
<div x-data="qrScannerHandler('{% url 'attendance:submit_qr_scan' sesi.id %}')" class="relative">
  <!-- Video Viewfinder -->
  <div id="qr-video-region" class="w-full max-w-sm rounded-3xl overflow-hidden shadow-elevation-2"></div>
  
  <!-- Status Feedback -->
  <div x-show="isProcessing" class="mt-4 flex items-center gap-2 text-primary font-medium">
    <span class="animate-spin">⏳</span> Memverifikasi kehadiran pesilat...
  </div>
</div>

<script>
function qrScannerHandler(submitUrl) {
  return {
    isProcessing: false,
    init() {
      const html5QrCode = new Html5Qrcode("qr-video-region");
      html5QrCode.start(
        { facingMode: "environment" },
        { fps: 10, qrbox: { width: 250, height: 250 } },
        (decodedText) => {
          this.isProcessing = true;
          // Trigger HTMX request secara programatik dengan payload
          htmx.ajax('POST', submitUrl, {
            values: { qr_token: decodedText },
            target: '#scanner-result-modal',
            swap: 'innerHTML'
          });
          html5QrCode.stop();
        }
      );
    }
  }
}
</script>
```

---

## 3. Sistem Desain: Google Material Design 3 (M3) Tokens

Implementasi warna dan token M3 diselaraskan dengan tema Pencak Silat (Karakter pendekar: *Deep Maroon / Silat Crimson* dan aksen *Golden Brass*).

### 3.1 Konfigurasi Palet Warna M3 (`tailwind.config.js`)

```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        // M3 Silat Palette
        primary: {
          DEFAULT: '#8A1C14',       // Crimson Pendekar
          container: '#FFDAD5',     // Container lembut
        },
        'on-primary': {
          DEFAULT: '#FFFFFF',
          container: '#410001',
        },
        secondary: {
          DEFAULT: '#77574E',
          container: '#FFDBD1',
        },
        'on-secondary': {
          DEFAULT: '#FFFFFF',
          container: '#2C150F',
        },
        tertiary: {
          DEFAULT: '#725B2E',       // Gold / Kuningan
          container: '#FEDFA6',
        },
        'on-tertiary': {
          DEFAULT: '#FFFFFF',
          container: '#261900',
        },
        surface: {
          DEFAULT: '#FFF8F6',
          dim: '#E8D6D3',
          bright: '#FFF8F6',
          'container-lowest': '#FFFFFF',
          'container-low': '#FFF0EE',
          'container': '#FCEAE6',
          'container-high': '#F7E4E1',
          'container-highest': '#F1DEDC',
        },
        'on-surface': {
          DEFAULT: '#231918',
          variant: '#534341',
        },
        outline: {
          DEFAULT: '#857371',
          variant: '#D8C2BE',
        },
        error: {
          DEFAULT: '#BA1A1A',
          container: '#FFDAD6',
        }
      },
      borderRadius: {
        'none': '0',
        'xs': '4px',
        'sm': '8px',
        'md': '12px',
        'lg': '16px',
        'xl': '28px',       // Standar M3 Container / Card besar
        'full': '9999px',   // Standar M3 Pill / FAB / Buttons
      },
      boxShadow: {
        'elevation-1': '0px 1px 3px 1px rgba(0, 0, 0, 0.15), 0px 1px 2px 0px rgba(0, 0, 0, 0.30)',
        'elevation-2': '0px 2px 6px 2px rgba(0, 0, 0, 0.15), 0px 1px 2px 0px rgba(0, 0, 0, 0.30)',
        'elevation-3': '0px 4px 8px 3px rgba(0, 0, 0, 0.15), 0px 1px 3px 0px rgba(0, 0, 0, 0.30)',
      }
    }
  }
}
```

### 3.2 Komponen Kunci M3
- **Extended Floating Action Button (FAB)**: Berada di sudut kanan bawah dengan elevasi level 3 dan rounded `full`, digunakan untuk scan instan atau mulai sesi latihan.
- **M3 Navigation Bar (Bottom Navigation Mobile)**: 4 target navigasi dengan pill active indicator (`bg-secondary-container text-on-secondary-container`).
- **M3 Outlined Card**: Digunakan untuk menampilkan data kehadiran harian dan profil kartu anggota pesilat.

---

## 4. Struktur Proyek Django (Modular & Scalable)

```
absensi_eskul_pencak_silat/
├── manage.py
├── requirements.txt
├── docs/
│   ├── PRD.md
│   ├── ERD.md
│   └── ARCHITECTURE.md
├── silattrack_core/             # Django Main Project Settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── apps/
│   ├── accounts/                # Custom User, Auth, RBAC
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   └── urls.py
│   ├── members/                 # Data Anggota, Sabuk, Prestasi
│   │   ├── models.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── schedule/                # Jadwal Latihan Mingguan
│   │   ├── models.py
│   │   ├── views.py
│   │   └── urls.py
│   └── attendance/              # Sesi Latihan, Dynamic QR, Presensi
│       ├── models.py
│       ├── views.py
│       ├── services.py          # HMAC QR Generator, Haversine Geolocation
│       ├── urls.py
│       └── reports.py           # Export Excel & PDF generator
├── templates/
│   ├── base.html                # App Shell (M3 Header, Navigation Bar/Rail)
│   ├── components/              # Reusable M3 Components (cards, buttons, inputs)
│   ├── accounts/
│   ├── members/
│   ├── schedule/
│   └── attendance/
│       ├── session_detail.html
│       ├── scanner.html
│       └── partials/            # HTMX Small Fragments
│           ├── _qr_display.html
│           ├── _pesilat_row.html
│           └── _scan_success.html
└── static/
    ├── css/
    │   └── input.css            # Tailwind Directives
    └── js/
        ├── htmx.min.js
        ├── alpine.min.js
        └── html5-qrcode.min.js
```

---

## 5. Algoritma Keamanan Dynamic QR & Geofence

### 5.1 Dynamic QR Payload Formula
Payload QR di-generate di server Django setiap interval waktu $\Delta t = 15 \text{ detik}$:
$$\text{TimeSlot} = \lfloor \frac{\text{CurrentTimestamp}}{\Delta t} \rfloor$$
$$\text{Signature} = \text{HMAC-SHA256}(\text{Key} = \text{sesi.qr\_secret\_salt}, \text{Msg} = \text{sesi.id} + ":" + \text{TimeSlot})$$
$$\text{QR Payload} = \text{base64url}(\text{sesi.id} + "." + \text{TimeSlot} + "." + \text{Signature})$$

- **Verifikasi**: Server memvalidasi bahwa $\text{TimeSlot}$ pada token berada dalam toleransi $\pm 1$ slot (toleransi 15 detik untuk latensi jaringan). Jika waktu kedaluwarsa, presensi ditolak.

### 5.2 Geofence Formula (Haversine Distance)
Memvalidasi siswa benar-benar berada di tempat latihan:
$$d = 2r \arcsin \left( \sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta \lambda}{2}\right)} \right)$$
Jika $d \le \text{radius\_toleransi\_meter}$, absensi dianggap sah secara lokasi.
