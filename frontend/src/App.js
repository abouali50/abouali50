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
import { Users, CreditCard, TrendingUp, UserPlus, Settings, Globe, LogOut, Plus, Search, Filter, Eye, Edit, DollarSign } from 'lucide-react';
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
    'payment.add': 'Ajouter un paiement',
    'payment.amount': 'Montant',
    'payment.method': 'Méthode',
    'payment.note': 'Note',
    'payment.date': 'Date',
    'payment.recorded_by': 'Enregistré par',
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
    'success.member_registered': 'Adhérent enregistré avec succès',
    'success.payment_added': 'Paiement ajouté avec succès',
    'success.member_updated': 'Adhérent mis à jour avec succès',
    'error.occurred': 'Une erreur s\'est produite',
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
    'payment.add': 'إضافة دفعة',
    'payment.amount': 'المبلغ',
    'payment.method': 'الطريقة',
    'payment.note': 'ملاحظة',
    'payment.date': 'التاريخ',
    'payment.recorded_by': 'سجل بواسطة',
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
    'success.member_registered': 'تم تسجيل العضو بنجاح',
    'success.payment_added': 'تم إضافة الدفعة بنجاح',
    'success.member_updated': 'تم تحديث العضو بنجاح',
    'error.occurred': 'حدث خطأ',
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
    'payment.add': 'Add Payment',
    'payment.amount': 'Amount',
    'payment.method': 'Method',
    'payment.note': 'Note',
    'payment.date': 'Date',
    'payment.recorded_by': 'Recorded By',
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
    'success.member_registered': 'Member registered successfully',
    'success.payment_added': 'Payment added successfully',
    'success.member_updated': 'Member updated successfully',
    'error.occurred': 'An error occurred',
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
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
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
  const [payments, setPayments] = useState([]);
  
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
      const paymentsResponse = await axios.get(`${API}/members/${member.id}/payments`);
      setPayments(paymentsResponse.data);
    } catch (error) {
      console.error('Error fetching payments:', error);
    }
    
    setShowMemberDialog(true);
  };
  
  const handleAddPayment = (member) => {
    setSelectedMember(member);
    setShowPaymentDialog(true);
  };
  
  const filteredMembers = members.filter(member => {
    const matchesSearch = member.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         member.phone.includes(searchQuery);
    const matchesStatus = !statusFilter || member.status === statusFilter;
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
                      <div className="flex space-x-2">
                        <Button size="sm" variant="outline" onClick={() => handleViewMember(member)}>
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button size="sm" onClick={() => handleAddPayment(member)}>
                          <Plus className="h-4 w-4" />
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
      </div>
    </AdminLayout>
  );
};

// Member Details Dialog Component
const MemberDetailsDialog = ({ member, payments, open, onOpenChange, onRefresh }) => {
  const { t } = useI18n();
  
  if (!member) return null;
  
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Détails de l'adhérent</DialogTitle>
        </DialogHeader>
        
        <Tabs defaultValue="details" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="details">Informations</TabsTrigger>
            <TabsTrigger value="payments">Paiements</TabsTrigger>
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
        </Tabs>
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
            <Select value={formData.method} onValueChange={(value) => setFormData({...formData, method: value})}>
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