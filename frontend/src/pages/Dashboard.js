import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { 
  BookOpen, 
  Users, 
  BookMarked, 
  AlertTriangle, 
  TrendingUp, 
  Calendar,
  Clock,
  CheckCircle
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = () => {
  const { user, isAdmin, isLibrarian, isTeacher, isStudent } = useAuth();
  const [stats, setStats] = useState(null);
  const [recentActivity, setRecentActivity] = useState([]);
  const [myLoans, setMyLoans] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const promises = [];
      
      // Load general stats for admin/librarian
      if (isAdmin() || isLibrarian()) {
        promises.push(
          axios.get(`${API}/books/`).then(res => res.data),
          axios.get(`${API}/loans/`).then(res => res.data)
        );
      }
      
      // Load personal loans for all users
      promises.push(
        axios.get(`${API}/loans/my`).then(res => res.data)
      );

      const results = await Promise.all(promises);
      
      if (isAdmin() || isLibrarian()) {
        const [books, allLoans] = results.slice(0, 2);
        const personalLoans = results[results.length - 1];
        
        // Calculate stats
        const activeLoans = allLoans.filter(loan => loan.status === 'borrowed').length;
        const overdueLoans = allLoans.filter(loan => loan.status === 'overdue').length;
        const availableBooks = books.reduce((sum, book) => sum + book.available_copies, 0);
        
        setStats({
          totalBooks: books.length,
          availableBooks,
          activeLoans,
          overdueLoans,
          totalUsers: 5 // From seed data
        });
        
        setMyLoans(personalLoans);
      } else {
        const personalLoans = results[0];
        setMyLoans(personalLoans);
      }
      
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRoleWelcomeMessage = () => {
    const messages = {
      admin: "Gérez votre bibliothèque en toute simplicité",
      librarian: "Votre espace de gestion de la bibliothèque",
      teacher: "Découvrez et réservez vos ressources pédagogiques",
      student: "Explorez le catalogue et gérez vos emprunts"
    };
    return messages[user?.role] || "Bienvenue dans votre bibliothèque";
  };

  const getQuickActions = () => {
    if (isAdmin() || isLibrarian()) {
      return [
        { label: 'Ajouter un livre', href: '/books/new', icon: BookOpen, color: 'bg-blue-500' },
        { label: 'Gérer les prêts', href: '/loans', icon: BookMarked, color: 'bg-green-500' },
        { label: 'Voir les statistiques', href: '/statistics', icon: TrendingUp, color: 'bg-purple-500' }
      ];
    } else {
      return [
        { label: 'Parcourir le catalogue', href: '/books', icon: BookOpen, color: 'bg-blue-500' },
        { label: 'Mes prêts', href: '/my-loans', icon: BookMarked, color: 'bg-green-500' }
      ];
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
  };

  const getDaysUntilDue = (dueDate) => {
    const due = new Date(dueDate);
    const now = new Date();
    const diffTime = due - now;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-primary to-secondary rounded-xl p-8 text-white">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between">
          <div className="mb-6 md:mb-0">
            <h1 className="text-3xl font-bold mb-2">
              Bonjour, {user?.full_name || user?.email} !
            </h1>
            <p className="text-blue-100 text-lg">
              {getRoleWelcomeMessage()}
            </p>
          </div>
          <div className="flex flex-col sm:flex-row gap-3">
            {getQuickActions().map((action, index) => (
              <Button
                key={index}
                variant="secondary"
                className="bg-white/20 hover:bg-white/30 text-white border border-white/20"
                onClick={() => window.location.href = action.href}
              >
                <action.icon className="h-4 w-4 mr-2" />
                {action.label}
              </Button>
            ))}
          </div>
        </div>
      </div>

      {/* Stats Cards for Admin/Librarian */}
      {(isAdmin() || isLibrarian()) && stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Livres</CardTitle>
              <BookOpen className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalBooks}</div>
              <p className="text-xs text-muted-foreground">
                {stats.availableBooks} disponibles
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Prêts Actifs</CardTitle>
              <BookMarked className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.activeLoans}</div>
              <p className="text-xs text-muted-foreground">
                En cours
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Retards</CardTitle>
              <AlertTriangle className="h-4 w-4 text-destructive" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-destructive">{stats.overdueLoans}</div>
              <p className="text-xs text-muted-foreground">
                À traiter
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Utilisateurs</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalUsers}</div>
              <p className="text-xs text-muted-foreground">
                Actifs
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* My Loans Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <BookMarked className="h-5 w-5 mr-2" />
              Mes Prêts en Cours
            </CardTitle>
            <CardDescription>
              Vos emprunts actuels et leurs échéances
            </CardDescription>
          </CardHeader>
          <CardContent>
            {myLoans.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <BookOpen className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Aucun prêt en cours</p>
                <Button variant="outline" className="mt-4" onClick={() => window.location.href = '/books'}>
                  Parcourir le catalogue
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                {myLoans.slice(0, 3).map((loan) => {
                  const daysUntilDue = getDaysUntilDue(loan.due_at);
                  const isOverdue = daysUntilDue < 0;
                  const isDueSoon = daysUntilDue <= 3 && daysUntilDue >= 0;
                  
                  return (
                    <div key={loan.id} className="flex items-center space-x-4 p-4 border rounded-lg">
                      <div className="flex-1 min-w-0">
                        <p className="font-medium truncate">{loan.book?.title || 'Livre inconnu'}</p>
                        <p className="text-sm text-muted-foreground">
                          Échéance: {formatDate(loan.due_at)}
                        </p>
                      </div>
                      <div className="flex items-center space-x-2">
                        {isOverdue ? (
                          <div className="flex items-center text-destructive">
                            <AlertTriangle className="h-4 w-4 mr-1" />
                            <span className="text-sm font-medium">En retard</span>
                          </div>
                        ) : isDueSoon ? (
                          <div className="flex items-center text-orange-600">
                            <Clock className="h-4 w-4 mr-1" />
                            <span className="text-sm font-medium">{daysUntilDue}j restants</span>
                          </div>
                        ) : (
                          <div className="flex items-center text-green-600">
                            <CheckCircle className="h-4 w-4 mr-1" />
                            <span className="text-sm font-medium">OK</span>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
                
                {myLoans.length > 3 && (
                  <Button variant="outline" className="w-full" onClick={() => window.location.href = '/my-loans'}>
                    Voir tous mes prêts ({myLoans.length})
                  </Button>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Quick Access Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <TrendingUp className="h-5 w-5 mr-2" />
              Accès Rapide
            </CardTitle>
            <CardDescription>
              Vos actions les plus fréquentes
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {getQuickActions().map((action, index) => (
                <Button
                  key={index}
                  variant="outline"
                  className="w-full justify-start h-12"
                  onClick={() => window.location.href = action.href}
                >
                  <div className={`p-2 rounded-md mr-3 ${action.color}`}>
                    <action.icon className="h-4 w-4 text-white" />
                  </div>
                  {action.label}
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity - Admin/Librarian only */}
      {(isAdmin() || isLibrarian()) && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Calendar className="h-5 w-5 mr-2" />
              Activité Récente
            </CardTitle>
            <CardDescription>
              Les dernières actions dans la bibliothèque
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8 text-muted-foreground">
              <Calendar className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>Aucune activité récente</p>
              <p className="text-sm">Les actions seront affichées ici</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default Dashboard;