#!/bin/bash

# 🚀 Regam Blockchain - One Command Deploy
echo "🚀 بدء نشر موقع Regam Blockchain..."

# 1. Build the project
echo "📦 إنشاء build الإنتاج..."
cd /app/frontend
npm run build

# 2. Return to root and setup git
echo "📋 إعداد Git..."
cd /app
git init
git add .
git commit -m "Regam Blockchain website - ready for launch"
git branch -M main

# 3. Ask for GitHub username and repo name
echo "📋 أدخل بيانات GitHub:"
read -p "اسم المستخدم على GitHub: " GITHUB_USER
read -p "اسم الريبو (اتركه فارغ للافتراضي regam-blockchain): " REPO_NAME

# Set default repo name if empty
if [ -z "$REPO_NAME" ]; then
    REPO_NAME="regam-blockchain"
fi

# 4. Add remote and push
echo "🔄 رفع الكود إلى GitHub..."
git remote add origin https://github.com/$GITHUB_USER/$REPO_NAME.git
git push -u origin main

# 5. Deploy with Vercel CLI
echo "🚀 النشر على Vercel..."
npx vercel --prod --confirm

# 6. Add custom domain
echo "🌐 إضافة الدومين المخصص..."
read -p "أدخل الدومين الخاص بك (مثال: regamcoin.com): " DOMAIN
npx vercel domains add $DOMAIN
npx vercel domains add www.$DOMAIN

echo "✅ تم! الموقع جاهز على:"
echo "🔗 Vercel URL: (سيظهر أعلاه)"
echo "🌐 الدومين الخاص: https://$DOMAIN"
echo "📋 لا تنس إعداد DNS records كما في الوصفة!"