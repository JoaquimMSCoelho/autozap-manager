import { useEffect, useState } from 'react';
import axios from 'axios';
import { Users, Upload, Folder, RefreshCw } from 'lucide-react';

interface Group {
  id: number;
  name: string;
  contact_count: number;
}

export default function Contacts() {
  const [groups, setGroups] = useState<Group[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [summary, setSummary] = useState("");

  const fetchGroups = () => {
    setLoading(true);
    axios.get('http://127.0.0.1:8000/groups')
      .then(res => {
        setGroups(res.data);
        setLoading(false);
      })
      .catch(console.error);
  };

  useEffect(() => {
    fetchGroups();
  }, []);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    
    setUploading(true);
    setSummary("");
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append("file", file);

    axios.post('http://127.0.0.1:8000/import-contacts', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    .then(res => {
      // Aqui estava o erro: agora usamos crases (backticks) corretamente
      setSummary(`Sucesso! ${res.data.imported} novos contatos importados.`);
      setUploading(false);
      fetchGroups(); 
    })
    .catch(err => {
      setSummary("Erro na importacao: " + err.message);
      setUploading(false);
    });
  };

  return (
    <div className="space-y-8">
      {/* Cabecalho */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-white">Gestão de Contatos</h2>
          <p className="text-slate-400">Importe listas e gerencie seus segmentos</p>
        </div>
      </div>

      {/* Area de Upload */}
      <div className="bg-slate-800 p-8 rounded-xl border-2 border-dashed border-slate-600 hover:border-blue-500 transition-colors text-center group">
        <div className="flex flex-col items-center gap-4">
          <div className="p-4 bg-slate-700 rounded-full group-hover:bg-blue-500/20 group-hover:text-blue-400 transition-colors">
            {uploading ? <RefreshCw className="animate-spin" size={32} /> : <Upload size={32} />}
          </div>
          
          <div>
            <h3 className="text-xl font-bold text-white">Importar Lista (Excel / CSV)</h3>
            <p className="text-slate-400 text-sm mt-1 mb-4">
              O arquivo deve conter colunas: <strong>nome</strong> e <strong>telefone</strong>.<br/>
              Use siglas como <strong>[INF]</strong> ou <strong>[AD]</strong> no nome para criar grupos automaticamente.
            </p>
          </div>

          <label className="cursor-pointer bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-bold transition-colors shadow-lg">
            Escolher Arquivo
            <input type="file" className="hidden" accept=".xlsx,.csv" onChange={handleFileUpload} disabled={uploading} />
          </label>

          {summary && (
            <div className={"mt-4 p-3 rounded text-sm font-bold " + (summary.includes("Erro") ? "bg-red-500/20 text-red-400" : "bg-green-500/20 text-green-400")}>
              {summary}
            </div>
          )}
        </div>
      </div>

      {/* Grid de Grupos */}
      <div>
        <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
          <Folder size={20} />
          Seus Segmentos
        </h3>
        
        {loading ? (
          <p className="text-slate-500">Carregando grupos...</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {groups.map(group => (
              <div key={group.id} className="bg-slate-800 p-6 rounded-xl border border-slate-700 hover:border-slate-500 transition-all shadow-lg">
                <div className="flex justify-between items-start mb-4">
                  <div className="p-3 bg-indigo-500/20 text-indigo-400 rounded-lg">
                    <Users size={24} />
                  </div>
                  <span className="text-xs font-bold text-slate-500 bg-slate-900 px-2 py-1 rounded">
                    ID: {group.id}
                  </span>
                </div>
                
                <h4 className="text-lg font-bold text-white">{group.name}</h4>
                <p className="text-slate-400 text-sm">{group.contact_count} contatos</p>
                
                <div className="mt-4 pt-4 border-t border-slate-700 flex gap-2">
                    <button className="text-xs bg-slate-700 hover:bg-slate-600 text-white px-3 py-1 rounded w-full transition-colors">
                        Ver Lista
                    </button>
                </div>
              </div>
            ))}
            
            {groups.length === 0 && (
                <div className="col-span-full text-center py-10 text-slate-500 border border-slate-700 rounded-xl bg-slate-800/50">
                    Nenhum grupo encontrado. Importe uma lista acima!
                </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}