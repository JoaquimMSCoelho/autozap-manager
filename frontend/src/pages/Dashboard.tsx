import { useState, useEffect } from 'react';
import axios from 'axios';
import { Play, Square, Activity, Send, Clock, AlertTriangle, ShieldCheck } from 'lucide-react';

interface DashboardStats {
  sent_today: number;
  pending: number;
  error_today: number;
  is_running: boolean;
  next_in_queue: Array<{
    id: number;
    phone_dest: string;
    content: string;
    status: string;
  }>;
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loadingAction, setLoadingAction] = useState(false);

  // Busca dados a cada 2 segundos para dar sensacao de "Tempo Real"
  const fetchStats = () => {
    axios.get('http://127.0.0.1:8000/dashboard-stats')
      .then(res => setStats(res.data))
      .catch(err => console.error(err));
  };

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 2000);
    return () => clearInterval(interval);
  }, []);

  const toggleBot = (action: 'start' | 'stop') => {
    setLoadingAction(true);
    axios.post(`http://127.0.0.1:8000/bot/${action}`)
      .then(res => {
        alert(res.data.message);
        fetchStats();
      })
      .catch(err => alert("Erro: " + err.message))
      .finally(() => setLoadingAction(false));
  };

  if (!stats) return <div className="text-white p-10">Carregando Painel de Controle...</div>;

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Cabecalho */}
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2">Painel de Comando</h2>
          <p className="text-slate-400">Visão geral da operação em tempo real</p>
        </div>
        
        {/* Controle do Robo */}
        <div className="flex items-center gap-4 bg-slate-800 p-2 rounded-lg border border-slate-700">
           <div className="text-right mr-2">
              <p className="text-xs text-slate-400 uppercase font-bold">Status do Motor</p>
              <p className={stats.is_running ? "text-green-400 font-bold" : "text-slate-500 font-bold"}>
                {stats.is_running ? "ONLINE ●" : "OFFLINE ○"}
              </p>
           </div>
           
           {!stats.is_running ? (
             <button 
               onClick={() => toggleBot('start')} 
               disabled={loadingAction}
               className="bg-green-600 hover:bg-green-500 text-white p-3 rounded-lg shadow-lg shadow-green-900/20 transition-all flex gap-2 items-center font-bold"
             >
               <Play size={20} fill="currentColor" /> INICIAR ROBÔ
             </button>
           ) : (
             <button 
               onClick={() => toggleBot('stop')} 
               disabled={loadingAction}
               className="bg-red-600 hover:bg-red-500 text-white p-3 rounded-lg shadow-lg shadow-red-900/20 transition-all flex gap-2 items-center font-bold"
             >
               <Square size={20} fill="currentColor" /> PARAR
             </button>
           )}
        </div>
      </div>

      {/* CARDS DE METRICAS */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Card 1: Produtividade Hoje */}
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-xl relative overflow-hidden">
            <div className="absolute top-0 right-0 p-4 opacity-10">
                <Send size={100} />
            </div>
            <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-blue-500/20 rounded-lg text-blue-400">
                    <Send size={24} />
                </div>
                <h3 className="text-slate-400 font-bold text-sm uppercase">Enviadas Hoje</h3>
            </div>
            <p className="text-4xl font-bold text-white mt-2">{stats.sent_today}</p>
            <p className="text-xs text-slate-500 mt-2">Mensagens entregues com sucesso</p>
        </div>

        {/* Card 2: Fila de Espera */}
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-xl relative overflow-hidden">
            <div className="absolute top-0 right-0 p-4 opacity-10">
                <Clock size={100} />
            </div>
            <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-yellow-500/20 rounded-lg text-yellow-400">
                    <Clock size={24} />
                </div>
                <h3 className="text-slate-400 font-bold text-sm uppercase">Fila de Espera</h3>
            </div>
            <p className="text-4xl font-bold text-white mt-2">{stats.pending}</p>
            <p className="text-xs text-slate-500 mt-2">Aguardando disparo</p>
        </div>

        {/* Card 3: Erros/Falhas */}
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-xl relative overflow-hidden">
            <div className="absolute top-0 right-0 p-4 opacity-10">
                <AlertTriangle size={100} />
            </div>
            <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-red-500/20 rounded-lg text-red-400">
                    <Activity size={24} />
                </div>
                <h3 className="text-slate-400 font-bold text-sm uppercase">Erros Hoje</h3>
            </div>
            <p className="text-4xl font-bold text-white mt-2">{stats.error_today}</p>
            <p className="text-xs text-slate-500 mt-2">Falhas de conexão ou número inválido</p>
        </div>
      </div>

      {/* LISTA DE PROXIMOS */}
      <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden shadow-xl mt-8">
          <div className="p-6 border-b border-slate-700 flex justify-between items-center">
              <h3 className="font-bold text-white text-lg flex items-center gap-2">
                  <ShieldCheck className="text-green-500" />
                  Próximos na Fila de Disparo
              </h3>
              <span className="text-xs text-slate-500 bg-slate-900 px-2 py-1 rounded">Atualizado em tempo real</span>
          </div>
          
          {stats.next_in_queue.length === 0 ? (
              <div className="p-10 text-center text-slate-500">
                  <p>A fila está vazia. Bom trabalho! 🍹</p>
              </div>
          ) : (
            <table className="w-full text-left">
                <thead className="bg-slate-900 text-slate-400 uppercase text-xs font-bold">
                    <tr>
                    <th className="p-4">Destino</th>
                    <th className="p-4">Mensagem (Preview)</th>
                    <th className="p-4">Status</th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-slate-700 text-sm text-slate-300">
                    {stats.next_in_queue.map(msg => (
                        <tr key={msg.id} className="hover:bg-slate-700/50">
                            <td className="p-4 font-mono text-blue-300">{msg.phone_dest}</td>
                            <td className="p-4 text-slate-400 truncate max-w-xs">{msg.content}</td>
                            <td className="p-4">
                                <span className="bg-yellow-500/20 text-yellow-400 px-2 py-1 rounded text-xs font-bold">
                                    PENDING
                                </span>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
          )}
      </div>
    </div>
  );
}