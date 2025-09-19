import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Library, Eye, EyeOff, AlertCircle, Users, BookOpen, Shield } from 'lucide-react';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError('Email ou mot de passe incorrect');
    } finally {
      setLoading(false);
    }
  };

  const demoAccounts = [
    {
      role: 'Administrateur',
      username: 'admin',
      password: 'admin123',
      description: 'Accès complet à toutes les fonctionnalités',
      icon: Shield,
      color: 'text-red-600',
      bgColor: 'bg-red-50'
    },
    {
      role: 'Bibliothécaire',
      username: 'bibliothecaire',
      password: 'biblio123',
      description: 'Gestion des livres, prêts et statistiques',
      icon: BookOpen,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50'
    },
    {
      role: 'Enseignant',
      username: 'prof_martin',
      password: 'prof123',
      description: 'Consultation et réservation de ressources',
      icon: Users,
      color: 'text-green-600',
      bgColor: 'bg-green-50'
    },
    {
      role: 'Élève',
      username: 'eleve_sophie',
      password: 'eleve123',
      description: 'Catalogue et gestion des prêts personnels',
      icon: Users,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50'
    }
  ];

  const quickLogin = (username, password) => {
    setEmail(username);
    setPassword(password);
    setError('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 via-secondary/5 to-accent/5 flex items-center justify-center p-4">
      <div className="w-full max-w-6xl grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Formulaire de connexion */}
        <div className="flex items-center justify-center">
          <Card className="w-full max-w-md shadow-xl border-0 bg-white/80 backdrop-blur">
            <CardHeader className="space-y-4 text-center">
              <div className="mx-auto p-3 bg-primary rounded-full">
                <Library className="h-8 w-8 text-white" />
              </div>
              <div>
                <CardTitle className="text-2xl font-bold text-gray-900">BiblioSco</CardTitle>
                <CardDescription className="text-gray-600">
                  Connectez-vous à votre bibliothèque scolaire
                </CardDescription>
              </div>
            </CardHeader>
            
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                {error && (
                  <Alert className="border-red-200 bg-red-50">
                    <AlertCircle className="h-4 w-4 text-red-600" />
                    <AlertDescription className="text-red-800">
                      {error}
                    </AlertDescription>
                  </Alert>
                )}
                
                <div className="space-y-2">
                  <Label htmlFor="email" className="text-gray-700">
                    Nom d'utilisateur
                  </Label>
                  <Input
                    id="email"
                    type="text"
                    placeholder="votre-nom-utilisateur"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="h-11"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="password" className="text-gray-700">
                    Mot de passe
                  </Label>
                  <div className="relative">
                    <Input
                      id="password"
                      type={showPassword ? 'text' : 'password'}
                      placeholder="Votre mot de passe"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      className="h-11 pr-10"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 transition-colors"
                    >
                      {showPassword ? (
                        <EyeOff className="h-4 w-4" />
                      ) : (
                        <Eye className="h-4 w-4" />
                      )}
                    </button>
                  </div>
                </div>
                
                <Button
                  type="submit"
                  className="w-full h-11 bg-primary hover:bg-primary/90 text-white font-medium"
                  disabled={loading}
                >
                  {loading ? (
                    <div className="flex items-center gap-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      Connexion...
                    </div>
                  ) : (
                    'Se connecter'
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>

        {/* Comptes de démonstration */}
        <div className="space-y-6">
          <div className="text-center lg:text-left">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Comptes de démonstration
            </h2>
            <p className="text-gray-600">
              Testez les différents rôles avec ces comptes préconfigurés
            </p>
          </div>
          
          <div className="grid gap-4">
            {demoAccounts.map((account, index) => (
              <Card 
                key={index} 
                className="cursor-pointer transition-all duration-200 hover:shadow-md hover:scale-[1.01] border border-gray-200"
                onClick={() => quickLogin(account.username, account.password)}
              >
                <CardContent className="p-4">
                  <div className="flex items-center space-x-4">
                    <div className={`p-3 rounded-lg ${account.bgColor}`}>
                      <account.icon className={`h-6 w-6 ${account.color}`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-semibold text-gray-900">
                          {account.role}
                        </h3>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">
                        {account.description}
                      </p>
                      <div className="text-xs text-gray-500 space-y-1">
                        <div className="font-mono bg-gray-100 px-2 py-1 rounded">
                          👤 {account.username}
                        </div>
                        <div className="font-mono bg-gray-100 px-2 py-1 rounded">
                          🔑 {account.password}
                        </div>
                      </div>
                    </div>
                    <div className="text-gray-400">
                      <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
          
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0">
                <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5" />
              </div>
              <div>
                <h4 className="text-sm font-medium text-blue-900 mb-1">
                  Mode démonstration
                </h4>
                <p className="text-sm text-blue-800">
                  Cliquez sur un compte pour vous connecter automatiquement et explorer les fonctionnalités selon le rôle sélectionné.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;