import { useEffect, useState } from 'react';
import axios from 'axios';
import { Plus, Trash2, Smartphone, Wifi, WifiOff } from 'lucide-react';

interface Connection {
  id: number;
  name: string;
  phone_number: string;
  status: string;
}

export default function Connections() {
  const [connections, setConnections] = useState<Connection[]>([]);
  const [isFormOpen, setIsFormOpen] = useState(false);
  
  const [newName, setNewName] = useState("");
  const [newPhone, setNewPhone] = useState("");

  const fetchConnections = () => {
    axios.get('http://127.0.0.1:8000/connections')
      .then(res => setConnections(res.data))
      .catch(err => console.error("Erro ao buscar conexoes", err));
  };

  useEffect(() => {
    fetchConnections();
  }, []);

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName) return;

    axios.post('http://127.0.0.1:8000/connections', {
      name: newName,
      phone_number: newPhone
    })
    .then(() => {
      setIsFormOpen(false);
      setNewName("");
      setNewPhone("");
      fetchConnections();
    })
    .catch(err => alert("Erro ao criar: " + err));
  };

  const handleDelete = (id: number) => {
    if (confirm("Tem a certeza que deseja remover esta conexao?")) {
      axios.delete('http://127.0.0.1:8000/connections/' + id)
        .then(() => fetchConnections())
        .catch(err => alert("Erro ao deletar"));
    }
  };

  const inputStyle = "w-full bg-slate-900 border border-slate-700 rounded p-2 text-white mb-3 focus:outline-none focus:border-blue-500";
  const btnPrimary = "bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded flex items-center gap-2 transition-colors";
  const btnDanger = "text-red-400 hover:text-red-300 p-2 rounded hover:bg-red-400/10 transition-colors";

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-3xl font-bold text-white">Gerir Conexoes</h2>
          <p className="text-slate-400">Adicione e monitorize as suas instancias do WhatsApp</p>
        </div>
        <button onClick={() => setIsFormOpen(!isFormOpen)} className={btnPrimary}>
          <Plus size={20} />
          Nova Conexao
        </button>
      </div>

      {isFormOpen && (
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 mb-8 animate-fade-in">
          <h3 className="text-lg font-semibold text-white mb-4">Nova Instancia</h3>
          <form onSubmit={handleCreate}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <input 
                type="text" 
                placeholder="Nome da Conexao (Ex: Vendas)" 
                className={inputStyle}
                value={newName}
                onChange={e => setNewName(e.target.value)}
              />
              <input 
                type="text" 
                placeholder="Numero (Opcional)" 
                className={inputStyle}
                value={newPhone}
                onChange={e => setNewPhone(e.target.value)}
              />
            </div>
            <div className="flex justify-end gap-2 mt-2">
              <button type="button" onClick={() => setIsFormOpen(false)} className="text-slate-400 hover:text-white px-4 py-2">Cancelar</button>
              <button type="submit" className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded">Salvar</button>
            </div>
          </form>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {connections.map(conn => {
            // Logica de estilo isolada para nao quebrar o PowerShell
            const statusColor = conn.status === 'connected' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400';
            const statusIcon = conn.status === 'connected' ? <Wifi size={14} /> : <WifiOff size={14} />;

            return (
              <div key={conn.id} className="bg-slate-800 rounded-xl border border-slate-700 p-6 flex flex-col justify-between hover:border-blue-500/50 transition-colors">
                
                <div className="flex justify-between items-start mb-4">
                  <div className="p-3 bg-slate-900 rounded-lg text-blue-400">
                    <Smartphone size={24} />
                  </div>
                  <div className={"px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1 " + statusColor}>
                    {statusIcon}
                    {conn.status.toUpperCase()}
                  </div>
                </div>

                <div>
                  <h3 className="text-xl font-bold text-white mb-1">{conn.name}</h3>
                  <p className="text-slate-500 text-sm">{conn.phone_number || "Sem numero definido"}</p>
                </div>

                <div className="border-t border-slate-700 mt-6 pt-4 flex justify-between items-center">
                  <span className="text-xs text-slate-600">ID: {conn.id}</span>
                  <button onClick={() => handleDelete(conn.id)} className={btnDanger} title="Remover">
                    <Trash2 size={18} />
                  </button>
                </div>

              </div>
            );
        })}

        {connections.length === 0 && !isFormOpen && (
          <div className="col-span-full text-center py-12 text-slate-500 border-2 border-dashed border-slate-800 rounded-xl">
            <p>Nenhuma conexao encontrada. Crie a primeira acima!</p>
          </div>
        )}
      </div>
    </div>
  );
}
