import { useEffect, useState } from 'react';
import axios from 'axios';
import { Activity, Server, MessageSquare, ShieldCheck } from 'lucide-react';

export default function Dashboard() {
  const [apiStatus, setApiStatus] = useState("Verificando...");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Busca o status real do Backend Python
    axios.get('http://127.0.0.1:8000/')
      .then(res => {
        setApiStatus(res.data.status || "Online");
        setLoading(false);
      })
      .catch(() => {
        setApiStatus("Offline");
        setLoading(false);
      });
  }, []);

  // Variaveis de estilo para evitar conflito no PowerShell
  const cardBase = "bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-lg";
  const textTitle = "text-slate-400 text-sm font-medium mb-1";
  const textValue = "text-2xl font-bold text-white";

  // Logica de cor do icone baseada no status
  const iconColor = apiStatus === "online" ? "bg-green-500/20 text-green-500" : "bg-red-500/20 text-red-500";

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold text-white">Painel de Controle</h2>
        <span className="text-xs text-slate-500">Atualizado em tempo real</span>
      </div>

      {/* Grid de Indicadores */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        
        {/* Card 1: Status do Sistema */}
        <div className={cardBase}>
          <div className="flex items-center justify-between">
            <div>
              <p className={textTitle}>Status da API</p>
              <h3 className={textValue}>{loading ? "..." : apiStatus.toUpperCase()}</h3>
            </div>
            <div className={"p-3 rounded-full " + iconColor}>
              <Server size={24} />
            </div>
          </div>
        </div>

        {/* Card 2: Dispositivos (Mock) */}
        <div className={cardBase}>
          <div className="flex items-center justify-between">
            <div>
              <p className={textTitle}>WhatsApp Conectado</p>
              <h3 className={textValue}>Nao</h3>
            </div>
            <div className="p-3 rounded-full bg-orange-500/20 text-orange-500">
              <ShieldCheck size={24} />
            </div>
          </div>
        </div>

        {/* Card 3: Mensagens (Mock) */}
        <div className={cardBase}>
          <div className="flex items-center justify-between">
            <div>
              <p className={textTitle}>Mensagens Hoje</p>
              <h3 className={textValue}>0</h3>
            </div>
            <div className="p-3 rounded-full bg-blue-500/20 text-blue-500">
              <MessageSquare size={24} />
            </div>
          </div>
        </div>

        {/* Card 4: Atividade (Mock) */}
        <div className={cardBase}>
          <div className="flex items-center justify-between">
            <div>
              <p className={textTitle}>Fila de Envio</p>
              <h3 className={textValue}>0</h3>
            </div>
            <div className="p-3 rounded-full bg-purple-500/20 text-purple-500">
              <Activity size={24} />
            </div>
          </div>
        </div>

      </div>

      {/* Area de Graficos ou Listas Futuras */}
      <div className="mt-8 bg-slate-900 rounded-xl border border-slate-800 p-6">
        <h3 className="text-xl font-bold text-white mb-4">Ultimas Atividades do Sistema</h3>
        <div className="text-slate-400 text-sm text-center py-10">
          Nenhuma atividade registrada no momento.
        </div>
      </div>
    </div>
  );
}
