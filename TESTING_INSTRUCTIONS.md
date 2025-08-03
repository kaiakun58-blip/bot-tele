# 🧪 ObrolanId Testing Instructions

Gunakan checklist ini untuk memastikan semua fitur berfungsi 100%.

## 📋 Pre-Requirements

1. **Install Dependencies:**
```bash
pip install python-telegram-bot>=20.0 requests>=2.28.0 python-dotenv>=1.0.0
```

2. **Setup Environment:**
```bash
cp .env.example .env
# Edit .env dengan bot token dari @BotFather
```

3. **Run Bot:**
```bash
python3 bot.py
```

## ✅ Testing Checklist

### 🎯 **1. Basic Flow (CRITICAL)**
- [ ] `/start` menampilkan welcome message lengkap dengan command list
- [ ] User baru dapat 1200 poin otomatis
- [ ] Menu utama dengan 8 tombol muncul
- [ ] Semua shortcut buttons (🏠 Menu, 👤 Profile, 📊 Stats) berfungsi

### 👤 **2. Profile System (FIXED)**
- [ ] `/profile` memulai conversation
- [ ] Pilih gender → berhasil lanjut ke umur (TIDAK MENTOK)
- [ ] Input umur → lanjut ke bio
- [ ] Input bio → lanjut ke upload foto
- [ ] Upload foto → lanjut ke pilih bahasa
- [ ] Pilih bahasa → lanjut ke pilih hobi
- [ ] Pilih hobi → profil tersimpan, kembali ke menu
- [ ] `My Profile` menampilkan profil lengkap dengan foto

### 💬 **3. Chat System**
- [ ] `Find a partner` berfungsi (dengan/tanpa profil lengkap)
- [ ] User tanpa profil tetap bisa chat (mode basic)
- [ ] Chat menu muncul dengan shortcuts
- [ ] `Next` ganti partner
- [ ] `Stop` akhiri chat
- [ ] Forward pesan (text, foto, voice, sticker) berfungsi

### 🎯 **4. Pro Search (RESTORED)**
- [ ] `Search Pro` menampilkan pilihan untuk Pro users
- [ ] Non-Pro user melihat upgrade options
- [ ] Pro users dapat akses:
  - [ ] Search by Gender (Male/Female/Other/Any)
  - [ ] Search by Hobby
  - [ ] Search by Age range
  - [ ] Advanced Search (kombinasi)

### 💰 **5. Payment System (NEW)**
- [ ] `Upgrade to Pro` menampilkan paket & harga
- [ ] **Demo Payment**: `/pay week` atau `/pay month` langsung aktifkan Pro
- [ ] **Points Redemption**: Tukar 1000 poin → 7 hari Pro
- [ ] **Payment Methods**: Info bank transfer, e-wallet, QRIS
- [ ] Pro status ditampilkan di profile & menu
- [ ] Pro expires otomatis setelah periode habis

### 🔧 **6. Navigation & Shortcuts**
Dari setiap screen, test shortcut buttons:
- [ ] 🏠 Menu → Kembali ke main menu
- [ ] 👤 Profile → Tampilkan profil
- [ ] 📊 Stats → Statistik bot
- [ ] ⚙️ Settings → Menu utama
- [ ] 🔍 Help → Help command

### 📊 **7. Stats & Info**
- [ ] `/stats` menampilkan statistik user & leaderboard
- [ ] `/help` menampilkan command list lengkap
- [ ] User stats menampilkan Pro status & poin

## 🧪 **Test Scenarios**

### **Scenario 1: New User Journey**
1. User baru start bot → Welcome message muncul
2. Skip profile → Bisa langsung chat (mode basic)
3. Upgrade to Pro → Test payment/points redemption
4. Search Pro → Test advanced search

### **Scenario 2: Profile Completion**
1. Complete profile → Test full conversation flow
2. Verify each step works (gender → age → bio → photo → language → hobby)
3. Check profile display dengan foto

### **Scenario 3: Chat Testing**
1. Find partner → Test matching
2. Send berbagai jenis pesan (text, foto, voice)
3. Test shortcuts saat chat
4. Test Next & Stop

### **Scenario 4: Pro Features**
1. Get Pro status (payment/points)
2. Test Search Pro dengan berbagai filter
3. Verify Pro badge di profile
4. Test Pro expiry

## 🚨 **Critical Issues to Check**

1. **Profile conversation TIDAK mentok di gender** ✅
2. **Shortcut buttons muncul di semua screen** ✅
3. **Payment system berfungsi** ✅
4. **Pro Search features accessible** ✅
5. **Chat tanpa profil lengkap works** ✅

## 📞 **Demo Commands**

For quick testing:
```bash
/start          # Welcome & main menu
/profile        # Complete profile setup
/find           # Find chat partner
/searchpro      # Pro search features
/upgrade        # Pro membership options
/pay week       # Demo payment (instant Pro)
/stats          # Bot statistics
/help           # All commands
```

## 🎉 **Success Criteria**

✅ **100% Functional** if:
- Profile conversation works completely
- Chat system works (basic & Pro)
- Payment system activates Pro
- All shortcuts accessible from any screen
- No crashes or hanging conversations

## 🐛 **If Issues Found**

1. Check logs for error messages
2. Verify bot token in .env
3. Ensure dependencies installed
4. Check conversation handler conflicts
5. Test with multiple users

---

**Expected Result**: Fully functional ObrolanId bot with all features working seamlessly! 🚀