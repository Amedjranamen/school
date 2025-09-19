import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import { 
  BarChart3, 
  TrendingUp, 
  Users, 
  Book, 
  Calendar, 
  Download,
  AlertTriangle,
  CheckCircle,
  Clock,
  BookOpen
} from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const Statistics = () => {
  const { toast } = useToast();
  const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
  
  const [dashboardStats, setDashboardStats] = useState({});
  const [loansReport, setLoansReport] = useState({ summary: {}, loans: [] });
  const [booksReport, setBooksReport] = useState({ summary: {}, books: [] });
  const [usersReport, setUsersReport] = useState({ summary: {}, users: [] });
  const [loading, setLoading] = useState(true);
  
  // Filtres
  const [loansStatusFilter, setLoansStatusFilter] = useState('');
  const [loansRoleFilter, setLoansRoleFilter] = useState('');
  const [booksAvailabilityFilter, setBooksAvailabilityFilter] = useState('');
  const [userRoleFilter, setUserRoleFilter] = useState('');

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  useEffect(() => {
    fetchLoansReport();
  }, [loansStatusFilter, loansRoleFilter]);

  useEffect(() => {
    fetchBooksReport();
  }, [booksAvailabilityFilter]);

  useEffect(() => {
    fetchUsersReport();
  }, [userRoleFilter]);

  const fetchDashboardStats = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${backendUrl}/api/reports/dashboard-stats`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setDashboardStats(data);
      }
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchLoansReport = async () => {
    try {
      const token = localStorage.getItem('token');
      const params = new URLSearchParams();
      if (loansStatusFilter) params.append('status', loansStatusFilter);
      if (loansRoleFilter) params.append('user_role', loansRoleFilter);
      
      const response = await fetch(`${backendUrl}/api/reports/loans-report?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setLoansReport(data);
      }
    } catch (error) {
      console.error('Error fetching loans report:', error);
    }
  };

  const fetchBooksReport = async () => {
    try {
      const token = localStorage.getItem('token');
      const params = new URLSearchParams();
      if (booksAvailabilityFilter) params.append('availability', booksAvailabilityFilter);
      
      const response = await fetch(`${backendUrl}/api/reports/books-report?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setBooksReport(data);
      }
    } catch (error) {
      console.error('Error fetching books report:', error);
    }
  };

  const fetchUsersReport = async () => {
    try {
      const token = localStorage.getItem('token');
      const params = new URLSearchParams();
      if (userRoleFilter) params.append('role', userRoleFilter);
      
      const response = await fetch(`${backendUrl}/api/reports/users-report?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setUsersReport(data);
      }
    } catch (error) {
      console.error('Error fetching users report:', error);
    }
  };

  const exportReport = async (type, params = {}) => {
    try {
      const token = localStorage.getItem('token');
      const urlParams = new URLSearchParams(params);
      
      const response = await fetch(`${backendUrl}/api/import-export/${type}/export?${urlParams}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${type}_report.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        toast({
          title: "Succès",
          description: "Export terminé"
        });
      }
    } catch (error) {
      toast({
        title: "Erreur",
        description: "Erreur lors de l'export",
        variant: "destructive"
      });
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('fr-FR');
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'borrowed':
        return <Clock className="h-4 w-4 text-blue-600" />;
      case 'returned':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'overdue':
        return <AlertTriangle className="h-4 w-4 text-red-600" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'borrowed':
        return 'bg-blue-100 text-blue-800';
      case 'returned':
        return 'bg-green-100 text-green-800';
      case 'overdue':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Statistiques et Rapports</h1>
          <p className="text-gray-600 mt-1">Analysez l'activité de votre bibliothèque</p>
        </div>
      </div>

      <Tabs defaultValue="dashboard" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="dashboard">Tableau de bord</TabsTrigger>
          <TabsTrigger value="loans">Prêts</TabsTrigger>
          <TabsTrigger value="books">Livres</TabsTrigger>
          <TabsTrigger value="users">Utilisateurs</TabsTrigger>
        </TabsList>

        {/* Tableau de bord général */}
        <TabsContent value="dashboard" className="space-y-6">
          {/* Métriques principales */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Livres</CardTitle>
                <Book className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{dashboardStats.overview?.total_books || 0}</div>
                <p className="text-xs text-muted-foreground">
                  {dashboardStats.overview?.available_books || 0} disponibles
                </p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Utilisateurs</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{dashboardStats.overview?.total_users || 0}</div>
                <p className="text-xs text-muted-foreground">utilisateurs actifs</p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Prêts Actifs</CardTitle>
                <BookOpen className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{dashboardStats.overview?.active_loans || 0}</div>
                <p className="text-xs text-muted-foreground">en cours</p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Retards</CardTitle>
                <AlertTriangle className="h-4 w-4 text-red-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">
                  {dashboardStats.overview?.overdue_loans || 0}
                </div>
                <p className="text-xs text-muted-foreground">en retard</p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Taux d'occupation</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {dashboardStats.overview ? 
                    Math.round(((dashboardStats.overview.total_books - dashboardStats.overview.available_books) / dashboardStats.overview.total_books) * 100) || 0
                    : 0}%
                </div>
                <p className="text-xs text-muted-foreground">des livres empruntés</p>
              </CardContent>
            </Card>
          </div>

          {/* Livres populaires */}
          <Card>
            <CardHeader>
              <CardTitle>Livres les plus populaires (30 derniers jours)</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Livre</TableHead>
                    <TableHead>Auteurs</TableHead>
                    <TableHead className="text-right">Emprunts</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {dashboardStats.popular_books?.slice(0, 5).map((book, index) => (
                    <TableRow key={index}>
                      <TableCell className="font-medium">{book.book_title}</TableCell>
                      <TableCell>{book.book_authors?.join(', ')}</TableCell>
                      <TableCell className="text-right">
                        <Badge variant="secondary">{book.loan_count}</Badge>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              
              {!dashboardStats.popular_books?.length && (
                <div className="text-center py-8 text-muted-foreground">
                  Aucune donnée disponible
                </div>
              )}
            </CardContent>
          </Card>

          {/* Activité récente */}
          <Card>
            <CardHeader>
              <CardTitle>Activité récente</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Livre</TableHead>
                    <TableHead>Utilisateur</TableHead>
                    <TableHead>Date d'emprunt</TableHead>
                    <TableHead>Statut</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {dashboardStats.recent_activity?.slice(0, 10).map((activity) => (
                    <TableRow key={activity.id}>
                      <TableCell className="font-medium">{activity.book_title}</TableCell>
                      <TableCell>{activity.user_name}</TableCell>
                      <TableCell>{formatDate(activity.borrowed_at)}</TableCell>
                      <TableCell>
                        <Badge className={getStatusColor(activity.status)}>
                          {activity.status === 'borrowed' ? 'Emprunté' : 
                           activity.status === 'returned' ? 'Rendu' : 'En retard'}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              
              {!dashboardStats.recent_activity?.length && (
                <div className="text-center py-8 text-muted-foreground">
                  Aucune activité récente
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Rapport des prêts */}
        <TabsContent value="loans" className="space-y-6">
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
            <div className="flex gap-4">
              <Select value={loansStatusFilter} onValueChange={setLoansStatusFilter}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Filtrer par statut" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Tous les statuts</SelectItem>
                  <SelectItem value="borrowed">Emprunté</SelectItem>
                  <SelectItem value="returned">Rendu</SelectItem>
                  <SelectItem value="overdue">En retard</SelectItem>
                </SelectContent>
              </Select>
              
              <Select value={loansRoleFilter} onValueChange={setLoansRoleFilter}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Filtrer par rôle" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Tous les rôles</SelectItem>
                  <SelectItem value="student">Élèves</SelectItem>
                  <SelectItem value="teacher">Enseignants</SelectItem>
                  <SelectItem value="librarian">Bibliothécaires</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <Button 
              onClick={() => exportReport('loans', { 
                status: loansStatusFilter, 
                user_role: loansRoleFilter 
              })}
              className="gap-2"
            >
              <Download className="h-4 w-4" />
              Exporter
            </Button>
          </div>

          {/* Résumé des prêts */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Total des prêts</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{loansReport.summary?.total_loans || 0}</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Total des amendes</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{loansReport.summary?.total_fines || 0}€</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Répartition par statut</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {Object.entries(loansReport.summary?.status_breakdown || {}).map(([status, count]) => (
                    <div key={status} className="flex justify-between">
                      <span className="capitalize">{status === 'borrowed' ? 'Emprunté' : status === 'returned' ? 'Rendu' : 'En retard'}</span>
                      <Badge variant="outline">{count}</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Table des prêts */}
          <Card>
            <CardHeader>
              <CardTitle>Détail des prêts</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Livre</TableHead>
                    <TableHead>Utilisateur</TableHead>
                    <TableHead>Emprunté le</TableHead>
                    <TableHead>Échéance</TableHead>
                    <TableHead>Statut</TableHead>
                    <TableHead className="text-right">Amende</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loansReport.loans?.slice(0, 20).map((loan) => (
                    <TableRow key={loan.id}>
                      <TableCell>
                        <div>
                          <div className="font-medium">{loan.book_title}</div>
                          <div className="text-sm text-muted-foreground">
                            {loan.book_authors?.join(', ')}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div>
                          <div>{loan.user_name}</div>
                          <div className="text-sm text-muted-foreground">{loan.user_class}</div>
                        </div>
                      </TableCell>
                      <TableCell>{formatDate(loan.borrowed_at)}</TableCell>
                      <TableCell>{formatDate(loan.due_at)}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {getStatusIcon(loan.status)}
                          <Badge className={getStatusColor(loan.status)}>
                            {loan.status === 'borrowed' ? 'Emprunté' : 
                             loan.status === 'returned' ? 'Rendu' : 'En retard'}
                          </Badge>
                        </div>
                      </TableCell>
                      <TableCell className="text-right">
                        {loan.fine > 0 ? `${loan.fine}€` : '-'}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              
              {!loansReport.loans?.length && (
                <div className="text-center py-8 text-muted-foreground">
                  Aucun prêt trouvé
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Rapport des livres */}
        <TabsContent value="books" className="space-y-6">
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
            <Select value={booksAvailabilityFilter} onValueChange={setBooksAvailabilityFilter}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filtrer par disponibilité" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">Tous les livres</SelectItem>
                <SelectItem value="available">Disponibles</SelectItem>
                <SelectItem value="unavailable">Non disponibles</SelectItem>
              </SelectContent>
            </Select>
            
            <Button onClick={() => exportReport('books', { availability: booksAvailabilityFilter })} className="gap-2">
              <Download className="h-4 w-4" />
              Exporter
            </Button>
          </div>

          {/* Résumé des livres */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Total livres</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{booksReport.summary?.total_books || 0}</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Exemplaires total</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{booksReport.summary?.total_copies || 0}</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Disponibles</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-green-600">
                  {booksReport.summary?.available_copies || 0}
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Taux d'emprunt</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{booksReport.summary?.loan_rate || 0}%</div>
              </CardContent>
            </Card>
          </div>

          {/* Table des livres avec statistiques */}
          <Card>
            <CardHeader>
              <CardTitle>Popularité des livres</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Livre</TableHead>
                    <TableHead>Auteurs</TableHead>
                    <TableHead className="text-center">Exemplaires</TableHead>
                    <TableHead className="text-center">Disponibles</TableHead>
                    <TableHead className="text-center">Total prêts</TableHead>
                    <TableHead className="text-center">Score popularité</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {booksReport.books?.slice(0, 20).map((book) => (
                    <TableRow key={book.id}>
                      <TableCell>
                        <div className="font-medium">{book.title}</div>
                        <div className="text-sm text-muted-foreground">
                          {book.categories?.join(', ')}
                        </div>
                      </TableCell>
                      <TableCell>{book.authors?.join(', ')}</TableCell>
                      <TableCell className="text-center">{book.total_copies}</TableCell>
                      <TableCell className="text-center">
                        <Badge variant={book.available_copies > 0 ? "default" : "secondary"}>
                          {book.available_copies}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-center">{book.total_loans}</TableCell>
                      <TableCell className="text-center">
                        <Badge variant="outline">
                          {book.popularity_score?.toFixed(1) || '0.0'}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              
              {!booksReport.books?.length && (
                <div className="text-center py-8 text-muted-foreground">
                  Aucun livre trouvé
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Rapport des utilisateurs */}
        <TabsContent value="users" className="space-y-6">
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
            <Select value={userRoleFilter} onValueChange={setUserRoleFilter}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filtrer par rôle" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">Tous les rôles</SelectItem>
                <SelectItem value="student">Élèves</SelectItem>
                <SelectItem value="teacher">Enseignants</SelectItem>
                <SelectItem value="librarian">Bibliothécaires</SelectItem>
                <SelectItem value="admin">Administrateurs</SelectItem>
              </SelectContent>
            </Select>
            
            <Button onClick={() => exportReport('users', { role: userRoleFilter })} className="gap-2">
              <Download className="h-4 w-4" />
              Exporter
            </Button>
          </div>

          {/* Résumé des utilisateurs */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Total utilisateurs</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{usersReport.summary?.total_users || 0}</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Utilisateurs actifs</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-green-600">
                  {usersReport.summary?.active_users || 0}
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Total prêts</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{usersReport.summary?.total_loans || 0}</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Moyenne par utilisateur</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{usersReport.summary?.avg_loans_per_user || 0}</div>
              </CardContent>
            </Card>
          </div>

          {/* Table des utilisateurs avec activité */}
          <Card>
            <CardHeader>
              <CardTitle>Activité des utilisateurs</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Utilisateur</TableHead>
                    <TableHead>Rôle</TableHead>
                    <TableHead>Classe</TableHead>
                    <TableHead className="text-center">Total prêts</TableHead>
                    <TableHead className="text-center">Prêts actifs</TableHead>
                    <TableHead className="text-center">En retard</TableHead>
                    <TableHead className="text-center">Amendes</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {usersReport.users?.slice(0, 20).map((user) => (
                    <TableRow key={user.id}>
                      <TableCell>
                        <div>
                          <div className="font-medium">{user.full_name}</div>
                          <div className="text-sm text-muted-foreground">{user.email}</div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">{user.role}</Badge>
                      </TableCell>
                      <TableCell>{user.class || '-'}</TableCell>
                      <TableCell className="text-center">{user.total_loans}</TableCell>
                      <TableCell className="text-center">
                        <Badge variant={user.active_loans > 0 ? "default" : "secondary"}>
                          {user.active_loans}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-center">
                        {user.overdue_loans > 0 ? (
                          <Badge variant="destructive">{user.overdue_loans}</Badge>
                        ) : (
                          <span>-</span>
                        )}
                      </TableCell>
                      <TableCell className="text-center">
                        {user.total_fines > 0 ? `${user.total_fines}€` : '-'}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              
              {!usersReport.users?.length && (
                <div className="text-center py-8 text-muted-foreground">
                  Aucun utilisateur trouvé
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Statistics;