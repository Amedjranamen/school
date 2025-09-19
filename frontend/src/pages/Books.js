import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/Card';
import { 
  Search, 
  BookOpen, 
  Plus, 
  Filter,
  Eye,
  Edit,
  Trash2,
  BookMarked,
  Calendar,
  User,
  MapPin
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Books = () => {
  const { user, isAdmin, isLibrarian } = useAuth();
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [availableOnly, setAvailableOnly] = useState(false);

  useEffect(() => {
    loadBooks();
  }, [searchQuery, selectedCategory, availableOnly]);

  const loadBooks = async () => {
    try {
      const params = new URLSearchParams();
      if (searchQuery) params.append('q', searchQuery);
      if (selectedCategory) params.append('category', selectedCategory);
      if (availableOnly) params.append('available', 'true');
      
      const response = await axios.get(`${API}/books/?${params.toString()}`);
      setBooks(response.data);
    } catch (error) {
      console.error('Error loading books:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLoanBook = async (bookId) => {
    try {
      await axios.post(`${API}/loans/`, {
        book_id: bookId
      });
      
      // Refresh books list to update availability
      loadBooks();
      
      alert('Livre emprunté avec succès !');
    } catch (error) {
      console.error('Error borrowing book:', error);
      alert(error.response?.data?.detail || 'Erreur lors de l\'emprunt');
    }
  };

  const categories = [...new Set(books.flatMap(book => book.categories || []))];

  const BookCard = ({ book }) => {
    const isAvailable = book.available_copies > 0;
    
    return (
      <Card className="h-full flex flex-col hover:shadow-lg transition-shadow duration-200">
        <div className="relative">
          {book.cover_url ? (
            <img 
              src={book.cover_url} 
              alt={book.title}
              className="w-full h-48 object-cover rounded-t-lg"
            />
          ) : (
            <div className="w-full h-48 bg-gradient-to-br from-blue-100 to-blue-200 rounded-t-lg flex items-center justify-center">
              <BookOpen className="h-16 w-16 text-blue-500" />
            </div>
          )}
          
          <div className="absolute top-2 right-2">
            <div className={`px-2 py-1 rounded-md text-xs font-medium ${
              isAvailable 
                ? 'bg-green-100 text-green-800' 
                : 'bg-red-100 text-red-800'
            }`}>
              {isAvailable ? `${book.available_copies} dispo` : 'Indisponible'}
            </div>
          </div>
        </div>
        
        <CardHeader className="flex-1">
          <CardTitle className="text-lg line-clamp-2">{book.title}</CardTitle>
          <CardDescription className="space-y-2">
            <div className="flex items-center text-sm">
              <User className="h-4 w-4 mr-1" />
              {book.authors?.join(', ') || 'Auteur inconnu'}
            </div>
            
            {book.year && (
              <div className="flex items-center text-sm">
                <Calendar className="h-4 w-4 mr-1" />
                {book.year}
              </div>
            )}
            
            {book.location && (
              <div className="flex items-center text-sm">
                <MapPin className="h-4 w-4 mr-1" />
                {book.location}
              </div>
            )}
            
            {book.categories && book.categories.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-2">
                {book.categories.slice(0, 2).map((category, index) => (
                  <span 
                    key={index}
                    className="inline-flex items-center px-2 py-1 rounded-md text-xs bg-blue-100 text-blue-800"
                  >
                    {category}
                  </span>
                ))}
                {book.categories.length > 2 && (
                  <span className="text-xs text-muted-foreground">
                    +{book.categories.length - 2} autres
                  </span>
                )}
              </div>
            )}
          </CardDescription>
        </CardHeader>

        <CardContent className="pt-0">
          {book.description && (
            <p className="text-sm text-muted-foreground mb-4 line-clamp-3">
              {book.description}
            </p>
          )}

          <div className="flex items-center justify-between space-x-2">
            <div className="flex items-center space-x-2">
              <Button variant="outline" size="sm">
                <Eye className="h-4 w-4 mr-1" />
                Détails
              </Button>
              
              {(isAdmin() || isLibrarian()) && (
                <Button variant="outline" size="sm">
                  <Edit className="h-4 w-4" />
                </Button>
              )}
            </div>

            {isAvailable && (
              <Button 
                size="sm"
                onClick={() => handleLoanBook(book.id)}
                className="flex-shrink-0"
              >
                <BookMarked className="h-4 w-4 mr-1" />
                Emprunter
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between space-y-4 sm:space-y-0">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Catalogue des Livres</h1>
          <p className="text-muted-foreground">
            {books.length} livre{books.length !== 1 ? 's' : ''} disponible{books.length !== 1 ? 's' : ''}
          </p>
        </div>
        
        {(isAdmin() || isLibrarian()) && (
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Ajouter un livre
          </Button>
        )}
      </div>

      {/* Search and Filters */}
      <Card>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Rechercher un livre, auteur, ISBN..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            >
              <option value="">Toutes les catégories</option>
              {categories.map((category) => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
            
            <div className="flex items-center space-x-4">
              <label className="flex items-center space-x-2 text-sm">
                <input
                  type="checkbox"
                  checked={availableOnly}
                  onChange={(e) => setAvailableOnly(e.target.checked)}
                  className="rounded border-gray-300"
                />
                <span>Disponibles uniquement</span>
              </label>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Books Grid */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
      ) : books.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <BookOpen className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
            <h3 className="text-lg font-medium mb-2">Aucun livre trouvé</h3>
            <p className="text-muted-foreground mb-4">
              Essayez de modifier vos critères de recherche
            </p>
            <Button
              variant="outline"
              onClick={() => {
                setSearchQuery('');
                setSelectedCategory('');
                setAvailableOnly(false);
              }}
            >
              Réinitialiser les filtres
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {books.map((book) => (
            <BookCard key={book.id} book={book} />
          ))}
        </div>
      )}
    </div>
  );
};

export default Books;