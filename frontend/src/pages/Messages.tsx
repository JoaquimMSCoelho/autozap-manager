import { useEffect, useState } from 'react';
import axios from 'axios';
import { Clock, CheckCircle, AlertCircle, RefreshCw } from 'lucide-react';

interface Message {
  id: number;
  phone_dest: string;
  content: string;
  status: string;
  created_at: string;
  connection_id: number;
}

export default function Messages() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchMessages = () => {
    setLoading(true);
    axios.get('http://127.0.0.1:8000/messages')
      .then(res => {
        setMessages(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchMessages();
    
    // Atualiza automaticamente a cada 10 segundos
    const interval = setInterval(fetchMessages, 10000);
    return () => clearInterval(interval);
  }, []);

  // Formatador de data simples
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('pt-BR');
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-3xl font-bold text-white">Logs de Envio</h2>
          <p className="text-slate-400">Historico de todas as mensagens processadas pelo sistema</p>
        </div>
        <button onClick={fetchMessages} className="bg-slate-800 hover:bg-slate-700 text-white px-4 py-2 rounded flex items-center gap-2 border border-slate-700 transition-colors">
          <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
          Atualizar
        </button>
      </div>

      <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden shadow-xl">
        <table className="w-full text-left">
          <thead className="bg-slate-900 text-slate-400 uppercase text-xs font-bold">
            <tr>
              <th className="p-4">ID</th>
              <th className="p-4">Data / Hora</th>
              <th className="p-4">Destino</th>
              <th className="p-4">Mensagem</th>
              <th className="p-4">Instancia ID</th>
              <th className="p-4">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700 text-sm text-slate-300">
            {messages.map(msg => {
              // Logica de status (cores e icones)
              let statusColor = "bg-slate-700 text-slate-300";
              let StatusIcon = Clock;
              
              if (msg.status === 'sent') {
                statusColor = "bg-green-500/20 text-green-400";
                StatusIcon = CheckCircle;
              } else if (msg.status === 'error') {
                statusColor = "bg-red-500/20 text-red-400";
                StatusIcon = AlertCircle;
              } else if (msg.status === 'pending') {
                statusColor = "bg-yellow-500/20 text-yellow-400";
                StatusIcon = Clock;
              }

              return (
                <tr key={msg.id} className="hover:bg-slate-700/50 transition-colors">
                  <td className="p-4 font-mono text-slate-500">#{msg.id}</td>
                  <td className="p-4">{formatDate(msg.created_at)}</td>
                  <td className="p-4 font-bold">{msg.phone_dest}</td>
                  <td className="p-4 truncate max-w-xs" title={msg.content}>{msg.content}</td>
                  <td className="p-4 text-center">{msg.connection_id}</td>
                  <td className="p-4">
                    <span className={"px-3 py-1 rounded-full text-xs font-bold flex items-center gap-2 w-fit " + statusColor}>
                      <StatusIcon size={14} />
                      {msg.status.toUpperCase()}
                    </span>
                  </td>
                </tr>
              );
            })}
            
            {messages.length === 0 && (
              <tr>
                <td colSpan={6} className="p-8 text-center text-slate-500">
                  Nenhum registro encontrado.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
