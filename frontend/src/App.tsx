import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, MessageSquare, Settings, Users, LogOut } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Messages from './pages/Messages';
import SettingsPage from './pages/Settings';
import Contacts from './pages/Contacts';

function App() {
  return (
    <Router>
      <MainLayout />
    </Router>
  );
}

function MainLayout() {
  const location = useLocation();

  // Funcao para verificar se o link esta ativo
  const isActive = (path: string) => {
    return location.pathname === path 
      ? "bg-blue-600 text-white shadow-lg shadow-blue-900/50" 
      : "text-slate-400 hover:bg-slate-800 hover:text-white";
  };

  const navItemClass = "flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-medium mb-1";

  return (
    <div className="flex h-screen bg-slate-950 text-slate-200 overflow-hidden font-sans selection:bg-blue-500/30">
      
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col p-6 shadow-2xl z-10">
        <div className="mb-10 flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-tr from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center shadow-lg shadow-blue-900/20">
            <MessageSquare className="text-white" size={24} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight">AutoZap</h1>
            <span className="text-xs text-blue-400 font-bold tracking-wider uppercase">Manager</span>
          </div>
        </div>

        <nav className="flex-1 space-y-2">
          {/* Note o uso de aspas invertidas (crases) abaixo, essenciais para o React */}
          <Link to="/" className={`${navItemClass} ${isActive('/')}`}>
            <LayoutDashboard size={20} />
            Dashboard
          </Link>

          <Link to="/contacts" className={`${navItemClass} ${isActive('/contacts')}`}>
            <Users size={20} />
            Contatos
          </Link>

          <Link to="/messages" className={`${navItemClass} ${isActive('/messages')}`}>
            <MessageSquare size={20} />
            Mensagens
          </Link>

          <Link to="/settings" className={`${navItemClass} ${isActive('/settings')}`}>
            <Settings size={20} />
            Configurações
          </Link>
        </nav>

        <div className="pt-6 border-t border-slate-800">
          <button className="flex items-center gap-3 px-4 py-3 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-xl transition-colors w-full">
            <LogOut size={20} />
            Sair do Sistema
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto bg-slate-950 relative">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-slate-950 to-slate-950 pointer-events-none" />
        <div className="p-8 max-w-7xl mx-auto relative z-0">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/messages" element={<Messages />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="/contacts" element={<Contacts />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}

export default App;