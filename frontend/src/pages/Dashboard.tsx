import { useEffect, useState } from 'react';
import axios from 'axios';
import { Activity, Server, MessageSquare, Power, RefreshCw } from 'lucide-react';

export default function Dashboard() {
  const [apiStatus, setApiStatus] = useState("Verificando...");
  const [botStatus, setBotStatus] = useState(false);
  const [loading, setLoading] = useState(false);
  
  // Estatisticas (Mock por enquanto)
  const [stats, setStats] = useState({ sent: 0, pending: 0, errors: 0 });

  // Funcao para checar status geral
  const checkStatus = () => {
    // 1. Checa API
    axios.get('http://127.0.0.1:8000/')
      .then(() => setApiStatus("Online"))
      .catch(() => setApiStatus("Offline"));

    // 2. Checa Status do Robo
    axios.get('http://127.0.0.1:8000/bot/status')
      .then(res => setBotStatus(res.data.is_running))
      .catch(() => setBotStatus(false));

    // 3. Atualiza contadores (busca mensagens reais)
    axios.get('http://127.0.0.1:8000/messages')
      .then(res => {
        const msgs = res.data;
        setStats({
          sent: msgs.filter((m: any) => m.status === 'sent').length,
          pending: msgs.filter((m: any) => m.status === 'pending').length,
          errors: msgs.filter((m: any) => m.status === 'error').length
        });
      });
  };

  useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 5000); // Atualiza a cada 5s
    return () => clearInterval(interval);
  }, []);

  // Funcao para Ligar/Desligar Robo
  const toggleBot = () => {
    setLoading(true);
    const endpoint = botStatus ? '/bot/stop' : '/bot/start';
    
    axios.post('http://127.0.0.1:8000' + endpoint)
      .then(res => {
        alert(res.data.message);
        checkStatus();
        setLoading(false);
      })
      .catch(err => {
        alert("Erro ao controlar robo: " + err.message);
        setLoading(false);
      });
  };

  // Variaveis de estilo
  const cardBase = "bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-lg transition-all";
  const textTitle = "text-slate-400 text-sm font-medium mb-1";
  const textValue = "text-2xl font-bold text-white";

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-white">Painel de Controle</h2>
          <span className="text-xs text-slate-500">Monitoramento em Tempo Real</span>
        </div>
        
        {/* Botao Mestre de Controle */}
        <button 
          onClick={toggleBot}
          disabled={loading}
          className={"flex items-center gap-3 px-6 py-3 rounded-lg font-bold shadow-lg transition-all " + 
            (botStatus 
              ? "bg-red-500/20 text-red-400 border border-red-500/50 hover:bg-red-500/30" 
              : "bg-green-600 text-white hover:bg-green-700 hover:shadow-green-900/50")
          }
        >
          <Power size={24} />
          {loading ? "Processando..." : (botStatus ? "DESLIGAR ROBÔ" : "INICIAR ROBÔ")}
        </button>
      </div>

      {/* Grid de Indicadores */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        
        {/* Card 1: Status da API */}
        <div className={cardBase}>
          <div className="flex items-center justify-between">
            <div>
              <p className={textTitle}>Status da API</p>
              <h3 className={textValue}>{apiStatus.toUpperCase()}</h3>
            </div>
            <div className={"p-3 rounded-full " + (apiStatus === "Online" ? "bg-green-500/20 text-green-500" : "bg-red-500/20 text-red-500")}>
              <Server size={24} />
            </div>
          </div>
        </div>

        {/* Card 2: Status do Robo */}
        <div className={cardBase + (botStatus ? " border-green-500/50" : "")}>
          <div className="flex items-center justify-between">
            <div>
              <p className={textTitle}>Motor de Envio</p>
              <h3 className={textValue}>{botStatus ? "RODANDO" : "PARADO"}</h3>
            </div>
            <div className={"p-3 rounded-full " + (botStatus ? "bg-green-500/20 text-green-500 animate-pulse" : "bg-slate-700 text-slate-500")}>
              <Activity size={24} />
            </div>
          </div>
        </div>

        {/* Card 3: Mensagens Enviadas */}
        <div className={cardBase}>
          <div className="flex items-center justify-between">
            <div>
              <p className={textTitle}>Enviadas Hoje</p>
              <h3 className={textValue}>{stats.sent}</h3>
            </div>
            <div className="p-3 rounded-full bg-blue-500/20 text-blue-500">
              <MessageSquare size={24} />
            </div>
          </div>
        </div>

        {/* Card 4: Pendentes */}
        <div className={cardBase}>
          <div className="flex items-center justify-between">
            <div>
              <p className={textTitle}>Na Fila</p>
              <h3 className={textValue}>{stats.pending}</h3>
            </div>
            <div className="p-3 rounded-full bg-orange-500/20 text-orange-500">
              <RefreshCw size={24} />
            </div>
          </div>
        </div>

      </div>

      {/* Instrucoes */}
      {!botStatus && (
        <div className="mt-8 bg-blue-900/20 border border-blue-800 rounded-xl p-6 flex items-start gap-4">
          <div className="p-2 bg-blue-600 rounded-lg text-white mt-1">
            <MessageSquare size={20} />
          </div>
          <div>
            <h4 className="text-lg font-bold text-white">Como Iniciar</h4>
            <p className="text-slate-400 text-sm mt-1">
              1. Clique no botao verde "INICIAR ROBÔ" acima.<br/>
              2. Uma janela do Chrome vai abrir.<br/>
              3. Escaneie o QR Code com o seu WhatsApp.<br/>
              4. O sistema começara a processar a fila de mensagens automaticamente.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
