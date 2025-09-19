import React, { useState, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { 
  Upload, 
  Download, 
  FileText, 
  Users, 
  Book, 
  Settings, 
  AlertCircle,
  CheckCircle,
  Clock,
  Database
} from 'lucide-react';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Progress } from '../components/ui/progress';
import { useToast } from '../hooks/use-toast';

const Admin = () => {
  const { toast } = useToast();
  const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
  
  const [uploadResults, setUploadResults] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  
  const booksFileRef = useRef(null);
  const usersFileRef = useRef(null);

  const handleFileUpload = async (file, endpoint, type) => {
    if (!file) return;
    
    setUploading(true);
    setUploadProgress(0);
    setUploadResults(null);
    
    try {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('file', file);
      
      // Simulation du progrès (car FormData upload ne permet pas de tracker facilement)
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90));
      }, 200);
      
      const response = await fetch(`${backendUrl}/api/import-export/${endpoint}/import`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      if (response.ok) {
        const result = await response.json();
        setUploadResults({
          type,
          success: true,
          ...result
        });
        
        toast({
          title: "Import terminé",
          description: `${result.created} éléments créés, ${result.errors?.length || 0} erreurs`
        });
      } else {
        const error = await response.json();
        setUploadResults({
          type,
          success: false,
          error: error.detail || 'Erreur lors de l\'import'
        });
        
        toast({
          title: "Erreur d'import",
          description: error.detail || 'Une erreur est survenue',
          variant: "destructive"
        });
      }
    } catch (error) {
      setUploadResults({
        type,
        success: false,
        error: 'Erreur de connexion'
      });
      
      toast({
        title: "Erreur",
        description: "Erreur de connexion au serveur",
        variant: "destructive"
      });
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const downloadTemplate = async (type) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${backendUrl}/api/import-export/template/${type}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `template_${type}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        toast({
          title: "Succès",
          description: "Template téléchargé"
        });
      }
    } catch (error) {
      toast({
        title: "Erreur",
        description: "Erreur lors du téléchargement",
        variant: "destructive"
      });
    }
  };

  const exportData = async (type) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${backendUrl}/api/import-export/${type}/export`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `export_${type}_${new Date().toISOString().split('T')[0]}.csv`;
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

  const resetUploadResults = () => {
    setUploadResults(null);
    if (booksFileRef.current) booksFileRef.current.value = '';
    if (usersFileRef.current) usersFileRef.current.value = '';
  };

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Administration</h1>
          <p className="text-gray-600 mt-1">Gestion avancée et import/export des données</p>
        </div>
      </div>

      <Tabs defaultValue="import-export" className="space-y-4">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="import-export">Import/Export</TabsTrigger>
          <TabsTrigger value="system">Système</TabsTrigger>
        </TabsList>

        {/* Import/Export */}
        <TabsContent value="import-export" className="space-y-6">
          {/* Actions rapides */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Export */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Download className="h-5 w-5" />
                  Exporter les données
                </CardTitle>
                <CardDescription>
                  Téléchargez vos données au format CSV
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 gap-3">
                  <Button 
                    onClick={() => exportData('books')} 
                    variant="outline" 
                    className="justify-start gap-2"
                  >
                    <Book className="h-4 w-4" />
                    Exporter les livres
                  </Button>
                  
                  <Button 
                    onClick={() => exportData('users')} 
                    variant="outline" 
                    className="justify-start gap-2"
                  >
                    <Users className="h-4 w-4" />
                    Exporter les utilisateurs
                  </Button>
                  
                  <Button 
                    onClick={() => exportData('loans')} 
                    variant="outline" 
                    className="justify-start gap-2"
                  >
                    <FileText className="h-4 w-4" />
                    Exporter les prêts
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Templates */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  Templates d'import
                </CardTitle>
                <CardDescription>
                  Téléchargez les modèles CSV pour l'import
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 gap-3">
                  <Button 
                    onClick={() => downloadTemplate('books')} 
                    variant="outline" 
                    className="justify-start gap-2"
                  >
                    <Book className="h-4 w-4" />
                    Template livres
                  </Button>
                  
                  <Button 
                    onClick={() => downloadTemplate('users')} 
                    variant="outline" 
                    className="justify-start gap-2"
                  >
                    <Users className="h-4 w-4" />
                    Template utilisateurs
                  </Button>
                </div>
                
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    Utilisez ces templates pour formater correctement vos données avant l'import.
                  </AlertDescription>
                </Alert>
              </CardContent>
            </Card>
          </div>

          {/* Import de fichiers */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Upload className="h-5 w-5" />
                Importer des données
              </CardTitle>
              <CardDescription>
                Importez vos données depuis des fichiers CSV
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Import Livres */}
              <div className="space-y-4">
                <div>
                  <Label htmlFor="books-file" className="text-base font-medium">
                    Import des livres
                  </Label>
                  <p className="text-sm text-muted-foreground mb-2">
                    Fichier CSV avec les colonnes : title, authors, isbn, publisher, year, categories, total_copies
                  </p>
                </div>
                
                <div className="flex items-center gap-4">
                  <Input
                    id="books-file"
                    type="file"
                    accept=".csv"
                    ref={booksFileRef}
                    disabled={uploading}
                    className="flex-1"
                  />
                  <Button
                    onClick={() => {
                      const file = booksFileRef.current?.files[0];
                      if (file) handleFileUpload(file, 'books', 'livres');
                    }}
                    disabled={uploading}
                    className="gap-2"
                  >
                    <Upload className="h-4 w-4" />
                    Importer
                  </Button>
                </div>
              </div>

              {/* Import Utilisateurs */}
              <div className="space-y-4">
                <div>
                  <Label htmlFor="users-file" className="text-base font-medium">
                    Import des utilisateurs
                  </Label>
                  <p className="text-sm text-muted-foreground mb-2">
                    Fichier CSV avec les colonnes : username, email, full_name, role, class, phone, password
                  </p>
                </div>
                
                <div className="flex items-center gap-4">
                  <Input
                    id="users-file"
                    type="file"
                    accept=".csv"
                    ref={usersFileRef}
                    disabled={uploading}
                    className="flex-1"
                  />
                  <Button
                    onClick={() => {
                      const file = usersFileRef.current?.files[0];
                      if (file) handleFileUpload(file, 'users', 'utilisateurs');
                    }}
                    disabled={uploading}
                    className="gap-2"
                  >
                    <Upload className="h-4 w-4" />
                    Importer
                  </Button>
                </div>
              </div>

              {/* Progrès de l'upload */}
              {uploading && (
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4" />
                    <span className="text-sm">Import en cours...</span>
                  </div>
                  <Progress value={uploadProgress} className="w-full" />
                </div>
              )}

              {/* Résultats de l'upload */}
              {uploadResults && (
                <div className="space-y-4">
                  <Alert className={uploadResults.success ? "border-green-200 bg-green-50" : "border-red-200 bg-red-50"}>
                    {uploadResults.success ? (
                      <CheckCircle className="h-4 w-4 text-green-600" />
                    ) : (
                      <AlertCircle className="h-4 w-4 text-red-600" />
                    )}
                    <AlertDescription>
                      {uploadResults.success ? (
                        <div>
                          <p className="font-medium">Import réussi !</p>
                          <ul className="mt-2 space-y-1 text-sm">
                            <li>✅ {uploadResults.created} {uploadResults.type} créés</li>
                            {uploadResults.updated > 0 && (
                              <li>🔄 {uploadResults.updated} {uploadResults.type} mis à jour</li>
                            )}
                            {uploadResults.duplicates > 0 && (
                              <li>⚠️ {uploadResults.duplicates} doublons ignorés</li>
                            )}
                            {uploadResults.errors?.length > 0 && (
                              <li>❌ {uploadResults.errors.length} erreurs</li>
                            )}
                          </ul>
                        </div>
                      ) : (
                        <div>
                          <p className="font-medium">Erreur d'import</p>
                          <p className="text-sm mt-1">{uploadResults.error}</p>
                        </div>
                      )}
                    </AlertDescription>
                  </Alert>

                  {/* Détail des erreurs */}
                  {uploadResults.success && uploadResults.errors?.length > 0 && (
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg">Erreurs détectées</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2 max-h-60 overflow-y-auto">
                          {uploadResults.errors.slice(0, 10).map((error, index) => (
                            <div key={index} className="flex items-start gap-2 text-sm">
                              <Badge variant="destructive" className="mt-0.5">
                                Ligne {error.row}
                              </Badge>
                              <span className="text-muted-foreground">{error.error}</span>
                            </div>
                          ))}
                          {uploadResults.errors.length > 10 && (
                            <p className="text-sm text-muted-foreground">
                              ... et {uploadResults.errors.length - 10} autres erreurs
                            </p>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  )}

                  <Button onClick={resetUploadResults} variant="outline">
                    Nouveau fichier
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Système */}
        <TabsContent value="system" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                Configuration du système
              </CardTitle>
              <CardDescription>
                Paramètres généraux de l'application
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <Alert>
                <Database className="h-4 w-4" />
                <AlertDescription>
                  <strong>Base de données :</strong> MongoDB connectée et opérationnelle
                </AlertDescription>
              </Alert>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Paramètres des prêts</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label>Durée de prêt par défaut</Label>
                      <Input value="14 jours" disabled className="mt-1" />
                    </div>
                    <div>
                      <Label>Amende par jour de retard</Label>
                      <Input value="0.50€" disabled className="mt-1" />
                    </div>
                    <div>
                      <Label>Nombre max de prêts par utilisateur</Label>
                      <Input value="5" disabled className="mt-1" />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Notifications</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label>Rappel avant échéance</Label>
                      <Input value="3 jours" disabled className="mt-1" />
                    </div>
                    <div>
                      <Label>Rappel de retard</Label>
                      <Input value="Quotidien" disabled className="mt-1" />
                    </div>
                  </CardContent>
                </Card>
              </div>

              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  Les paramètres de configuration avancée seront disponibles dans une prochaine version.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Admin;