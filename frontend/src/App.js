import React, { useState, useEffect, createContext, useContext } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Label } from './components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './components/ui/table';
import { Badge } from './components/ui/badge';
import { Textarea } from './components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Users, CreditCard, TrendingUp, UserPlus, Settings, Globe, LogOut, Plus, Search, Filter, Eye, Edit, DollarSign, Gift, ShoppingCart, Award, Trophy, Crown, Medal, Star, ChevronRight, Progress } from 'lucide-react';
import { toast, Toaster } from 'sonner';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Context for Authentication
const AuthContext = createContext();
const useAuth = () => useContext(AuthContext);

// Context for Internationalization
const I18nContext = createContext();
const useI18n = () => useContext(I18nContext);

// Translations
const translations = {
  fr: {
    'app.title': 'Amicale Anouar',
    'nav.dashboard': 'Tableau de bord',
    'nav.members': 'Adhérents',
    'nav.payments': 'Paiements',
    'nav.reports': 'Rapports',
    'nav.settings': 'Paramètres',
    'auth.login': 'Connexion',
    'auth.email': 'Email',
    'auth.password': 'Mot de passe',
    'auth.logout': 'Déconnexion',
    'member.register': 'Devenir adhérent',
    'member.full_name': 'Nom complet',
    'member.sex': 'Sexe',
    'member.phone': 'Téléphone',
    'member.job': 'Profession',
    'member.project_type': 'Type de projet',
    'member.amount_paid': 'Montant versé',
    'member.balance': 'Reste à payer',
    'member.status': 'Statut',
    'member.join_date': 'Date d\'adhésion',
    'member.notes': 'Notes',
    'member.points': 'Points',
    'payment.add': 'Ajouter un paiement',
    'payment.amount': 'Montant',
    'payment.method': 'Méthode',
    'payment.note': 'Note',
    'payment.date': 'Date',
    'payment.recorded_by': 'Enregistré par',
    'points.add': 'Ajouter des points',
    'points.earned': 'Points gagnés',
    'points.total': 'Total points',
    'points.history': 'Historique des points',
    'points.transaction_type': 'Type',
    'points.description': 'Description',
    'points.leaderboard': 'Classement',
    'action.save': 'Enregistrer',
    'action.cancel': 'Annuler',
    'action.edit': 'Modifier',
    'action.view': 'Voir',
    'action.search': 'Rechercher',
    'status.pending': 'En attente',
    'status.active': 'Actif',
    'status.inactive': 'Inactif',
    'sex.male': 'Homme',
    'sex.female': 'Femme',
    'sex.other': 'Autre',
    'method.cash': 'Espèces',
    'method.bank': 'Virement',
    'method.mobile': 'Mobile Money',
    'reports.total_members': 'Total adhérents',
    'reports.total_collected': 'Total collecté',
    'reports.total_outstanding': 'Total en attente',
    'reports.active_members': 'Adhérents actifs',
    'reports.total_points': 'Points distribués',
    'reports.average_points': 'Moyenne points',
    'rewards.title': 'Récompenses',
    'rewards.catalog': 'Catalogue des récompenses',
    'rewards.cost': 'Coût',
    'rewards.stock': 'Stock',
    'rewards.redeem': 'Échanger',
    'rewards.out_of_stock': 'Rupture de stock',
    'rewards.low_stock': 'Stock faible',
    'rewards.category': 'Catégorie',
    'rewards.description': 'Description',
    'rewards.name': 'Nom',
    'rewards.points_required': 'Points requis',
    'rewards.category.materiel': 'Matériel',
    'rewards.category.services': 'Services',
    'rewards.category.reductions': 'Réductions',
    'rewards.category.privileges': 'Privilèges',
    'redemptions.title': 'Mes échanges',
    'redemptions.history': 'Historique des échanges',
    'redemptions.status': 'Statut',
    'redemptions.date': 'Date',
    'redemptions.status.pending': 'En attente',
    'redemptions.status.approved': 'Approuvé',
    'redemptions.status.delivered': 'Livré',
    'redemptions.status.rejected': 'Rejeté',
    'redemptions.status.canceled': 'Annulé',
    'redemptions.request': 'Demander un échange',
    'redemptions.note': 'Note (optionnelle)',
    'success.member_registered': 'Adhérent enregistré avec succès',
    'success.payment_added': 'Paiement ajouté avec succès',
    'success.member_updated': 'Adhérent mis à jour avec succès',
    'success.redemption_requested': 'Demande d\'échange envoyée avec succès',
    'success.redemption_approved': 'Échange approuvé avec succès',
    'success.redemption_delivered': 'Échange marqué comme livré',
    'success.redemption_rejected': 'Échange rejeté',
    'error.occurred': 'Une erreur s\'est produite',
    'error.insufficient_points': 'Points insuffisants',
    'error.out_of_stock': 'Produit en rupture de stock',
    'levels.title': 'Niveaux',
    'levels.current': 'Niveau actuel',
    'levels.next': 'Prochain niveau',
    'levels.progress': 'Progression',
    'levels.bronze': 'Bronze',
    'levels.silver': 'Argent',
    'levels.gold': 'Or',
    'levels.platinum': 'Platine',
    'levels.points_to_next': 'Points restants',
    'badges.title': 'Badges',
    'badges.earned': 'Badges obtenus',
    'badges.count': 'badges',
    'leaderboard.title': 'Classement',
    'leaderboard.monthly': 'Mensuel',
    'leaderboard.all_time': 'Général',
    'leaderboard.rank': 'Rang',
    'leaderboard.points': 'Points',
    'leaderboard.level': 'Niveau',
    'leaderboard.member': 'Membre',
    'leaderboard.top_3': 'Podium',
    'leaderboard.view_full': 'Voir le classement complet',
    'welcome.title': 'Bienvenue à l\'Amicale Anouar',
    'welcome.subtitle': 'Plateforme de gestion des adhérents',
    'welcome.cta': 'Devenir adhérent',
    'welcome.login': 'Connexion administrateur'
  },
  ar: {
    'app.title': 'جمعية أنوار',
    'nav.dashboard': 'لوحة التحكم',
    'nav.members': 'الأعضاء',
    'nav.payments': 'المدفوعات',
    'nav.reports': 'التقارير',
    'nav.settings': 'الإعدادات',
    'auth.login': 'تسجيل الدخول',
    'auth.email': 'البريد الإلكتروني',
    'auth.password': 'كلمة المرور',
    'auth.logout': 'تسجيل الخروج',
    'member.register': 'انضم كعضو',
    'member.full_name': 'الاسم الكامل',
    'member.sex': 'الجنس',
    'member.phone': 'الهاتف',
    'member.job': 'المهنة',
    'member.project_type': 'نوع المشروع',
    'member.amount_paid': 'المبلغ المدفوع',
    'member.balance': 'المبلغ المتبقي',
    'member.status': 'الحالة',
    'member.join_date': 'تاريخ الانضمام',
    'member.notes': 'ملاحظات',
    'member.points': 'النقاط',
    'payment.add': 'إضافة دفعة',
    'payment.amount': 'المبلغ',
    'payment.method': 'الطريقة',
    'payment.note': 'ملاحظة',
    'payment.date': 'التاريخ',
    'payment.recorded_by': 'سجل بواسطة',
    'points.add': 'إضافة نقاط',
    'points.earned': 'النقاط المكتسبة',
    'points.total': 'إجمالي النقاط',
    'points.history': 'تاريخ النقاط',
    'points.transaction_type': 'النوع',
    'points.description': 'الوصف',
    'points.leaderboard': 'المتصدرين',
    'action.save': 'حفظ',
    'action.cancel': 'إلغاء',
    'action.edit': 'تعديل',
    'action.view': 'عرض',
    'action.search': 'بحث',
    'status.pending': 'في الانتظار',
    'status.active': 'نشط',
    'status.inactive': 'غير نشط',
    'sex.male': 'ذكر',
    'sex.female': 'أنثى',
    'sex.other': 'آخر',
    'method.cash': 'نقدا',
    'method.bank': 'تحويل بنكي',
    'method.mobile': 'محفظة إلكترونية',
    'reports.total_members': 'إجمالي الأعضاء',
    'reports.total_collected': 'إجمالي المجمع',
    'reports.total_outstanding': 'إجمالي المعلق',
    'reports.active_members': 'الأعضاء النشطون',
    'reports.total_points': 'النقاط الموزعة',
    'reports.average_points': 'متوسط النقاط',
    'rewards.title': 'المكافآت',
    'rewards.catalog': 'كتالوج المكافآت',
    'rewards.cost': 'التكلفة',
    'rewards.stock': 'المخزون',
    'rewards.redeem': 'استبدال',
    'rewards.out_of_stock': 'نفد المخزون',
    'rewards.low_stock': 'مخزون منخفض',
    'rewards.category': 'الفئة',
    'rewards.description': 'الوصف',
    'rewards.name': 'الاسم',
    'rewards.points_required': 'النقاط المطلوبة',
    'rewards.category.materiel': 'مواد',
    'rewards.category.services': 'خدمات',
    'rewards.category.reductions': 'تخفيضات',
    'rewards.category.privileges': 'امتيازات',
    'redemptions.title': 'استبدالاتي',
    'redemptions.history': 'تاريخ الاستبدالات',
    'redemptions.status': 'الحالة',
    'redemptions.date': 'التاريخ',
    'redemptions.status.pending': 'في الانتظار',
    'redemptions.status.approved': 'موافق عليه',
    'redemptions.status.delivered': 'تم التسليم',
    'redemptions.status.rejected': 'مرفوض',
    'redemptions.status.canceled': 'ملغي',
    'redemptions.request': 'طلب استبدال',
    'redemptions.note': 'ملاحظة (اختيارية)',
    'success.member_registered': 'تم تسجيل العضو بنجاح',
    'success.payment_added': 'تم إضافة الدفعة بنجاح',
    'success.member_updated': 'تم تحديث العضو بنجاح',
    'success.redemption_requested': 'تم إرسال طلب الاستبدال بنجاح',
    'success.redemption_approved': 'تم الموافقة على الاستبدال بنجاح',
    'success.redemption_delivered': 'تم تسليم الاستبدال',
    'success.redemption_rejected': 'تم رفض الاستبدال',
    'error.occurred': 'حدث خطأ',
    'error.insufficient_points': 'نقاط غير كافية',
    'error.out_of_stock': 'المنتج غير متوفر',
    'levels.title': 'المستويات',
    'levels.current': 'المستوى الحالي',
    'levels.next': 'المستوى التالي',
    'levels.progress': 'التقدم',
    'levels.bronze': 'برونزي',
    'levels.silver': 'فضي',
    'levels.gold': 'ذهبي',
    'levels.platinum': 'بلاتيني',
    'levels.points_to_next': 'النقاط المتبقية',
    'badges.title': 'الشارات',
    'badges.earned': 'الشارات المحصلة',
    'badges.count': 'شارات',
    'leaderboard.title': 'المتصدرين',
    'leaderboard.monthly': 'شهري',    
    'leaderboard.all_time': 'عام',
    'leaderboard.rank': 'الترتيب',
    'leaderboard.points': 'النقاط',
    'leaderboard.level': 'المستوى',
    'leaderboard.member': 'العضو',
    'leaderboard.top_3': 'المنصة',
    'leaderboard.view_full': 'عرض الترتيب الكامل',
    'welcome.title': 'مرحبا بكم في جمعية أنوار',
    'welcome.subtitle': 'منصة إدارة الأعضاء',
    'welcome.cta': 'انضم كعضو',
    'welcome.login': 'دخول المدير'
  },
  en: {
    'app.title': 'Amicale Anouar',
    'nav.dashboard': 'Dashboard',
    'nav.members': 'Members',
    'nav.payments': 'Payments',
    'nav.reports': 'Reports',
    'nav.settings': 'Settings',
    'auth.login': 'Login',
    'auth.email': 'Email',
    'auth.password': 'Password',
    'auth.logout': 'Logout',
    'member.register': 'Become a Member',
    'member.full_name': 'Full Name',
    'member.sex': 'Sex',
    'member.phone': 'Phone',
    'member.job': 'Job',
    'member.project_type': 'Project Type',
    'member.amount_paid': 'Amount Paid',
    'member.balance': 'Balance',
    'member.status': 'Status',
    'member.join_date': 'Join Date',
    'member.notes': 'Notes',
    'member.points': 'Points',
    'payment.add': 'Add Payment',
    'payment.amount': 'Amount',
    'payment.method': 'Method',
    'payment.note': 'Note',
    'payment.date': 'Date',
    'payment.recorded_by': 'Recorded By',
    'points.add': 'Add Points',
    'points.earned': 'Points Earned',
    'points.total': 'Total Points',
    'points.history': 'Points History',
    'points.transaction_type': 'Type',
    'points.description': 'Description',
    'points.leaderboard': 'Leaderboard',
    'action.save': 'Save',
    'action.cancel': 'Cancel',
    'action.edit': 'Edit',
    'action.view': 'View',
    'action.search': 'Search',
    'status.pending': 'Pending',
    'status.active': 'Active',
    'status.inactive': 'Inactive',
    'sex.male': 'Male',
    'sex.female': 'Female',
    'sex.other': 'Other',
    'method.cash': 'Cash',
    'method.bank': 'Bank Transfer',
    'method.mobile': 'Mobile Money',
    'reports.total_members': 'Total Members',
    'reports.total_collected': 'Total Collected',
    'reports.total_outstanding': 'Total Outstanding',
    'reports.active_members': 'Active Members',
    'reports.total_points': 'Points Distributed',
    'reports.average_points': 'Average Points',
    'rewards.title': 'Rewards',
    'rewards.catalog': 'Rewards Catalog',
    'rewards.cost': 'Cost',
    'rewards.stock': 'Stock',
    'rewards.redeem': 'Redeem',
    'rewards.out_of_stock': 'Out of Stock',
    'rewards.low_stock': 'Low Stock',
    'rewards.category': 'Category',
    'rewards.description': 'Description',
    'rewards.name': 'Name',
    'rewards.points_required': 'Points Required',
    'rewards.category.materiel': 'Material',
    'rewards.category.services': 'Services',
    'rewards.category.reductions': 'Discounts',
    'rewards.category.privileges': 'Privileges',
    'redemptions.title': 'My Redemptions',
    'redemptions.history': 'Redemption History',
    'redemptions.status': 'Status',
    'redemptions.date': 'Date',
    'redemptions.status.pending': 'Pending',
    'redemptions.status.approved': 'Approved',
    'redemptions.status.delivered': 'Delivered',
    'redemptions.status.rejected': 'Rejected',
    'redemptions.status.canceled': 'Canceled',
    'redemptions.request': 'Request Redemption',
    'redemptions.note': 'Note (optional)',
    'success.member_registered': 'Member registered successfully',
    'success.payment_added': 'Payment added successfully',
    'success.member_updated': 'Member updated successfully',
    'success.redemption_requested': 'Redemption request sent successfully',
    'success.redemption_approved': 'Redemption approved successfully',
    'success.redemption_delivered': 'Redemption marked as delivered',
    'success.redemption_rejected': 'Redemption rejected',
    'error.occurred': 'An error occurred',
    'error.insufficient_points': 'Insufficient points',
    'error.out_of_stock': 'Product out of stock',
    'levels.title': 'Levels',
    'levels.current': 'Current Level',
    'levels.next': 'Next Level',
    'levels.progress': 'Progress',
    'levels.bronze': 'Bronze',
    'levels.silver': 'Silver',
    'levels.gold': 'Gold',
    'levels.platinum': 'Platinum',
    'levels.points_to_next': 'Points to next',
    'badges.title': 'Badges',
    'badges.earned': 'Badges Earned',
    'badges.count': 'badges',
    'leaderboard.title': 'Leaderboard',
    'leaderboard.monthly': 'Monthly',
    'leaderboard.all_time': 'All Time',
    'leaderboard.rank': 'Rank',
    'leaderboard.points': 'Points',
    'leaderboard.level': 'Level',
    'leaderboard.member': 'Member',
    'leaderboard.top_3': 'Podium',
    'leaderboard.view_full': 'View Full Leaderboard',
    'welcome.title': 'Welcome to Amicale Anouar',
    'welcome.subtitle': 'Member Management Platform',
    'welcome.cta': 'Become a Member',
    'welcome.login': 'Admin Login'
  }
};

// I18n Provider
const I18nProvider = ({ children }) => {
  const [language, setLanguage] = useState('fr');
  
  const t = (key) => translations[language][key] || key;
  
  return (
    <I18nContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </I18nContext.Provider>
  );
};

// Auth Provider
const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      // You could verify token validity here
    }
  }, [token]);
  
  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, { email, password });
      const { access_token, user: userData } = response.data;
      
      setToken(access_token);
      setUser(userData);
      localStorage.setItem('token', access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      return true;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  };
  
  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
  };
  
  return (
    <AuthContext.Provider value={{ user, token, login, logout, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  );
};

// Language Switcher Component
const LanguageSwitcher = () => {
  const { language, setLanguage } = useI18n();
  
  return (
    <Select value={language} onValueChange={setLanguage}>
      <SelectTrigger className="w-20">
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="fr">FR</SelectItem>
        <SelectItem value="ar">AR</SelectItem>
        <SelectItem value="en">EN</SelectItem>
      </SelectContent>
    </Select>
  );
};

// Home/Landing Page
const HomePage = () => {
  const { t } = useI18n();
  const navigate = useNavigate();
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-teal-100">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-emerald-700">{t('app.title')}</h1>
            </div>
            <div className="flex items-center space-x-4">
              <LanguageSwitcher />
              <Button variant="outline" onClick={() => navigate('/login')}>
                {t('welcome.login')}
              </Button>
            </div>
          </div>
        </div>
      </header>
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">{t('welcome.title')}</h2>
          <p className="text-xl text-gray-600 mb-8">{t('welcome.subtitle')}</p>
          <div className="space-x-4">
            <Button size="lg" onClick={() => navigate('/register')} className="bg-emerald-600 hover:bg-emerald-700">
              <UserPlus className="mr-2 h-5 w-5" />
              {t('welcome.cta')}
            </Button>
          </div>
        </div>
        
        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
          <Card>
            <CardHeader>
              <Users className="h-8 w-8 text-emerald-600" />
              <CardTitle>Gestion des adhérents</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">Inscrivez-vous facilement et suivez votre adhésion</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CreditCard className="h-8 w-8 text-emerald-600" />
              <CardTitle>Suivi des paiements</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">Consultez vos paiements et votre solde restant</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <TrendingUp className="h-8 w-8 text-emerald-600" />
              <CardTitle>Rapports détaillés</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">Accédez aux statistiques et rapports de l'association</p>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
};

// Login Page
const LoginPage = () => {
  const { t } = useI18n();
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    const success = await login(email, password);
    if (success) {
      navigate('/dashboard');
      toast.success('Connexion réussie');
    } else {
      toast.error('Email ou mot de passe incorrect');
    }
    
    setLoading(false);
  };
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-teal-100 flex items-center justify-center">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-center">{t('auth.login')}</CardTitle>
          <CardDescription className="text-center">{t('app.title')}</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="email">{t('auth.email')}</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div>
              <Label htmlFor="password">{t('auth.password')}</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? 'Connexion...' : t('auth.login')}
            </Button>
          </form>
          
          <div className="mt-4 text-center">
            <Button variant="link" onClick={() => navigate('/')}>
              Retour à l'accueil
            </Button>
          </div>
          
          <div className="mt-6 text-sm text-gray-500 text-center">
            <p>Compte de démonstration:</p>
            <p>Email: admin@amicale.ma</p>
            <p>Mot de passe: admin123</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Member Registration Page
const MemberRegistrationPage = () => {
  const { t } = useI18n();
  const navigate = useNavigate();
  const [projectTypes, setProjectTypes] = useState([]);
  const [formData, setFormData] = useState({
    full_name: '',
    sex: '',
    phone: '',
    job: '',
    project_type_id: '',
    initial_paid: ''
  });
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    fetchProjectTypes();
  }, []);
  
  const fetchProjectTypes = async () => {
    try {
      const response = await axios.get(`${API}/project-types`);
      setProjectTypes(response.data);
    } catch (error) {
      console.error('Error fetching project types:', error);
    }
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await axios.post(`${API}/members/register`, {
        ...formData,
        initial_paid: parseFloat(formData.initial_paid) || 0
      });
      
      toast.success(t('success.member_registered'));
      navigate('/registration-success');
    } catch (error) {
      toast.error(t('error.occurred'));
      console.error('Registration error:', error);
    }
    
    setLoading(false);
  };
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-teal-100">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <h1 className="text-2xl font-bold text-emerald-700">{t('app.title')}</h1>
            <div className="flex items-center space-x-4">
              <LanguageSwitcher />
              <Button variant="outline" onClick={() => navigate('/')}>
                Accueil
              </Button>
            </div>
          </div>
        </div>
      </header>
      
      <main className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Card>
          <CardHeader>
            <CardTitle>{t('member.register')}</CardTitle>
            <CardDescription>Remplissez ce formulaire pour devenir adhérent</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="full_name">{t('member.full_name')} *</Label>
                <Input
                  id="full_name"
                  value={formData.full_name}
                  onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                  required
                />
              </div>
              
              <div>
                <Label htmlFor="sex">{t('member.sex')} *</Label>
                <Select value={formData.sex || undefined} onValueChange={(value) => setFormData({...formData, sex: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Sélectionnez" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Male">{t('sex.male')}</SelectItem>
                    <SelectItem value="Female">{t('sex.female')}</SelectItem>
                    <SelectItem value="Other">{t('sex.other')}</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label htmlFor="phone">{t('member.phone')} *</Label>
                <Input
                  id="phone"
                  value={formData.phone}
                  onChange={(e) => setFormData({...formData, phone: e.target.value})}
                  placeholder="+212612345678"
                  required
                />
              </div>
              
              <div>
                <Label htmlFor="job">{t('member.job')}</Label>
                <Input
                  id="job"
                  value={formData.job}
                  onChange={(e) => setFormData({...formData, job: e.target.value})}
                />
              </div>
              
              <div>
                <Label htmlFor="project_type">{t('member.project_type')} *</Label>
                <Select value={formData.project_type_id || undefined} onValueChange={(value) => setFormData({...formData, project_type_id: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Sélectionnez un type de projet" />
                  </SelectTrigger>
                  <SelectContent>
                    {projectTypes.map((pt) => (
                      <SelectItem key={pt.id} value={pt.id}>
                        {pt.name} ({pt.default_due} MAD)
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label htmlFor="initial_paid">{t('member.amount_paid')} (MAD)</Label>
                <Input
                  id="initial_paid"
                  type="number"
                  min="0"
                  step="0.01"
                  value={formData.initial_paid}
                  onChange={(e) => setFormData({...formData, initial_paid: e.target.value})}
                  placeholder="0.00"
                />
              </div>
              
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? 'Enregistrement...' : t('action.save')}
              </Button>
            </form>
          </CardContent>
        </Card>
      </main>
    </div>
  );
};

// Registration Success Page
const RegistrationSuccessPage = () => {
  const { t } = useI18n();
  const navigate = useNavigate();
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-teal-100 flex items-center justify-center">
      <Card className="w-full max-w-md text-center">
        <CardHeader>
          <CardTitle className="text-emerald-600">Inscription réussie !</CardTitle>
          <CardDescription>
            Votre adhésion a été enregistrée avec succès. Un administrateur examinera votre demande.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={() => navigate('/')} className="w-full">
            Retour à l'accueil
          </Button>
        </CardContent>
      </Card>
    </div>
  );
};

// Admin Layout
const AdminLayout = ({ children }) => {
  const { t } = useI18n();
  const { logout } = useAuth();
  const navigate = useNavigate();
  
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-emerald-700">{t('app.title')}</h1>
              <nav className="ml-10 flex space-x-8">
                <Link to="/dashboard" className="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium">
                  {t('nav.dashboard')}
                </Link>
                <Link to="/members" className="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium">
                  {t('nav.members')}
                </Link>
                <Link to="/payments" className="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium">
                  {t('nav.payments')}
                </Link>
                <Link to="/rewards" className="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium">
                  {t('rewards.title')}
                </Link>
                <Link to="/leaderboard" className="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium">
                  {t('leaderboard.title')}
                </Link>
                <Link to="/reports" className="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium">
                  {t('nav.reports')}
                </Link>
              </nav>
            </div>
            <div className="flex items-center space-x-4">
              <LanguageSwitcher />
              <Button variant="outline" size="sm" onClick={() => { logout(); navigate('/'); }}>
                <LogOut className="h-4 w-4 mr-2" />
                {t('auth.logout')}
              </Button>
            </div>
          </div>
        </div>
      </header>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
};

// Dashboard Page
const DashboardPage = () => {
  const { t } = useI18n();
  const [reports, setReports] = useState(null);
  const [recentMembers, setRecentMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchDashboardData();
  }, []);
  
  const fetchDashboardData = async () => {
    try {
      const [reportsResponse, membersResponse] = await Promise.all([
        axios.get(`${API}/reports/summary`),
        axios.get(`${API}/members?limit=5`)
      ]);
      
      setReports(reportsResponse.data);
      setRecentMembers(membersResponse.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      toast.error(t('error.occurred'));
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) {
    return (
      <AdminLayout>
        <div className="text-center py-12">Chargement...</div>
      </AdminLayout>
    );
  }
  
  return (
    <AdminLayout>
      <div className="space-y-8">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">{t('nav.dashboard')}</h2>
          <p className="text-gray-600">Vue d'ensemble de l'association</p>
        </div>
        
        {reports && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{t('reports.total_members')}</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{reports.total_members}</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{t('reports.active_members')}</CardTitle>
                <UserPlus className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{reports.active_members}</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{t('reports.total_collected')}</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{reports.total_collected.toFixed(2)} MAD</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{t('reports.total_outstanding')}</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{reports.total_outstanding.toFixed(2)} MAD</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{t('reports.total_points')}</CardTitle>
                <span className="text-yellow-500">⭐</span>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{reports.total_points_distributed || 0} pts</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{t('reports.average_points')}</CardTitle>
                <span className="text-emerald-500">📊</span>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{reports.average_points_per_member || 0} pts</div>
              </CardContent>
            </Card>
          </div>
        )}
        
        <Card>
          <CardHeader>
            <CardTitle>Adhérents récents</CardTitle>
            <CardDescription>Les derniers adhérents inscrits</CardDescription>
          </CardHeader>
          <CardContent>
            {recentMembers.length > 0 ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>{t('member.full_name')}</TableHead>
                    <TableHead>{t('member.phone')}</TableHead>
                    <TableHead>{t('member.project_type')}</TableHead>
                    <TableHead>{t('member.status')}</TableHead>
                    <TableHead>{t('member.balance')}</TableHead>
                    <TableHead>{t('member.points')}</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {recentMembers.map((member) => (
                    <TableRow key={member.id}>
                      <TableCell className="font-medium">{member.full_name}</TableCell>
                      <TableCell>{member.phone}</TableCell>
                      <TableCell>{member.project_type}</TableCell>
                      <TableCell>
                        <Badge variant={member.status === 'Active' ? 'default' : 'secondary'}>
                          {t(`status.${member.status.toLowerCase()}`)}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <span className={member.balance > 0 ? 'text-red-600' : 'text-green-600'}>
                          {member.balance.toFixed(2)} MAD
                        </span>
                      </TableCell>
                      <TableCell>
                        <span className="text-emerald-600 font-semibold">
                          {member.points || 0} pts
                        </span>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <p className="text-gray-500 text-center py-4">Aucun adhérent trouvé</p>
            )}
          </CardContent>
        </Card>
      </div>
    </AdminLayout>
  );
};

// Members Management Page
const MembersPage = () => {
  const { t } = useI18n();
  const [members, setMembers] = useState([]);
  const [projectTypes, setProjectTypes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [selectedMember, setSelectedMember] = useState(null);
  const [showMemberDialog, setShowMemberDialog] = useState(false);
  const [showPaymentDialog, setShowPaymentDialog] = useState(false);
  const [showPointsDialog, setShowPointsDialog] = useState(false);
  const [payments, setPayments] = useState([]);
  const [pointsHistory, setPointsHistory] = useState([]);
  const [memberLevel, setMemberLevel] = useState(null);
  const [memberBadges, setMemberBadges] = useState([]);
  
  useEffect(() => {
    fetchData();
  }, []);
  
  const fetchData = async () => {
    try {
      const [membersResponse, projectTypesResponse] = await Promise.all([
        axios.get(`${API}/members`),
        axios.get(`${API}/project-types`)
      ]);
      
      setMembers(membersResponse.data);
      setProjectTypes(projectTypesResponse.data);
    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error(t('error.occurred'));
    } finally {
      setLoading(false);
    }
  };
  
  const handleViewMember = async (member) => {
    setSelectedMember(member);
    
    try {
      const [paymentsResponse, pointsResponse, levelResponse, badgesResponse] = await Promise.all([
        axios.get(`${API}/members/${member.id}/payments`),
        axios.get(`${API}/members/${member.id}/points`),
        axios.get(`${API}/members/${member.id}/level`),
        axios.get(`${API}/members/${member.id}/badges`)
      ]);
      setPayments(paymentsResponse.data);
      setPointsHistory(pointsResponse.data);
      setMemberLevel(levelResponse.data);
      setMemberBadges(badgesResponse.data);
    } catch (error) {
      console.error('Error fetching member data:', error);
    }
    
    setShowMemberDialog(true);
  };
  
  const handleAddPayment = (member) => {
    setSelectedMember(member);
    setShowPaymentDialog(true);
  };
  
  const handleAddPoints = (member) => {
    setSelectedMember(member);
    setShowPointsDialog(true);
  };
  
  const filteredMembers = members.filter(member => {
    const matchesSearch = member.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         member.phone.includes(searchQuery);
    const matchesStatus = !statusFilter || statusFilter === 'all' || member.status === statusFilter;
    return matchesSearch && matchesStatus;
  });
  
  if (loading) {
    return (
      <AdminLayout>
        <div className="text-center py-12">Chargement...</div>
      </AdminLayout>
    );
  }
  
  return (
    <AdminLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-3xl font-bold text-gray-900">{t('nav.members')}</h2>
            <p className="text-gray-600">Gestion des adhérents</p>
          </div>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input
                placeholder={t('action.search')}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
          <Select value={statusFilter || undefined} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Filtrer par statut" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Tous les statuts</SelectItem>
              <SelectItem value="Pending">{t('status.pending')}</SelectItem>
              <SelectItem value="Active">{t('status.active')}</SelectItem>
              <SelectItem value="Inactive">{t('status.inactive')}</SelectItem>
            </SelectContent>
          </Select>
        </div>
        
        <Card>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>{t('member.full_name')}</TableHead>
                  <TableHead>{t('member.phone')}</TableHead>
                  <TableHead>{t('member.project_type')}</TableHead>
                  <TableHead>{t('member.status')}</TableHead>
                  <TableHead>{t('member.balance')}</TableHead>
                  <TableHead>{t('member.points')}</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredMembers.map((member) => (
                  <TableRow key={member.id}>
                    <TableCell className="font-medium">{member.full_name}</TableCell>
                    <TableCell>{member.phone}</TableCell>
                    <TableCell>{member.project_type}</TableCell>
                    <TableCell>
                      <Badge variant={member.status === 'Active' ? 'default' : 'secondary'}>
                        {t(`status.${member.status.toLowerCase()}`)}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <span className={member.balance > 0 ? 'text-red-600' : 'text-green-600'}>
                        {member.balance.toFixed(2)} MAD
                      </span>
                    </TableCell>
                    <TableCell>
                      <span className="text-emerald-600 font-semibold">
                        {member.points || 0} pts
                      </span>
                    </TableCell>
                    <TableCell>
                      <div className="flex space-x-2">
                        <Button size="sm" variant="outline" onClick={() => handleViewMember(member)}>
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button size="sm" onClick={() => handleAddPayment(member)}>
                          <Plus className="h-4 w-4" />
                        </Button>
                        <Button size="sm" variant="outline" onClick={() => handleAddPoints(member)}>
                          ⭐
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
        
        {/* Member Details Dialog */}
        <MemberDetailsDialog
          member={selectedMember}
          payments={payments}
          pointsHistory={pointsHistory}
          open={showMemberDialog}
          onOpenChange={setShowMemberDialog}
          onRefresh={fetchData}
        />
        
        {/* Add Payment Dialog */}
        <AddPaymentDialog
          member={selectedMember}
          open={showPaymentDialog}
          onOpenChange={setShowPaymentDialog}
          onSuccess={() => {
            fetchData();
            setShowPaymentDialog(false);
          }}
        />
        
        {/* Add Points Dialog */}
        <AddPointsDialog
          member={selectedMember}
          open={showPointsDialog}
          onOpenChange={setShowPointsDialog}
          onSuccess={() => {
            fetchData();
            setShowPointsDialog(false);
          }}
        />
      </div>
    </AdminLayout>
  );
};

// Member Details Dialog Component
const MemberDetailsDialog = ({ member, payments, pointsHistory, open, onOpenChange, onRefresh }) => {
  const { t } = useI18n();
  
  if (!member) return null;
  
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Détails de l'adhérent</DialogTitle>
        </DialogHeader>
        
        <Tabs defaultValue="details" className="w-full">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="details">Infos</TabsTrigger>
            <TabsTrigger value="level">Niveau</TabsTrigger>
            <TabsTrigger value="badges">Badges</TabsTrigger>
            <TabsTrigger value="payments">Paiements</TabsTrigger>
            <TabsTrigger value="points">Points</TabsTrigger>
          </TabsList>
          
          <TabsContent value="details" className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Nom complet</Label>
                <p className="text-sm text-gray-600">{member.full_name}</p>
              </div>
              <div>
                <Label>Téléphone</Label>
                <p className="text-sm text-gray-600">{member.phone}</p>
              </div>
              <div>
                <Label>Sexe</Label>
                <p className="text-sm text-gray-600">{t(`sex.${member.sex.toLowerCase()}`)}</p>
              </div>
              <div>
                <Label>Profession</Label>
                <p className="text-sm text-gray-600">{member.job || 'Non spécifiée'}</p>
              </div>
              <div>
                <Label>Type de projet</Label>
                <p className="text-sm text-gray-600">{member.project_type}</p>
              </div>
              <div>
                <Label>Statut</Label>
                <Badge variant={member.status === 'Active' ? 'default' : 'secondary'}>
                  {t(`status.${member.status.toLowerCase()}`)}
                </Badge>
              </div>
              <div>
                <Label>Total dû</Label>
                <p className="text-sm font-semibold">{member.total_due.toFixed(2)} MAD</p>
              </div>
              <div>
                <Label>Montant payé</Label>
                <p className="text-sm font-semibold text-green-600">{member.amount_paid.toFixed(2)} MAD</p>
              </div>
              <div>
                <Label>Reste à payer</Label>
                <p className={`text-sm font-semibold ${member.balance > 0 ? 'text-red-600' : 'text-green-600'}`}>
                  {member.balance.toFixed(2)} MAD
                </p>
              </div>
              <div>
                <Label>Points cumulés</Label>
                <p className="text-sm font-semibold text-emerald-600">
                  {member.points || 0} points
                </p>
              </div>
              <div>
                <Label>Date d'adhésion</Label>
                <p className="text-sm text-gray-600">
                  {new Date(member.join_date).toLocaleDateString('fr-FR')}
                </p>
              </div>
            </div>
            
            {member.notes && (
              <div>
                <Label>Notes</Label>
                <p className="text-sm text-gray-600">{member.notes}</p>
              </div>
            )}
          </TabsContent>
          
          <TabsContent value="payments">
            {payments.length > 0 ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Date</TableHead>
                    <TableHead>Montant</TableHead>
                    <TableHead>Méthode</TableHead>
                    <TableHead>Note</TableHead>
                    <TableHead>Enregistré par</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {payments.map((payment) => (
                    <TableRow key={payment.id}>
                      <TableCell>
                        {new Date(payment.date).toLocaleDateString('fr-FR')}
                      </TableCell>
                      <TableCell className="font-semibold">
                        {payment.amount.toFixed(2)} MAD
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">
                          {t(`method.${payment.method.toLowerCase()}`)}
                        </Badge>
                      </TableCell>
                      <TableCell>{payment.note || '-'}</TableCell>
                      <TableCell>{payment.recorded_by_name}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <p className="text-center text-gray-500 py-8">Aucun paiement enregistré</p>
            )}
          </TabsContent>
          
          <TabsContent value="points">
            {pointsHistory.length > 0 ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Date</TableHead>
                    <TableHead>Points</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Description</TableHead>
                    <TableHead>Enregistré par</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {pointsHistory.map((transaction) => (
                    <TableRow key={transaction.id}>
                      <TableCell>
                        {new Date(transaction.date).toLocaleDateString('fr-FR')}
                      </TableCell>
                      <TableCell className={`font-semibold ${transaction.points > 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {transaction.points > 0 ? '+' : ''}{transaction.points} pts
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">
                          {transaction.transaction_type}
                        </Badge>
                      </TableCell>
                      <TableCell>{transaction.description}</TableCell>
                      <TableCell>{transaction.recorded_by_name}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <p className="text-center text-gray-500 py-8">Aucune transaction de points</p>
            )}
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
};

// Add Points Dialog Component
const AddPointsDialog = ({ member, open, onOpenChange, onSuccess }) => {
  const { t } = useI18n();
  const [formData, setFormData] = useState({
    points: '',
    transaction_type: 'manual',
    description: ''
  });
  const [loading, setLoading] = useState(false);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await axios.post(`${API}/members/${member.id}/points`, {
        points: parseInt(formData.points),
        transaction_type: formData.transaction_type,
        description: formData.description
      });
      
      toast.success('Points ajoutés avec succès');
      setFormData({ points: '', transaction_type: 'manual', description: '' });
      onSuccess();
    } catch (error) {
      toast.error(t('error.occurred'));
      console.error('Points error:', error);
    } finally {
      setLoading(false);
    }
  };
  
  if (!member) return null;
  
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Ajouter des points</DialogTitle>
          <p className="text-sm text-gray-600">
            Adhérent: {member.full_name} | Points actuels: {member.points || 0}
          </p>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="points">Nombre de points *</Label>
            <Input
              id="points"
              type="number"
              value={formData.points}
              onChange={(e) => setFormData({...formData, points: e.target.value})}
              placeholder="Entrez le nombre de points (positif ou négatif)"
              required
            />
          </div>
          
          <div>
            <Label htmlFor="transaction_type">Type de transaction *</Label>
            <Select value={formData.transaction_type || undefined} onValueChange={(value) => setFormData({...formData, transaction_type: value})}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="manual">Attribution manuelle</SelectItem>
                <SelectItem value="bonus">Bonus</SelectItem>
                <SelectItem value="deduction">Déduction</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <div>
            <Label htmlFor="description">Description *</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              placeholder="Raison de l'attribution des points"
              required
            />
          </div>
          
          <div className="flex justify-end space-x-2">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              {t('action.cancel')}
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Ajout...' : t('action.save')}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

// Add Payment Dialog Component
const AddPaymentDialog = ({ member, open, onOpenChange, onSuccess }) => {
  const { t } = useI18n();
  const [formData, setFormData] = useState({
    amount: '',
    method: 'Cash',
    note: ''
  });
  const [loading, setLoading] = useState(false);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await axios.post(`${API}/members/${member.id}/payments`, {
        amount: parseFloat(formData.amount),
        method: formData.method,
        note: formData.note
      });
      
      toast.success(t('success.payment_added'));
      setFormData({ amount: '', method: 'Cash', note: '' });
      onSuccess();
    } catch (error) {
      toast.error(t('error.occurred'));
      console.error('Payment error:', error);
    } finally {
      setLoading(false);
    }
  };
  
  if (!member) return null;
  
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Ajouter un paiement</DialogTitle>
          <p className="text-sm text-gray-600">
            Adhérent: {member.full_name} | Balance: {member.balance.toFixed(2)} MAD
          </p>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="amount">Montant (MAD) *</Label>
            <Input
              id="amount"
              type="number"
              min="0"
              step="0.01"
              value={formData.amount}
              onChange={(e) => setFormData({...formData, amount: e.target.value})}
              required
            />
          </div>
          
          <div>
            <Label htmlFor="method">Méthode de paiement *</Label>
            <Select value={formData.method || undefined} onValueChange={(value) => setFormData({...formData, method: value})}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Cash">{t('method.cash')}</SelectItem>
                <SelectItem value="Bank">{t('method.bank')}</SelectItem>
                <SelectItem value="Mobile">{t('method.mobile')}</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <div>
            <Label htmlFor="note">Note</Label>
            <Textarea
              id="note"
              value={formData.note}
              onChange={(e) => setFormData({...formData, note: e.target.value})}
              placeholder="Note optionnelle"
            />
          </div>
          
          <div className="flex justify-end space-x-2">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              {t('action.cancel')}
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Ajout...' : t('action.save')}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

// Rewards Catalog Page
const RewardsPage = () => {
  const { t } = useI18n();
  const [rewards, setRewards] = useState([]);
  const [redemptions, setRedemptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [selectedReward, setSelectedReward] = useState(null);
  const [showRedemptionDialog, setShowRedemptionDialog] = useState(false);
  const [showRedemptionsHistory, setShowRedemptionsHistory] = useState(false);
  
  useEffect(() => {
    fetchData();
  }, []);
  
  const fetchData = async () => {
    try {
      // Always fetch rewards (public endpoint)
      const rewardsResponse = await axios.get(`${API}/rewards?active=true`);
      setRewards(rewardsResponse.data);
      
      // Try to fetch redemptions (admin endpoint)
      try {
        const redemptionsResponse = await axios.get(`${API}/redemptions`);
        setRedemptions(redemptionsResponse.data);
      } catch (redemptionError) {
        // If user doesn't have permission for redemptions, that's okay
        console.log('No permission for redemptions or no redemptions available');
        setRedemptions([]);
      }
    } catch (error) {
      console.error('Error fetching rewards data:', error);
      toast.error(t('error.occurred'));
    } finally {
      setLoading(false);
    }
  };
  
  const handleRedeemReward = (reward) => {
    setSelectedReward(reward);
    setShowRedemptionDialog(true);
  };
  
  const filteredRewards = rewards.filter(reward => {
    if (!selectedCategory || selectedCategory === 'ALL') return true;
    return reward.category === selectedCategory;
  });
  
  const categories = [
    { value: 'ALL', label: 'Toutes' },
    { value: 'Materiel', label: t('rewards.category.materiel') },
    { value: 'Services', label: t('rewards.category.services') },
    { value: 'Reductions', label: t('rewards.category.reductions') },
    { value: 'Privileges', label: t('rewards.category.privileges') }
  ];
  
  if (loading) {
    return (
      <AdminLayout>
        <div className="text-center py-12">Chargement...</div>
      </AdminLayout>
    );
  }
  
  return (
    <AdminLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-3xl font-bold text-gray-900">{t('rewards.catalog')}</h2>
            <p className="text-gray-600">Échangez vos points contre des récompenses</p>
          </div>
          <Button 
            variant="outline" 
            onClick={() => setShowRedemptionsHistory(true)}
            className="flex items-center gap-2"
          >
            <ShoppingCart className="h-4 w-4" />
            {t('redemptions.history')}
          </Button>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-4">
          <Select value={selectedCategory} onValueChange={setSelectedCategory}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Filtrer par catégorie" />
            </SelectTrigger>
            <SelectContent>
              {categories.map((category) => (
                <SelectItem key={category.value} value={category.value}>
                  {category.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredRewards.map((reward) => (
            <RewardCard 
              key={reward.id} 
              reward={reward} 
              onRedeem={handleRedeemReward}
              t={t}
            />
          ))}
        </div>
        
        {filteredRewards.length === 0 && (
          <div className="text-center py-12">
            <Gift className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">Aucune récompense disponible pour cette catégorie</p>
          </div>
        )}
        
        {/* Redemption Request Dialog */}
        <RedemptionRequestDialog
          reward={selectedReward}
          open={showRedemptionDialog}
          onOpenChange={setShowRedemptionDialog}
          onSuccess={() => {
            fetchData();
            setShowRedemptionDialog(false);
          }}
        />
        
        {/* Redemptions History Dialog */}
        <RedemptionsHistoryDialog
          redemptions={redemptions}
          open={showRedemptionsHistory}
          onOpenChange={setShowRedemptionsHistory}
          onRefresh={fetchData}
        />
      </div>
    </AdminLayout>
  );
};

// Reward Card Component
const RewardCard = ({ reward, onRedeem, t }) => {
  const isOutOfStock = reward.stock <= 0;
  const isLowStock = reward.stock <= 5 && reward.stock > 0;
  
  return (
    <Card className="overflow-hidden hover:shadow-lg transition-shadow duration-200">
      <div className="aspect-video relative">
        {reward.image_url ? (
          <img 
            src={reward.image_url} 
            alt={reward.name}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full bg-gradient-to-br from-emerald-100 to-teal-100 flex items-center justify-center">
            <Gift className="h-12 w-12 text-emerald-600" />
          </div>
        )}
        
        {isOutOfStock && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
            <Badge variant="destructive">{t('rewards.out_of_stock')}</Badge>
          </div>
        )}
        
        {isLowStock && (
          <div className="absolute top-2 right-2">
            <Badge variant="outline" className="bg-orange-100 text-orange-800">
              {t('rewards.low_stock')}
            </Badge>
          </div>
        )}
      </div>
      
      <CardContent className="p-4">
        <div className="space-y-2">
          <div className="flex items-start justify-between">
            <h3 className="font-semibold text-lg line-clamp-2">{reward.name}</h3>
            <Badge variant="outline" className="ml-2 shrink-0">
              {t(`rewards.category.${reward.category.toLowerCase()}`)}
            </Badge>
          </div>
          
          {reward.description && (
            <p className="text-sm text-gray-600 line-clamp-2">{reward.description}</p>
          )}
          
          <div className="flex items-center justify-between pt-2">
            <div className="flex items-center gap-1">
              <Award className="h-4 w-4 text-emerald-600" />
              <span className="font-bold text-emerald-600">{reward.cost_points} pts</span>
            </div>
            <span className="text-sm text-gray-500">Stock: {reward.stock}</span>
          </div>
          
          <Button 
            onClick={() => onRedeem(reward)}
            disabled={isOutOfStock}
            className="w-full mt-3"
            variant={isOutOfStock ? "outline" : "default"}
          >
            <Gift className="h-4 w-4 mr-2" />
            {isOutOfStock ? t('rewards.out_of_stock') : t('rewards.redeem')}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

// Redemption Request Dialog
const RedemptionRequestDialog = ({ reward, open, onOpenChange, onSuccess }) => {
  const { t } = useI18n();
  const [note, setNote] = useState('');
  const [loading, setLoading] = useState(false);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!reward) return;
    
    setLoading(true);
    
    try {
      // For demo, we'll use the first member (in real app, this would be current user's member profile)
      const membersResponse = await axios.get(`${API}/members`);
      const members = membersResponse.data;
      
      if (members.length === 0) {
        toast.error('Aucun membre trouvé');
        return;
      }
      
      const firstMember = members[0]; // Demo: use first member
      
      await axios.post(`${API}/members/${firstMember.id}/redemptions`, {
        reward_id: reward.id,
        note: note
      });
      
      toast.success(t('success.redemption_requested'));
      setNote('');
      onSuccess();
    } catch (error) {
      console.error('Redemption request error:', error);
      if (error.response?.data?.detail?.includes('points')) {
        toast.error(t('error.insufficient_points'));
      } else if (error.response?.data?.detail?.includes('stock')) {
        toast.error(t('error.out_of_stock'));
      } else {
        toast.error(t('error.occurred'));
      }
    } finally {
      setLoading(false);
    }
  };
  
  if (!reward) return null;
  
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{t('redemptions.request')}</DialogTitle>
          <p className="text-sm text-gray-600">
            {reward.name} - {reward.cost_points} points
          </p>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="flex items-center space-x-4 p-4 bg-gray-50 rounded-lg">
            {reward.image_url ? (
              <img 
                src={reward.image_url} 
                alt={reward.name}
                className="w-16 h-16 object-cover rounded"
              />
            ) : (
              <div className="w-16 h-16 bg-emerald-100 rounded flex items-center justify-center">
                <Gift className="h-8 w-8 text-emerald-600" />
              </div>
            )}
            <div className="flex-1">
              <h3 className="font-semibold">{reward.name}</h3>
              <p className="text-sm text-gray-600">{reward.description}</p>
              <div className="flex items-center gap-4 mt-1">
                <span className="text-emerald-600 font-semibold">{reward.cost_points} pts</span>
                <span className="text-sm text-gray-500">Stock: {reward.stock}</span>
              </div>
            </div>
          </div>
          
          <div>
            <Label htmlFor="note">{t('redemptions.note')}</Label>
            <Textarea
              id="note"
              value={note}
              onChange={(e) => setNote(e.target.value)}
              placeholder="Ajoutez une note pour votre demande..."
              rows={3}
            />
          </div>
          
          <div className="flex justify-end space-x-2">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              {t('action.cancel')}
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Demande...' : t('redemptions.request')}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

// Redemptions History Dialog
const RedemptionsHistoryDialog = ({ redemptions, open, onOpenChange, onRefresh }) => {
  const { t } = useI18n();
  
  const getStatusColor = (status) => {
    switch (status) {
      case 'Pending': return 'bg-yellow-100 text-yellow-800';
      case 'Approved': return 'bg-blue-100 text-blue-800';
      case 'Delivered': return 'bg-green-100 text-green-800';
      case 'Rejected': return 'bg-red-100 text-red-800';
      case 'Canceled': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };
  
  const handleApprove = async (redemptionId) => {
    try {
      await axios.put(`${API}/redemptions/${redemptionId}/approve`, {});
      toast.success(t('success.redemption_approved'));
      onRefresh();
    } catch (error) {
      console.error('Approve error:', error);
      toast.error(t('error.occurred'));
    }
  };
  
  const handleDeliver = async (redemptionId) => {
    try {
      await axios.put(`${API}/redemptions/${redemptionId}/deliver`, {});
      toast.success(t('success.redemption_delivered'));
      onRefresh();
    } catch (error) {
      console.error('Deliver error:', error);
      toast.error(t('error.occurred'));
    }
  };
  
  const handleReject = async (redemptionId) => {
    try {
      await axios.put(`${API}/redemptions/${redemptionId}/reject`, {
        note: "Rejeté par l'administrateur"
      });
      toast.success(t('success.redemption_rejected'));
      onRefresh();
    } catch (error) {
      console.error('Reject error:', error);
      toast.error(t('error.occurred'));
    }
  };
  
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{t('redemptions.history')}</DialogTitle>
        </DialogHeader>
        
        {redemptions.length > 0 ? (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t('redemptions.date')}</TableHead>
                <TableHead>Membre</TableHead>
                <TableHead>Récompense</TableHead>
                <TableHead>Points</TableHead>
                <TableHead>{t('redemptions.status')}</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {redemptions.map((redemption) => (
                <TableRow key={redemption.id}>
                  <TableCell>
                    {new Date(redemption.created_at).toLocaleDateString('fr-FR')}
                  </TableCell>
                  <TableCell className="font-medium">{redemption.member_name}</TableCell>
                  <TableCell>{redemption.reward_name}</TableCell>
                  <TableCell className="font-semibold text-emerald-600">
                    {redemption.points_cost} pts
                  </TableCell>
                  <TableCell>
                    <Badge className={getStatusColor(redemption.status)}>
                      {t(`redemptions.status.${redemption.status.toLowerCase()}`)}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex space-x-1">
                      {redemption.status === 'Pending' && (
                        <>
                          <Button 
                            size="sm" 
                            onClick={() => handleApprove(redemption.id)}
                            className="bg-green-600 hover:bg-green-700"
                          >
                            Approuver
                          </Button>
                          <Button 
                            size="sm" 
                            variant="destructive" 
                            onClick={() => handleReject(redemption.id)}
                          >
                            Rejeter
                          </Button>
                        </>
                      )}
                      {redemption.status === 'Approved' && (
                        <Button 
                          size="sm" 
                          onClick={() => handleDeliver(redemption.id)}
                          className="bg-blue-600 hover:bg-blue-700"
                        >
                          Livrer
                        </Button>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        ) : (
          <div className="text-center py-8">
            <ShoppingCart className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">Aucun échange enregistré</p>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
};

// Leaderboard Page
const LeaderboardPage = () => {
  const { t } = useI18n();
  const [leaderboard, setLeaderboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState('all_time');
  const [selectedMonth, setSelectedMonth] = useState('');
  
  useEffect(() => {
    fetchLeaderboard();
  }, [selectedPeriod]);
  
  const fetchLeaderboard = async () => {
    setLoading(true);
    try {
      let period = selectedPeriod;
      if (selectedPeriod === 'monthly' && selectedMonth) {
        period = `monthly:${selectedMonth}`;
      }
      
      const response = await axios.get(`${API}/leaderboard?period=${period}&limit=50`);
      setLeaderboard(response.data);
    } catch (error) {
      console.error('Error fetching leaderboard:', error);
      toast.error(t('error.occurred'));
    } finally {
      setLoading(false);
    }
  };
  
  const handlePeriodChange = (period) => {
    setSelectedPeriod(period);
    if (period === 'monthly' && !selectedMonth) {
      const currentDate = new Date();
      setSelectedMonth(`${currentDate.getFullYear()}-${(currentDate.getMonth() + 1).toString().padStart(2, '0')}`);
    }
  };
  
  const getLevelIcon = (levelName) => {
    switch (levelName?.toLowerCase()) {
      case 'bronze': return <Medal className="h-5 w-5 text-orange-600" />;
      case 'argent': 
      case 'silver': return <Medal className="h-5 w-5 text-gray-400" />;
      case 'or':
      case 'gold': return <Medal className="h-5 w-5 text-yellow-500" />;
      case 'platine':
      case 'platinum': return <Crown className="h-5 w-5 text-purple-600" />;
      default: return <Medal className="h-5 w-5 text-gray-400" />;
    }
  };
  
  const getRankIcon = (rank) => {
    switch (rank) {
      case 1: return <Trophy className="h-6 w-6 text-yellow-500" />;
      case 2: return <Medal className="h-6 w-6 text-gray-400" />;
      case 3: return <Medal className="h-6 w-6 text-orange-600" />;
      default: return <span className="text-lg font-bold text-gray-600">#{rank}</span>;
    }
  };
  
  if (loading) {
    return (
      <AdminLayout>
        <div className="text-center py-12">Chargement du classement...</div>
      </AdminLayout>
    );
  }
  
  return (
    <AdminLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-3xl font-bold text-gray-900">{t('leaderboard.title')}</h2>
            <p className="text-gray-600">Découvrez les membres les plus actifs</p>
          </div>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex gap-2">
            <Button 
              variant={selectedPeriod === 'all_time' ? 'default' : 'outline'}
              onClick={() => handlePeriodChange('all_time')}
            >
              {t('leaderboard.all_time')}
            </Button>
            <Button 
              variant={selectedPeriod === 'monthly' ? 'default' : 'outline'}
              onClick={() => handlePeriodChange('monthly')}
            >
              {t('leaderboard.monthly')}
            </Button>
          </div>
          
          {selectedPeriod === 'monthly' && (
            <div className="flex items-center gap-2">
              <Input
                type="month"
                value={selectedMonth}
                onChange={(e) => setSelectedMonth(e.target.value)}
                className="w-40"
              />
              <Button onClick={fetchLeaderboard} size="sm">
                Actualiser
              </Button>
            </div>
          )}
        </div>
        
        {leaderboard && leaderboard.entries.length > 0 ? (
          <div className="space-y-6">
            {/* Podium Top 3 */}
            {leaderboard.entries.length >= 3 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Trophy className="h-5 w-5 text-yellow-500" />
                    {t('leaderboard.top_3')}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {leaderboard.entries.slice(0, 3).map((entry, index) => (
                      <div key={entry.member_id} className={`text-center p-6 rounded-lg ${
                        index === 0 ? 'bg-gradient-to-br from-yellow-50 to-yellow-100 border-yellow-200' :
                        index === 1 ? 'bg-gradient-to-br from-gray-50 to-gray-100 border-gray-200' :
                        'bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200'
                      } border-2`}>
                        <div className="mb-3">
                          {getRankIcon(entry.rank)}
                        </div>
                        <h3 className="font-bold text-lg mb-2">{entry.member_name}</h3>
                        <div className="flex items-center justify-center gap-2 mb-2">
                          {getLevelIcon(entry.level_name)}
                          <span className="text-sm font-medium">{entry.level_name}</span>
                        </div>
                        <p className="text-2xl font-bold text-emerald-600">{entry.points} pts</p>
                        {entry.badge_count > 0 && (
                          <p className="text-sm text-gray-600 mt-1">
                            {entry.badge_count} {t('badges.count')}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
            
            {/* Full Leaderboard Table */}
            <Card>
              <CardHeader>
                <CardTitle>Classement complet</CardTitle>
                <CardDescription>
                  {leaderboard.total_entries} membres • 
                  Généré le {new Date(leaderboard.generated_at).toLocaleDateString('fr-FR')}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-16">{t('leaderboard.rank')}</TableHead>
                      <TableHead>{t('leaderboard.member')}</TableHead>
                      <TableHead>{t('leaderboard.level')}</TableHead>
                      <TableHead>{t('leaderboard.points')}</TableHead>
                      <TableHead>Badges</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {leaderboard.entries.map((entry) => (
                      <TableRow key={entry.member_id}>
                        <TableCell className="font-medium">
                          {entry.rank <= 3 ? getRankIcon(entry.rank) : `#${entry.rank}`}
                        </TableCell>
                        <TableCell className="font-medium">{entry.member_name}</TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            {getLevelIcon(entry.level_name)}
                            <span className="text-sm">{entry.level_name}</span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <span className="font-semibold text-emerald-600">{entry.points} pts</span>
                        </TableCell>
                        <TableCell>
                          {entry.badge_count > 0 ? (
                            <Badge variant="outline">
                              <Star className="h-3 w-3 mr-1" />
                              {entry.badge_count}
                            </Badge>
                          ) : (
                            <span className="text-gray-400">-</span>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </div>
        ) : (
          <div className="text-center py-12">
            <Trophy className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">Aucun classement disponible pour cette période</p>
          </div>
        )}
      </div>
    </AdminLayout>
  );
};

// Member Level Component
const MemberLevelCard = ({ memberLevel, t }) => {
  if (!memberLevel || !memberLevel.current_level) {
    return null;
  }
  
  const getLevelColor = (levelName) => {
    switch (levelName?.toLowerCase()) {
      case 'bronze': return 'from-orange-100 to-orange-200 border-orange-300';
      case 'argent': 
      case 'silver': return 'from-gray-100 to-gray-200 border-gray-300';
      case 'or':
      case 'gold': return 'from-yellow-100 to-yellow-200 border-yellow-300';
      case 'platine':
      case 'platinum': return 'from-purple-100 to-purple-200 border-purple-300';
      default: return 'from-gray-100 to-gray-200 border-gray-300';
    }
  };
  
  const getLevelIcon = (levelName) => {
    switch (levelName?.toLowerCase()) {
      case 'bronze': return <Medal className="h-6 w-6 text-orange-600" />;
      case 'argent':
      case 'silver': return <Medal className="h-6 w-6 text-gray-500" />;
      case 'or':
      case 'gold': return <Crown className="h-6 w-6 text-yellow-600" />;
      case 'platine':
      case 'platinum': return <Crown className="h-6 w-6 text-purple-600" />;
      default: return <Medal className="h-6 w-6 text-gray-400" />;
    }
  };
  
  return (
    <Card className={`bg-gradient-to-r ${getLevelColor(memberLevel.current_level.name)} border-2`}>
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            {getLevelIcon(memberLevel.current_level.name)}
            <div>
              <h3 className="font-bold text-lg">{t('levels.current')}</h3>
              <p className="text-lg font-semibold">{memberLevel.current_level.name}</p>
            </div>
          </div>
          {memberLevel.next_level && (
            <div className="text-right">
              <p className="text-sm text-gray-600">{t('levels.next')}</p>
              <p className="font-medium">{memberLevel.next_level.name}</p>
            </div>
          )}
        </div>
        
        {memberLevel.next_level && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>{t('levels.progress')}</span>
              <span>{memberLevel.progress_percentage}%</span>
            </div>
            <div className="w-full bg-white rounded-full h-2">
              <div 
                className="bg-emerald-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${memberLevel.progress_percentage}%` }}
              ></div>
            </div>
            <p className="text-sm text-gray-600 text-center">
              {memberLevel.points_to_next} {t('levels.points_to_next')}
            </p>
          </div>
        )}
        
        {memberLevel.current_level.benefits && (
          <div className="mt-4 p-3 bg-white bg-opacity-50 rounded-lg">
            <p className="text-sm text-gray-700">{memberLevel.current_level.benefits}</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// Member Badges Component
const MemberBadgesCard = ({ badges, t }) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Star className="h-5 w-5 text-yellow-500" />
          {t('badges.earned')} ({badges.length})
        </CardTitle>
      </CardHeader>
      <CardContent>
        {badges.length > 0 ? (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {badges.map((badge) => (
              <div key={badge.id} className="text-center p-4 bg-gray-50 rounded-lg">
                {badge.image_url ? (
                  <img 
                    src={badge.image_url} 
                    alt={badge.badge_name}
                    className="w-12 h-12 mx-auto mb-2 rounded-full object-cover"
                  />
                ) : (
                  <div className="w-12 h-12 mx-auto mb-2 bg-emerald-100 rounded-full flex items-center justify-center">
                    <Star className="h-6 w-6 text-emerald-600" />
                  </div>
                )}
                <h4 className="font-semibold text-sm">{badge.badge_name}</h4>
                <p className="text-xs text-gray-500 mt-1">
                  {new Date(badge.awarded_at).toLocaleDateString('fr-FR')}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <Star className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">Aucun badge obtenu pour le moment</p>
            <p className="text-sm text-gray-400 mt-1">Continuez à participer pour débloquer des badges !</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

// Main App Component
function App() {
  return (
    <I18nProvider>
      <AuthProvider>
        <BrowserRouter>
          <div className="App">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<MemberRegistrationPage />} />
              <Route path="/registration-success" element={<RegistrationSuccessPage />} />
              
              <Route path="/dashboard" element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              } />
              
              <Route path="/members" element={
                <ProtectedRoute>
                  <MembersPage />
                </ProtectedRoute>
              } />
              
              <Route path="/payments" element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              } />
              
              <Route path="/rewards" element={
                <ProtectedRoute>
                  <RewardsPage />
                </ProtectedRoute>
              } />
              
              <Route path="/reports" element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              } />
            </Routes>
            <Toaster position="top-right" />
          </div>
        </BrowserRouter>
      </AuthProvider>
    </I18nProvider>
  );
}

export default App;