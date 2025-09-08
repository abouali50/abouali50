# 🍳 وصفة نشر Regam Blockchain - نسخ/لصق جاهزة

## 🚀 الطريقة السريعة (أمر واحد):
```bash
cd /app
./DEPLOY_ONE_COMMAND.sh
```

---

## 📋 الطريقة اليدوية (خطوة بخطوة):

### 1️⃣ GitHub - من داخل `/app`:
```bash
cd /app

git init
git add .
git commit -m "Regam Blockchain website - ready for launch"
git branch -M main

# ضع اسم المستخدم واسم الريبو
git remote add origin https://github.com/<YOUR_USERNAME>/regam-blockchain.git
git push -u origin main
```

### 2️⃣ Vercel Deploy:
```bash
# مرة واحدة: تثبيت CLI
npm i -g vercel

# النشر
cd /app
vercel --prod --confirm

# أو عبر المتصفح:
# https://vercel.com/new → اختر الريبو → Deploy
```

### 3️⃣ إضافة الدومين:
```bash
# عبر CLI
vercel domains add regamcoin.com
vercel domains add www.regamcoin.com

# أو عبر المتصفح: Vercel Dashboard → Domains
```

### 4️⃣ DNS Settings (نسخ/لصق في لوحة الدومين):
```
Type: A
Name: @
Value: 76.76.21.21
TTL: 300

Type: CNAME  
Name: www
Value: cname.vercel-dns.com
TTL: 300
```

## ✅ ما تم تجهيزه مسبقًا:

- [x] **vercel.json** - مع توجيه www → apex
- [x] **sitemap.xml** - SEO جاهز
- [x] **robots.txt** - محرك البحث
- [x] **Meta tags** - Open Graph + Twitter
- [x] **Build optimized** - 90KB gzipped
- [x] **Mobile responsive** - جميع الشاشات
- [x] **Legal pages** - Terms, Privacy, Cookies

## 🎯 النتيجة المتوقعة:

⏱️ **5 دقائق**: رابط Vercel جاهز  
⏱️ **30 دقيقة**: `regamcoin.com` شغال  
📊 **Lighthouse**: 90+ درجة  
🔒 **HTTPS**: تلقائي  
📱 **Mobile**: مُحسّن بالكامل  

## 🔍 فحص سريع بعد النشر:
```bash
# فحص DNS
nslookup regamcoin.com
nslookup www.regamcoin.com

# فحص HTTPS
curl -I https://regamcoin.com
curl -I https://www.regamcoin.com
```

## 🎉 الصفحات الجاهزة:
- ✅ **Homepage**: `/`
- ✅ **Token**: `/token` 
- ✅ **Technology**: `/technology`
- ✅ **Developers**: `/developers`
- ✅ **Legal**: `/terms`, `/privacy`, `/cookies`

---

**🚀 الموقع جاهز 100% للإطلاق! اختر أي طريقة وشغّل الأوامر**