import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { 
  BookMarked, 
  Calendar, 
  AlertTriangle, 
  CheckCircle, 
  Clock,
  BookOpen,
  User
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const MyLoans = () => {
  const { user } = useAuth();
  const [loans, setLoans] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMyLoans();
  }, []);

  const loadMyLoans = async () => {
    try {
      const response = await axios.get(`${API}/loans/my`);
      setLoans(response.data);
    } catch (error) {
      console.error('Error loading loans:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'long',
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

  const getStatusInfo = (loan) => {
    if (loan.returned_at) {
      return {
        status: 'returned',
        label: 'Rendu',
        color: 'text-green-600 bg-green-50',
        icon: CheckCircle
      };
    }
    
    const daysUntilDue = getDaysUntilDue(loan.due_at);
    
    if (daysUntilDue < 0) {
      return {
        status: 'overdue',
        label: `En retard (${Math.abs(daysUntilDue)} jour${Math.abs(daysUntilDue) > 1 ? 's' : ''})`,
        color: 'text-red-600 bg-red-50',
        icon: AlertTriangle
      };
    } else if (daysUntilDue <= 3) {
      return {
        status: 'due_soon',
        label: `${daysUntilDue} jour${daysUntilDue > 1 ? 's' : ''} restant${daysUntilDue > 1 ? 's' : ''}`,
        color: 'text-orange-600 bg-orange-50',
        icon: Clock
      };
    } else {
      return {
        status: 'active',
        label: `${daysUntilDue} jours restants`,
        color: 'text-blue-600 bg-blue-50',
        icon: BookMarked
      };
    }
  };

  const activeLoans = loans.filter(loan => !loan.returned_at);
  const returnedLoans = loans.filter(loan => loan.returned_at);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Mes Prêts</h1>
        <p className="text-muted-foreground">
          Gérez vos emprunts et consultez l'historique
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Prêts Actifs</CardTitle>
            <BookMarked className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{activeLoans.length}</div>
            <p className="text-xs text-muted-foreground">
              En cours
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">En Retard</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {activeLoans.filter(loan => getDaysUntilDue(loan.due_at) < 0).length}
            </div>
            <p className="text-xs text-muted-foreground">
              À rendre
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Historique</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{returnedLoans.length}</div>
            <p className="text-xs text-muted-foreground">
              Rendus
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Active Loans */}
      <div className="space-y-6">
        <div>
          <h2 className="text-xl font-semibold mb-4">Prêts en Cours</h2>
          
          {activeLoans.length === 0 ? (
            <Card>
              <CardContent className="text-center py-12">
                <BookOpen className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
                <h3 className="text-lg font-medium mb-2">Aucun prêt en cours</h3>
                <p className="text-muted-foreground mb-4">
                  Explorez notre catalogue pour emprunter des livres
                </p>
                <Button onClick={() => window.location.href = '/books'}>
                  Parcourir le catalogue
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {activeLoans.map((loan) => {
                const statusInfo = getStatusInfo(loan);
                const StatusIcon = statusInfo.icon;
                
                return (
                  <Card key={loan.id} className="hover:shadow-md transition-shadow">
                    <CardContent className="p-6">
                      <div className="flex flex-col md:flex-row md:items-center space-y-4 md:space-y-0 md:space-x-6">
                        {/* Book cover placeholder */}
                        <div className="flex-shrink-0">
                          <div className="w-16 h-20 bg-gradient-to-br from-blue-100 to-blue-200 rounded-md flex items-center justify-center">
                            <BookOpen className="h-8 w-8 text-blue-500" />
                          </div>
                        </div>
                        
                        {/* Book info */}
                        <div className="flex-1 min-w-0">
                          <h3 className="text-lg font-semibold mb-1">
                            {loan.book?.title || 'Titre non disponible'}
                          </h3>
                          <p className="text-muted-foreground mb-2">
                            {loan.book?.authors?.join(', ') || 'Auteur inconnu'}
                          </p>
                          
                          <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
                            <div className="flex items-center">
                              <Calendar className="h-4 w-4 mr-1" />
                              Emprunté le {formatDate(loan.borrowed_at)}
                            </div>
                            <div className="flex items-center">
                              <Clock className="h-4 w-4 mr-1" />
                              À rendre le {formatDate(loan.due_at)}
                            </div>
                          </div>
                        </div>
                        
                        {/* Status */}
                        <div className="flex items-center">
                          <div className={`flex items-center px-3 py-2 rounded-full ${statusInfo.color}`}>
                            <StatusIcon className="h-4 w-4 mr-2" />
                            <span className="font-medium">{statusInfo.label}</span>
                          </div>
                        </div>
                      </div>
                      
                      {loan.fine > 0 && (
                        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
                          <div className="flex items-center">
                            <AlertTriangle className="h-4 w-4 text-red-600 mr-2" />
                            <span className="text-red-800 font-medium">
                              Amende: {loan.fine}€
                            </span>
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          )}
        </div>

        {/* Loan History */}
        {returnedLoans.length > 0 && (
          <div>
            <h2 className="text-xl font-semibold mb-4">Historique des Prêts</h2>
            
            <div className="space-y-4">
              {returnedLoans.slice(0, 5).map((loan) => (
                <Card key={loan.id} className="opacity-75">
                  <CardContent className="p-4">
                    <div className="flex items-center space-x-4">
                      <div className="flex-shrink-0">
                        <div className="w-12 h-16 bg-gradient-to-br from-gray-100 to-gray-200 rounded-md flex items-center justify-center">
                          <BookOpen className="h-6 w-6 text-gray-400" />
                        </div>
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <h4 className="font-medium">
                          {loan.book?.title || 'Titre non disponible'}
                        </h4>
                        <p className="text-sm text-muted-foreground">
                          {loan.book?.authors?.join(', ') || 'Auteur inconnu'}
                        </p>
                        <div className="flex items-center text-sm text-muted-foreground mt-1">
                          <CheckCircle className="h-4 w-4 mr-1 text-green-500" />
                          Rendu le {formatDate(loan.returned_at)}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
              
              {returnedLoans.length > 5 && (
                <div className="text-center">
                  <Button variant="outline">
                    Voir tout l'historique ({returnedLoans.length - 5} autres)
                  </Button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MyLoans;