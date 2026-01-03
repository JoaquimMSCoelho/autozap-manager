import { useEffect, useState } from 'react';
import axios from 'axios';
import { Save, Settings as SettingsIcon, Zap } from 'lucide-react';

interface ConfigItem {
  key_name: string;
  value: string;
  is_active: boolean;
}

export default function Settings() {
  // Estados locais para os valores do formulario
  const [interval, setIntervalVal] = useState("15");
  const [isSystemActive, setIsSystemActive] = useState(true);
  const [loading, setLoading] = useState(false);

  // Carregar do Backend
  useEffect(() => {
    axios.get('http://127.0.0.1:8000/configs')
      .then(res => {
        const data: ConfigItem[] = res.data;
        
        // Mapeia o array que vem do banco para os estados da tela
        const intervalConfig = data.find(c => c.key_name === 'message_interval');
        const activeConfig = data.find(c => c.key_name === 'system_global_active');

        if (intervalConfig) setIntervalVal(intervalConfig.value);
        if (activeConfig) setIsSystemActive(activeConfig.value === 'true');
      })
      .catch(console.error);
  }, []);

  // Salvar no Backend
  const handleSave = () => {
    setLoading(true);
    
    // Salva o intervalo
    const p1 = axios.post('http://127.0.0.1:8000/configs', {
      key_name: 'message_interval',
      value: interval,
      is_active: true
    });

    // Salva o status global
    const p2 = axios.post('http://127.0.0.1:8000/configs', {
      key_name: 'system_global_active',
      value: isSystemActive ? 'true' : 'false',
      is_active: true
    });

    Promise.all([p1, p2])
      .then(() => {
        alert("Configuracoes salvas com sucesso!");
        setLoading(false);
      })
      .catch(err => {
        alert("Erro ao salvar.");
        setLoading(false);
      });
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-3xl font-bold text-white">Configuracoes</h2>
          <p className="text-slate-400">Ajustes globais do comportamento do sistema</p>
        </div>
      </div>

      <div className="bg-slate-800 rounded-xl border border-slate-700 p-8 max-w-2xl">
        
        {/* Switch: Sistema Ativo */}
        <div className="flex items-center justify-between mb-8 pb-8 border-b border-slate-700">
          <div className="flex items-center gap-4">
            <div className={"p-3 rounded-lg " + (isSystemActive ? "bg-green-500/20 text-green-500" : "bg-red-500/20 text-red-500")}>
              <Zap size={24} />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">Status do Robô</h3>
              <p className="text-slate-400 text-sm">Liga ou desliga o envio automatico de mensagens</p>
            </div>
          </div>
          
          <button 
            onClick={() => setIsSystemActive(!isSystemActive)}
            className={"relative inline-flex h-8 w-14 items-center rounded-full transition-colors " + (isSystemActive ? "bg-green-600" : "bg-slate-600")}
          >
            <span className={"inline-block h-6 w-6 transform rounded-full bg-white transition-transform " + (isSystemActive ? "translate-x-7" : "translate-x-1")} />
          </button>
        </div>

        {/* Input: Intervalo */}
        <div className="mb-8">
          <label className="block text-slate-300 font-bold mb-2 flex items-center gap-2">
            <SettingsIcon size={16} />
            Intervalo entre Envios (segundos)
          </label>
          <p className="text-xs text-slate-500 mb-3">Tempo de espera seguro para evitar bloqueios do WhatsApp.</p>
          <input 
            type="number" 
            className="w-full bg-slate-900 border border-slate-700 rounded p-3 text-white focus:border-blue-500 focus:outline-none"
            value={interval}
            onChange={(e) => setIntervalVal(e.target.value)}
          />
        </div>

        {/* Botao Salvar */}
        <div className="flex justify-end">
          <button 
            onClick={handleSave}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-bold flex items-center gap-2 transition-all disabled:opacity-50"
          >
            <Save size={20} />
            {loading ? "Salvando..." : "Salvar Alteracoes"}
          </button>
        </div>

      </div>
    </div>
  );
}
