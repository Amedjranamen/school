import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from './ui/Button';
import {
  Library,
  BookOpen,
  Users,
  BarChart3,
  Settings,
  Menu,
  X,
  LogOut,
  User,
  BookMarked,
  ClipboardList,
  Home
} from 'lucide-react';

const Layout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { user, logout, isAdmin, isLibrarian, isTeacher } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const menuItems = [
    {
      name: 'Tableau de bord',
      href: '/dashboard',
      icon: Home,
      roles: ['admin', 'librarian', 'teacher', 'student']
    },
    {
      name: 'Catalogue',
      href: '/books',
      icon: BookOpen,
      roles: ['admin', 'librarian', 'teacher', 'student']
    },
    {
      name: 'Mes Prêts',
      href: '/my-loans',
      icon: BookMarked,
      roles: ['teacher', 'student']
    },
    {
      name: 'Gestion Prêts',
      href: '/loans',
      icon: ClipboardList,
      roles: ['admin', 'librarian']
    },
    {
      name: 'Utilisateurs',
      href: '/users',
      icon: Users,
      roles: ['admin', 'librarian']
    },
    {
      name: 'Statistiques',
      href: '/statistics',
      icon: BarChart3,
      roles: ['admin', 'librarian']
    },
    {
      name: 'Administration',
      href: '/admin',
      icon: Settings,
      roles: ['admin']
    }
  ];

  const filteredMenuItems = menuItems.filter(item => 
    item.roles.includes(user?.role)
  );

  const getRoleDisplay = (role) => {
    const roles = {
      admin: 'Administrateur',
      librarian: 'Bibliothécaire',
      teacher: 'Enseignant',
      student: 'Élève'
    };
    return roles[role] || role;
  };

  const getRoleBadgeColor = (role) => {
    const colors = {
      admin: 'bg-red-100 text-red-800',
      librarian: 'bg-blue-100 text-blue-800',
      teacher: 'bg-green-100 text-green-800',
      student: 'bg-purple-100 text-purple-800'
    };
    return colors[role] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="min-h-screen bg-muted">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-primary transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0 ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between h-16 px-6 bg-primary/90">
            <div className="flex items-center space-x-3">
              <Library className="h-8 w-8 text-white" />
              <span className="text-xl font-bold text-white">BiblioSco</span>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden text-white hover:text-gray-300"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          {/* User info */}
          <div className="px-6 py-4 bg-primary/80 border-b border-primary/60">
            <div className="flex items-center space-x-3 mb-2">
              <div className="h-10 w-10 bg-white/20 rounded-full flex items-center justify-center">
                <User className="h-6 w-6 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">
                  {user?.full_name || user?.email}
                </p>
                <p className="text-xs text-blue-200 truncate">
                  {user?.email}
                </p>
              </div>
            </div>
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRoleBadgeColor(user?.role)}`}>
              {getRoleDisplay(user?.role)}
            </span>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
            {filteredMenuItems.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <button
                  key={item.name}
                  onClick={() => {
                    navigate(item.href);
                    setSidebarOpen(false);
                  }}
                  className={`w-full flex items-center space-x-3 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 ${
                    isActive
                      ? 'bg-white/20 text-white'
                      : 'text-blue-200 hover:bg-white/10 hover:text-white'
                  }`}
                >
                  <item.icon className="h-5 w-5" />
                  <span>{item.name}</span>
                </button>
              );
            })}
          </nav>

          {/* Logout */}
          <div className="p-4 border-t border-primary/60">
            <Button
              onClick={handleLogout}
              variant="ghost"
              className="w-full justify-start text-blue-200 hover:text-white hover:bg-white/10"
            >
              <LogOut className="h-5 w-5 mr-3" />
              Se déconnecter
            </Button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar */}
        <div className="sticky top-0 z-30 bg-white border-b border-gray-200 px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden text-gray-600 hover:text-gray-900"
            >
              <Menu className="h-6 w-6" />
            </button>
            
            <div className="flex items-center space-x-4">
              <h1 className="text-xl font-semibold text-gray-900">
                {menuItems.find(item => item.href === location.pathname)?.name || 'BiblioSco'}
              </h1>
            </div>

            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                Bienvenue, {user?.full_name || user?.email}
              </span>
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;