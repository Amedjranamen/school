import React, { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/Card';
import { BookOpen, Library, Eye, EyeOff } from 'lucide-react';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || '/dashboard';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await login(email, password);
    
    if (result.success) {
      navigate(from, { replace: true });
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  const demoAccounts = [
    { email: 'admin', password: 'admin123', role: 'Administrateur', color: 'bg-red-100 text-red-800' },
    { email: 'bibliothecaire', password: 'biblio123', role: 'Bibliothécaire', color: 'bg-blue-100 text-blue-800' },
    { email: 'prof_martin', password: 'prof123', role: 'Enseignant', color: 'bg-green-100 text-green-800' },
    { email: 'eleve_sophie', password: 'eleve123', role: 'Élève', color: 'bg-purple-100 text-purple-800' },
  ];

  const fillDemo = (demoEmail, demoPassword) => {
    setEmail(demoEmail);
    setPassword(demoPassword);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Hero Section avec image */}
      <div className="relative">
        <div className="absolute inset-0">
          <img
            src="https://images.unsplash.com/photo-1507738978512-35798112892c?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzl8MHwxfHNlYXJjaHwxfHxtb2Rlcm4lMjBsaWJyYXJ5fGVufDB8fHxibHVlfDE3NTgzMDY3MTl8MA&ixlib=rb-4.1.0&q=85"
            alt="Bibliothèque moderne"
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-primary/80"></div>
        </div>
        
        <div className="relative min-h-screen flex items-center justify-center px-4 py-12">
          <div className="w-full max-w-6xl grid lg:grid-cols-2 gap-8 items-center">
            
            {/* Section gauche - Branding */}
            <div className="text-white space-y-6 text-center lg:text-left">
              <div className="flex items-center justify-center lg:justify-start space-x-3">
                <div className="p-3 bg-white/20 rounded-xl backdrop-blur-sm">
                  <Library className="h-8 w-8 text-white" />
                </div>
                <h1 className="text-3xl font-bold">BiblioSco</h1>
              </div>
              
              <div className="space-y-4">
                <h2 className="text-4xl lg:text-5xl font-bold leading-tight">
                  Gestion de bibliothèque
                  <span className="block text-secondary">nouvelle génération</span>
                </h2>
                <p className="text-xl text-blue-100 max-w-lg">
                  Simplifiez la gestion de votre bibliothèque scolaire avec notre solution moderne et intuitive.
                </p>
              </div>

              <div className="flex flex-wrap gap-4 justify-center lg:justify-start">
                <div className="flex items-center space-x-2 bg-white/10 rounded-full px-4 py-2 backdrop-blur-sm">
                  <BookOpen className="h-5 w-5" />
                  <span>Catalogue numérique</span>
                </div>
                <div className="flex items-center space-x-2 bg-white/10 rounded-full px-4 py-2 backdrop-blur-sm">
                  <Library className="h-5 w-5" />
                  <span>Gestion des prêts</span>
                </div>
              </div>
            </div>

            {/* Section droite - Formulaire de connexion */}
            <div className="w-full max-w-md mx-auto">
              <Card className="shadow-2xl border-0 bg-white/95 backdrop-blur-sm">
                <CardHeader className="text-center">
                  <CardTitle className="text-2xl font-bold text-primary">Connexion</CardTitle>
                  <CardDescription>
                    Accédez à votre espace BiblioSco
                  </CardDescription>
                </CardHeader>
                
                <CardContent>
                  <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="space-y-2">
                      <label htmlFor="email" className="text-sm font-medium text-gray-700">
                        Nom d'utilisateur
                      </label>
                      <Input
                        id="email"
                        type="text"
                        placeholder="Votre nom d'utilisateur"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                        className="h-12"
                      />
                    </div>

                    <div className="space-y-2">
                      <label htmlFor="password" className="text-sm font-medium text-gray-700">
                        Mot de passe
                      </label>
                      <div className="relative">
                        <Input
                          id="password"
                          type={showPassword ? "text" : "password"}
                          placeholder="Votre mot de passe"
                          value={password}
                          onChange={(e) => setPassword(e.target.value)}
                          required
                          className="h-12 pr-12"
                        />
                        <button
                          type="button"
                          onClick={() => setShowPassword(!showPassword)}
                          className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
                        >
                          {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                        </button>
                      </div>
                    </div>

                    {error && (
                      <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-md">
                        <p className="text-sm text-destructive">{error}</p>
                      </div>
                    )}

                    <Button 
                      type="submit" 
                      className="w-full h-12 text-base font-semibold"
                      disabled={loading}
                    >
                      {loading ? (
                        <div className="flex items-center space-x-2">
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                          <span>Connexion...</span>
                        </div>
                      ) : (
                        'Se connecter'
                      )}
                    </Button>
                  </form>

                  {/* Comptes de démonstration */}
                  <div className="mt-8 pt-6 border-t border-gray-200">
                    <h3 className="text-sm font-medium text-gray-700 mb-4 text-center">
                      Comptes de démonstration
                    </h3>
                    <div className="space-y-2">
                      {demoAccounts.map((account, index) => (
                        <button
                          key={index}
                          onClick={() => fillDemo(account.email, account.password)}
                          className="w-full p-2 text-left rounded-md bg-gray-50 hover:bg-gray-100 transition-colors duration-200 border border-gray-200"
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium text-gray-900 truncate">
                                {account.email}
                              </p>
                              <p className="text-xs text-gray-500">
                                Mot de passe: {account.password}
                              </p>
                            </div>
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${account.color}`}>
                              {account.role}
                            </span>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;