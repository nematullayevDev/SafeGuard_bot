# 🛡️ SafeGuard Bot — Production Serverga Joylashtirish Qo'llanmasi

Ushbu qo'llanma SafeGuard Botini Linux VPS yoki bulutli platformalarda (Render, Railway) 24/7 rejimda, xatoliksiz va maksimal barqarorlik bilan ishga tushirish qadamlarini tushuntiradi.

---

## 🛠️ 1. VPS Serverda Ishga Tushirish (Tavsiya etiladi 🚀)

Operatsion tizim: **Ubuntu 20.04+ / Debian**

### 1-Qadam: Tizim paketlarini yangilash va kerakli dasturlarni o'rnatish
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv git -y
```

### 2-Qadam: Loyihani serverga yuklash
Bot kodlarini serverdagi `/var/www/SafeGuard_bot` manziliga yuklang.
```bash
sudo mkdir -p /var/www/SafeGuard_bot
sudo chown -R $USER:$USER /var/www/SafeGuard_bot
cd /var/www/SafeGuard_bot
# Kodlarni shu yerga yuklang yoki git orqali clone qiling
```

### 3-Qadam: Virtual muhit (venv) yaratish va paketlarni o'rnatish
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4-Qadam: `.env` sozlamalarini sozlash
Loyiha ichidagi `.env.example` faylidan nusxa olib, `.env` yarating:
```bash
cp .env.example .env
nano .env
```
Fayl ichidagi o'zgaruvchilarni (Bot tokeni, Virustotal API key, Admin ID va Gemini API key) kiriting va saqlang (`Ctrl+O`, `Enter`, `Ctrl+X`).

---

## 🔄 2. Fondagi Xizmat Sifatida Yoqish (2 ta usul)

### Usul A: PM2 Process Manager yordamida (Juda oson!)
PM2 botni fonda ishlatadi, loglarni boshqaradi va xatolik bo'lsa darhol qayta yoqadi.

1. NodeJS va PM2 o'rnatish:
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
sudo npm install pm2 -g
```

2. Botni ishga tushirish:
```bash
pm2 start ecosystem.config.js
```

3. Server o'chib yonganda avtomatik yonish sozlamalari:
```bash
pm2 save
pm2 startup
# Ekrandagi kelib chiqqan buyruqni nusxalab terminalda ishga tushiring!
```

- **Loglarni ko'rish**: `pm2 logs safeguard-bot`
- **Bot holatini ko'rish**: `pm2 status`
- **Botni to'xtatish**: `pm2 stop safeguard-bot`

---

### Usul B: Systemd Service yordamida (Linux Tizimi Xizmati)
Tashqi paketlarsiz (NodeJS-siz) toza Linux tizimi xizmati sifatida ishga tushirish.

1. Loyihadagi `safeguard.service` shablonini Linux tizimiga nusxalash:
```bash
sudo cp safeguard.service /etc/systemd/system/safeguard.service
```

2. Xizmatni yoqish va ishga tushirish:
```bash
sudo systemctl daemon-reload
sudo systemctl enable safeguard
sudo systemctl start safeguard
```

- **Status tekshirish**: `sudo systemctl status safeguard`
- **Loglarni ko'rish**: `journalctl -u safeguard -f --no-tail`
- **Qayta ishga tushirish**: `sudo systemctl restart safeguard`

---

## ☁️ 3. Cloud / PaaS Platformalarda (Render.com, Railway)

Agar botni Render yoki Railway platformasiga qo'ymoqchi bo'lsangiz, quyidagi muhim qoidalarga rioya qiling:

1. **Persistent Volume (Doimiy Disk) ulanishi**:
   - Platformaning sozlamalaridan yangi disk yarating (masalan, `/data` manziliga).
   - `.env` faylida bazani o'sha manzilga yo'naltiring:
     ```env
     DATABASE_URL=/data/users.db
     ```
   - *Aks holda har safar bot qayta yuklanganda foydalanuvchilar o'chib ketadi!*

2. **Port Binding va Webhook**:
   - Render bepul rejasida bot "so'nib qolmasligi" uchun `.env` fayliga `WEBHOOK_URL` kiriting.
   - Bot avtomatik HTTPS portini ochadi va asinxron webhooklar orqali ishlay boshlaydi.

---

## 🔬 4. Tizim Xavfsizligini Tekshirish

Bot ishga tushgach, admin profilidan quyidagilarni tekshiring:
1. `/stats` buyrug'ini yuboring (statistika chiqishi kerak).
2. "Baza Zaxirasi" tugmasini bosing (shaxsiy chatingizga `.db` fayli zaxira bo'lib kelishi kerak).
3. Guruhda `/settings` panelini ochib, filtrlarni sinab ko'ring.
