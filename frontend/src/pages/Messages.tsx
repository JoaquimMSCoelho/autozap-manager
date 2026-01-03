import { useEffect, useState } from 'react';
import axios from 'axios';
import { Clock, CheckCircle, AlertCircle, RefreshCw, Send, X } from 'lucide-react';

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
  
  // Estados do Modal de Envio
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newPhone, setNewPhone] = useState("");
  const [newText, setNewText] = useState("");
  const [sending, setSending] = useState(false);

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
    const interval = setInterval(fetchMessages, 5000);
    return () => clearInterval(interval);
  }, []);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('pt-BR');
  };

  // Funcao para enviar mensagem manual
  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    setSending(true);

    axios.post('http://127.0.0.1:8000/messages', {
      phone_dest: newPhone,
      content: newText,
      connection_id: 1 // Usando a conexao padrao 1
    })
    .then(() => {
      alert("Mensagem agendada com sucesso!");
      setIsModalOpen(false);
      setNewPhone("");
      setNewText("");
      setSending(false);
      fetchMessages(); // Atualiza a lista
    })
    .catch(err => {
      alert("Erro ao agendar: " + err.message);
      setSending(false);
    });
  };

  // Estilos
  const inputStyle = "w-full bg-slate-900 border border-slate-700 rounded p-3 text-white focus:border-blue-500 focus:outline-none mb-4";

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-3xl font-bold text-white">Logs de Envio</h2>
          <p className="text-slate-400">Historico e fila de processamento</p>
        </div>
        <div className="flex gap-3">
            <button onClick={fetchMessages} className="bg-slate-800 hover:bg-slate-700 text-white px-4 py-2 rounded flex items-center gap-2 border border-slate-700 transition-colors">
            <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
            </button>
            <button onClick={() => setIsModalOpen(true)} className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded flex items-center gap-2 transition-colors font-bold shadow-lg shadow-blue-900/50">
            <Send size={18} />
            Nova Mensagem
            </button>
        </div>
      </div>

      {/* Modal de Envio Manual */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 w-full max-w-md shadow-2xl animate-fade-in">
                <div className="flex justify-between items-center mb-6">
                    <h3 className="text-xl font-bold text-white">Novo Disparo</h3>
                    <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-white">
                        <X size={24} />
                    </button>
                </div>
                
                <form onSubmit={handleSend}>
                    <label className="block text-slate-400 text-sm mb-1">Numero (com DDI e DDD)</label>
                    <input 
                        type="text" 
                        placeholder="Ex: 5511999999999" 
                        className={inputStyle}
                        value={newPhone}
                        onChange={e => setNewPhone(e.target.value)}
                        required
                    />

                    <label className="block text-slate-400 text-sm mb-1">Mensagem</label>
                    <textarea 
                        rows={4}
                        placeholder="Digite o conteudo..." 
                        className={inputStyle}
                        value={newText}
                        onChange={e => setNewText(e.target.value)}
                        required
                    />

                    <button 
                        type="submit" 
                        disabled={sending}
                        className="w-full bg-green-600 hover:bg-green-700 text-white py-3 rounded-lg font-bold transition-colors disabled:opacity-50"
                    >
                        {sending ? "Agendando..." : "Adicionar a Fila"}
                    </button>
                </form>
            </div>
        </div>
      )}

      <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden shadow-xl">
        <table className="w-full text-left">
          <thead className="bg-slate-900 text-slate-400 uppercase text-xs font-bold">
            <tr>
              <th className="p-4">ID</th>
              <th className="p-4">Data</th>
              <th className="p-4">Destino</th>
              <th className="p-4">Mensagem</th>
              <th className="p-4">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700 text-sm text-slate-300">
            {messages.map(msg => {
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
                  <td className="p-4">
                    <span className={"px-3 py-1 rounded-full text-xs font-bold flex items-center gap-2 w-fit " + statusColor}>
                      <StatusIcon size={14} />
                      {msg.status.toUpperCase()}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
