import { useEffect, useState } from 'react';
import axios from 'axios';
import { Clock, CheckCircle, AlertCircle, RefreshCw, Send, X, Users, Smartphone, Paperclip, Trash2 } from 'lucide-react';

interface Message {
  id: number;
  phone_dest: string;
  content: string;
  status: string;
  created_at: string;
  connection_id: number;
}

interface Group {
  id: number;
  name: string;
  contact_count: number;
}

export default function Messages() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [groups, setGroups] = useState<Group[]>([]);
  const [loading, setLoading] = useState(false);
  
  // Estados do Modal
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [sendMode, setSendMode] = useState<'single' | 'group'>('single');
  
  // Formulario
  const [targetPhone, setTargetPhone] = useState("");
  const [selectedGroupId, setSelectedGroupId] = useState("");
  const [msgContent, setMsgContent] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [sending, setSending] = useState(false);

  const fetchData = () => {
    setLoading(true);
    axios.get('http://127.0.0.1:8000/messages')
      .then(res => {
        setMessages(res.data);
        setLoading(false);
      });
      
    axios.get('http://127.0.0.1:8000/groups')
      .then(res => setGroups(res.data));
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('pt-BR');
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    setSending(true);

    try {
        if (sendMode === 'single') {
            const formData = new FormData();
            formData.append('phone_dest', targetPhone);
            formData.append('content', msgContent || " ");
            formData.append('connection_id', "1");
            
            if (selectedFile) {
                formData.append('file', selectedFile);
            }

            await axios.post('http://127.0.0.1:8000/messages', formData);
            finishSubmit();

        } else {
            await axios.post('http://127.0.0.1:8000/broadcast', {
                group_id: parseInt(selectedGroupId),
                content: msgContent,
                connection_id: 1
            });
            finishSubmit();
        }
    } catch (err: any) {
        handleError(err);
    }
  };

  const finishSubmit = () => {
    console.log("Envio realizado com sucesso.");
    setIsModalOpen(false);
    setMsgContent("");
    setTargetPhone("");
    setSelectedFile(null);
    setSending(false);
    fetchData();
  };

  const handleError = (err: any) => {
    console.error(err);
    alert("Erro ao processar: " + (err.response?.data?.detail || err.message));
    setSending(false);
  };

  const inputStyle = `w-full bg-slate-900 border border-slate-700 rounded p-3 text-white focus:border-blue-500 focus:outline-none mb-4`;

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-3xl font-bold text-white">Central de Disparos</h2>
          <p className="text-slate-400">Gerencie filas e campanhas</p>
        </div>
        <div className="flex gap-3">
            <button onClick={fetchData} className="bg-slate-800 hover:bg-slate-700 text-white px-4 py-2 rounded flex items-center gap-2 border border-slate-700 transition-colors">
            <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
            </button>
            <button onClick={() => setIsModalOpen(true)} className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded flex items-center gap-2 transition-colors font-bold shadow-lg shadow-blue-900/50">
            <Send size={18} />
            Criar Campanha
            </button>
        </div>
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 w-full max-w-md shadow-2xl animate-fade-in">
                <div className="flex justify-between items-center mb-6">
                    <h3 className="text-xl font-bold text-white">Nova Campanha</h3>
                    <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-white">
                        <X size={24} />
                    </button>
                </div>
                
                <div className="flex bg-slate-900 p-1 rounded-lg mb-6">
                    <button 
                        onClick={() => setSendMode('single')}
                        className={`flex-1 py-2 text-sm font-bold rounded-md flex items-center justify-center gap-2 transition-all ${sendMode === 'single' ? 'bg-slate-700 text-white shadow' : 'text-slate-500 hover:text-slate-300'}`}
                    >
                        <Smartphone size={16} /> Individual
                    </button>
                    <button 
                        onClick={() => setSendMode('group')}
                        className={`flex-1 py-2 text-sm font-bold rounded-md flex items-center justify-center gap-2 transition-all ${sendMode === 'group' ? 'bg-blue-600 text-white shadow' : 'text-slate-500 hover:text-slate-300'}`}
                    >
                        <Users size={16} /> Grupo / Todos
                    </button>
                </div>

                <form onSubmit={handleSend}>
                    {sendMode === 'single' ? (
                        <>
                            <label className="block text-slate-400 text-sm mb-1">Numero de Destino</label>
                            <input 
                                type="text" 
                                placeholder="Ex: 5511999999999" 
                                className={inputStyle}
                                value={targetPhone}
                                onChange={e => setTargetPhone(e.target.value)}
                                required
                            />
                        </>
                    ) : (
                        <>
                            <label className="block text-slate-400 text-sm mb-1">Selecione o Público</label>
                            <select 
                                className={inputStyle}
                                value={selectedGroupId}
                                onChange={e => setSelectedGroupId(e.target.value)}
                                required
                            >
                                <option value="">-- Escolha um segmento --</option>
                                <option value="-1" className="font-bold text-yellow-400">📢 ENVIAR PARA TODA A LISTA (GERAL)</option>
                                {groups.map(g => (
                                    <option key={g.id} value={g.id}>
                                        {g.name} ({g.contact_count} contatos)
                                    </option>
                                ))}
                            </select>
                        </>
                    )}

                    <label className="block text-slate-400 text-sm mb-1">Conteúdo da Mensagem</label>
                    <textarea 
                        rows={4}
                        placeholder="Digite sua mensagem aqui..." 
                        className={inputStyle}
                        value={msgContent}
                        onChange={e => setMsgContent(e.target.value)}
                    />

                    {sendMode === 'single' && (
                        <div className="mb-4">
                            <label className="block text-slate-400 text-sm mb-1">Anexar Mídia (Opcional)</label>
                            <div className="flex items-center gap-2">
                                <label className="cursor-pointer bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded flex items-center gap-2 border border-slate-600 transition-colors w-full justify-center border-dashed border-2">
                                    <Paperclip size={16} />
                                    <span className="text-sm">{selectedFile ? selectedFile.name : "Escolher Arquivo"}</span>
                                    <input type="file" className="hidden" onChange={handleFileChange} />
                                </label>
                                {selectedFile && (
                                    <button 
                                        type="button" 
                                        onClick={() => setSelectedFile(null)}
                                        className="bg-red-500/20 text-red-400 p-2 rounded hover:bg-red-500/30"
                                    >
                                        <Trash2 size={18} />
                                    </button>
                                )}
                            </div>
                        </div>
                    )}

                    <button 
                        type="submit" 
                        disabled={sending}
                        className={`w-full py-3 rounded-lg font-bold transition-colors disabled:opacity-50 ${sendMode === 'group' ? 'bg-blue-600 hover:bg-blue-700 text-white' : 'bg-green-600 hover:bg-green-700 text-white'}`}
                    >
                        {sending ? "Processando..." : (
                            sendMode === 'group' 
                                ? (selectedGroupId === "-1" ? "⚠️ Disparar para TODOS" : "Disparar para Grupo") 
                                : "Enviar Mensagem"
                        )}
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
                    <span className={`px-3 py-1 rounded-full text-xs font-bold flex items-center gap-2 w-fit ${statusColor}`}>
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