#!/bin/bash

# 🚀 Regam Blockchain - VIP Deployment Script
# كل شيء أوتوماتيك: Git + Vercel + Domain + Analytics

echo "🔥 === REGAM BLOCKCHAIN VIP DEPLOYMENT ==="
echo "🚀 سكريپت نشر احترافي - كل شيء أوتوماتيك"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. Pre-flight checks
print_status "فحص المتطلبات..."

# Check if git is installed
if ! command -v git &> /dev/null; then
    print_error "Git غير مثبت. يرجى تثبيت Git أولاً"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    print_error "npm غير مثبت. يرجى تثبيت Node.js أولاً"
    exit 1
fi

print_success "جميع المتطلبات متوفرة ✅"

# 2. Build the project
print_status "إنشاء build الإنتاج..."
cd /app/frontend

if npm run build; then
    print_success "Build تم بنجاح! 📦"
else
    print_error "فشل في إنشاء Build"
    exit 1
fi

# 3. Setup git
print_status "إعداد Git repository..."
cd /app

# Initialize git if not already initialized
if [ ! -d ".git" ]; then
    git init
    print_success "Git repository تم إنشاؤه"
fi

git add .
git commit -m "🚀 Regam Blockchain website - VIP deployment $(date)"
git branch -M main

# 4. GitHub setup
echo ""
print_status "=== إعداد GitHub ==="
echo "أدخل بيانات GitHub الخاصة بك:"

read -p "📋 اسم المستخدم على GitHub: " GITHUB_USER

if [ -z "$GITHUB_USER" ]; then
    print_error "اسم المستخدم مطلوب"
    exit 1
fi

read -p "📋 اسم الريبو (افتراضي: regam-blockchain): " REPO_NAME
REPO_NAME=${REPO_NAME:-regam-blockchain}

# Add remote if not exists
if ! git remote get-url origin &> /dev/null; then
    git remote add origin https://github.com/$GITHUB_USER/$REPO_NAME.git
    print_success "تم ربط GitHub repository"
fi

# Push to GitHub
print_status "رفع الكود إلى GitHub..."
if git push -u origin main --force; then
    print_success "تم رفع الكود بنجاح! 🔄"
    echo "🔗 الريبو: https://github.com/$GITHUB_USER/$REPO_NAME"
else
    print_warning "فشل في رفع الكود. تحقق من صحة البيانات"
fi

# 5. Install Vercel CLI if not installed
if ! command -v vercel &> /dev/null; then
    print_status "تثبيت Vercel CLI..."
    npm install -g vercel
fi

# 6. Deploy to Vercel
print_status "=== النشر على Vercel ==="
echo "سيتم فتح متصفح للمصادقة مع Vercel إذا لم تكن مسجل الدخول..."

# Deploy with automatic settings
if vercel --prod --confirm --force; then
    print_success "تم النشر على Vercel بنجاح! 🚀"
else
    print_error "فشل في النشر على Vercel"
    exit 1
fi

# 7. Add custom domain
echo ""
print_status "=== إضافة الدومين المخصص ==="
read -p "🌐 أدخل الدومين الخاص بك (مثال: regamcoin.com): " DOMAIN

if [ ! -z "$DOMAIN" ]; then
    print_status "إضافة الدومين: $DOMAIN"
    
    # Add apex domain
    if vercel domains add $DOMAIN 2>/dev/null; then
        print_success "تم إضافة $DOMAIN"
    else
        print_warning "$DOMAIN قد يكون مضاف مسبقاً أو يحتاج تحقق"
    fi
    
    # Add www subdomain
    if vercel domains add www.$DOMAIN 2>/dev/null; then
        print_success "تم إضافة www.$DOMAIN"
    else
        print_warning "www.$DOMAIN قد يكون مضاف مسبقاً"
    fi
    
    # Link domains to project
    vercel alias --prod $DOMAIN 2>/dev/null
    vercel alias --prod www.$DOMAIN 2>/dev/null
    
    echo ""
    print_success "🎉 تم كل شيء بنجاح!"
    echo ""
    echo "📊 === معلومات المشروع ==="
    echo "🔗 الريبو: https://github.com/$GITHUB_USER/$REPO_NAME"
    echo "🌐 الموقع: https://$DOMAIN"
    echo "🌐 مع www: https://www.$DOMAIN"
    echo ""
    print_warning "⚠️  لا تنس إعداد DNS Records:"
    echo "Type: A, Name: @, Value: 76.76.21.21"
    echo "Type: CNAME, Name: www, Value: cname.vercel-dns.com"
    echo ""
    print_status "⏱️ DNS يحتاج 15-60 دقيقة للتفعيل"
    
else
    print_status "تم تخطي إضافة الدومين"
fi

# 8. Final checks and suggestions
echo ""
print_success "🔥 === النشر مكتمل بنجاح! ==="
echo ""
echo "📋 الخطوات التالية:"
echo "✅ 1. إعداد DNS Records (إذا لم تفعل)"
echo "✅ 2. فحص الموقع بعد 30 دقيقة"
echo "✅ 3. تشغيل Lighthouse test"
echo "✅ 4. إعداد Google Analytics (اختياري)"
echo "✅ 5. إعداد monitoring (UptimeRobot)"
echo ""
print_success "موقع Regam Blockchain جاهز للانطلاق! 🚀"