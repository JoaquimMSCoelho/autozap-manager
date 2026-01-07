import { useEffect, useState } from 'react';
import axios from 'axios';
import { Play, Square, Activity, AlertTriangle, Send } from 'lucide-react';

export default function Dashboard() {
  const [stats, setStats] = useState({
    sent_today: 0,
    pending: 0,
    error_today: 0,
    is_running: false,
    next_in_queue: []
  });

  const [loading, setLoading] = useState(false);
  const [configInterval, setConfigInterval] = useState(15);

  const fetchStats = () => {
    axios.get('http://127.0.0.1:8000/dashboard-stats')
      .then(res => setStats(res.data))
      .catch(err => console.error("Erro ao buscar stats:", err));
  };

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 2000); // Atualiza a cada 2s
    return () => clearInterval(interval);
  }, []);

  const handleStartBot = () => {
    setLoading(true);
    axios.post('http://127.0.0.1:8000/bot/start')
      .then(() => {
        // REMOVIDO: alert("Navegador iniciado.");
        console.log("Motor de envio iniciado.");
        fetchStats();
      })
      .catch(err => alert("Erro ao iniciar: " + err.message))
      .finally(() => setLoading(false));
  };

  const handleStopBot = () => {
    setLoading(true);
    axios.post('http://127.0.0.1:8000/bot/stop')
      .then(() => {
        // REMOVIDO: alert("Navegador fechado.");
        console.log("Motor de envio parado.");
        fetchStats();
      })
      .catch(err => alert("Erro ao parar: " + err.message))
      .finally(() => setLoading(false));
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-3xl font-bold text-white">Painel de Comando</h2>
          <p className="text-slate-400">Visão geral da operação em tempo real</p>
        </div>
        
        <div className="bg-slate-800 p-2 rounded-lg border border-slate-700 flex items-center gap-4">
            <div className="text-right">
                <p className="text-xs text-slate-400 font-bold uppercase">Status do Motor</p>
                <div className="flex items-center gap-2 justify-end">
                    {stats.is_running ? (
                        <span className="text-green-400 font-bold flex items-center gap-1 text-sm">
                            ONLINE <span className="relative flex h-3 w-3"><span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span><span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span></span>
                        </span>
                    ) : (
                        <span className="text-slate-500 font-bold text-sm">OFFLINE ○</span>
                    )}
                </div>
            </div>

            {stats.is_running ? (
                <button 
                    onClick={handleStopBot} 
                    disabled={loading}
                    className="bg-red-600 hover:bg-red-700 text-white px-6 py-2 rounded font-bold flex items-center gap-2 transition-all shadow-lg shadow-red-900/50"
                >
                    {loading ? "..." : <><Square size={18} fill="white" /> PARAR</>}
                </button>
            ) : (
                <button 
                    onClick={handleStartBot} 
                    disabled={loading}
                    className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded font-bold flex items-center gap-2 transition-all shadow-lg shadow-green-900/50"
                >
                    {loading ? "..." : <><Play size={18} fill="white" /> INICIAR ROBÔ</>}
                </button>
            )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Card Enviadas */}
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-xl relative overflow-hidden group hover:border-blue-500/50 transition-colors">
            <div className="absolute right-0 top-0 p-6 opacity-10 group-hover:opacity-20 transition-opacity">
                <Send size={100} />
            </div>
            <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-blue-500/20 rounded-lg text-blue-400">
                    <Send size={24} />
                </div>
                <h3 className="font-bold text-slate-300 text-sm uppercase">Enviadas Hoje</h3>
            </div>
            <p className="text-4xl font-bold text-white mb-1">{stats.sent_today}</p>
            <p className="text-xs text-slate-500">Mensagens entregues com sucesso</p>
        </div>

        {/* Card Fila */}
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-xl relative overflow-hidden group hover:border-yellow-500/50 transition-colors">
            <div className="absolute right-0 top-0 p-6 opacity-10 group-hover:opacity-20 transition-opacity">
                <Activity size={100} />
            </div>
            <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-yellow-500/20 rounded-lg text-yellow-400">
                    <Activity size={24} />
                </div>
                <h3 className="font-bold text-slate-300 text-sm uppercase">Fila de Espera</h3>
            </div>
            <p className="text-4xl font-bold text-white mb-1">{stats.pending}</p>
            <p className="text-xs text-slate-500">Aguardando disparo</p>
        </div>

        {/* Card Erros */}
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-xl relative overflow-hidden group hover:border-red-500/50 transition-colors">
            <div className="absolute right-0 top-0 p-6 opacity-10 group-hover:opacity-20 transition-opacity">
                <AlertTriangle size={100} />
            </div>
            <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-red-500/20 rounded-lg text-red-400">
                    <AlertTriangle size={24} />
                </div>
                <h3 className="font-bold text-slate-300 text-sm uppercase">Erros Hoje</h3>
            </div>
            <p className="text-4xl font-bold text-white mb-1">{stats.error_today}</p>
            <p className="text-xs text-slate-500">Falhas de conexão ou número inválido</p>
        </div>
      </div>

      <div className="bg-slate-900/50 p-6 rounded-xl border border-slate-800">
        <h3 className="flex items-center gap-2 font-bold text-white mb-4">
            <Activity size={20} className="text-green-500" />
            Próximos na Fila de Disparo
            <span className="ml-auto text-xs bg-slate-800 px-2 py-1 rounded text-slate-500 font-normal">Atualizado em tempo real</span>
        </h3>
        
        {stats.next_in_queue && stats.next_in_queue.length > 0 ? (
            <div className="space-y-3">
                {stats.next_in_queue.map((msg: any) => (
                    <div key={msg.id} className="bg-slate-800 p-4 rounded-lg flex justify-between items-center border border-slate-700">
                        <div>
                            <p className="font-bold text-white">{msg.phone_dest}</p>
                            <p className="text-xs text-slate-400 truncate max-w-md">{msg.content}</p>
                        </div>
                        <span className="text-xs font-bold bg-yellow-500/10 text-yellow-500 px-3 py-1 rounded-full border border-yellow-500/20">
                            AGUARDANDO
                        </span>
                    </div>
                ))}
            </div>
        ) : (
            <div className="text-center py-8 text-slate-500">
                <p>A fila está vazia. Bom trabalho! 🍹</p>
            </div>
        )}
      </div>
    </div>
  );
}