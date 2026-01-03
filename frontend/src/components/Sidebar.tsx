import { LayoutDashboard, MessageSquare, Settings, Smartphone, LogOut } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

const Sidebar = () => {
  const location = useLocation();

  const menuItems = [
    { icon: LayoutDashboard, label: 'Dashboard', path: '/' },
    { icon: Smartphone, label: 'Conexoes', path: '/connections' },
    { icon: MessageSquare, label: 'Mensagens', path: '/messages' },
    { icon: Settings, label: 'Configuracoes', path: '/settings' },
  ];

  return (
    <div className="h-screen w-64 bg-slate-900 border-r border-slate-800 flex flex-col text-white">
      <div className="p-6 border-b border-slate-800">
        <h1 className="text-2xl font-bold text-blue-500">AutoZap<span className="text-white">Manager</span></h1>
        <p className="text-xs text-slate-500 mt-1">v1.0.0 Enterprise</p>
      </div>

      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          
          // Logica simplificada para evitar erro no PowerShell
          const baseClass = "flex items-center space-x-3 p-3 rounded-lg transition-all duration-200 ";
          const activeClass = "bg-blue-600 text-white shadow-lg shadow-blue-900/50";
          const inactiveClass = "text-slate-400 hover:bg-slate-800 hover:text-white";
          
          return (
            <Link
              key={item.path}
              to={item.path}
              className={baseClass + (isActive ? activeClass : inactiveClass)}
            >
              <Icon size={20} />
              <span className="font-medium">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-slate-800">
        <button className="flex items-center space-x-3 text-slate-400 hover:text-red-400 p-3 w-full transition-colors">
          <LogOut size={20} />
          <span>Sair do Sistema</span>
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
