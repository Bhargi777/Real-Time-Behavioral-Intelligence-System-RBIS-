import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { Activity, Users, Clock, AlertCircle } from 'lucide-react';

const RBISDashboard = () => {
  const [data, setData] = useState([]);
  const [engagementHistory, setEngagementHistory] = useState([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/analytics');
    
    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onmessage = (event) => {
      const update = JSON.parse(event.data);
      if (update.persons) {
        setData(update.persons);
        
        // Compute average engagement for chart
        const avgEng = update.persons.reduce((sum, p) => sum + p.engagement_score, 0) / (update.persons.length || 1);
        setEngagementHistory(prev => [...prev.slice(-20), { time: new Date().toLocaleTimeString(), score: avgEng }]);
      }
    };

    return () => ws.close();
  }, []);

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-8 font-sans">
      <header className="flex justify-between items-center mb-8 border-b border-slate-700 pb-4">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
            RBIS Live Analytics
          </h1>
          <p className="text-slate-400">Behavioral Intelligence Pipeline v1.0</p>
        </div>
        <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm ${connected ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
          <div className={`w-2 h-2 rounded-full ${connected ? 'bg-emerald-400' : 'bg-rose-400'} animate-pulse`} />
          {connected ? 'Streaming Live' : 'Disconnected'}
        </div>
      </header>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <MetricCard label="Active Persons" value={data.length} icon={<Users className="w-5 h-5" />} />
        <MetricCard label="Avg Engagement" value={`${Math.round(engagementHistory[engagementHistory.length-1]?.score || 0)}%`} icon={<Activity className="w-5 h-5" />} />
        <MetricCard label="Active Alerts" value={data.filter(p => p.events.length > 0).length} icon={<AlertCircle className="w-5 h-5" />} />
        <MetricCard label="System Latency" value="~35ms" icon={<Clock className="w-5 h-5" />} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Engagement Timeline */}
        <div className="bg-slate-800 p-6 rounded-2xl border border-slate-700">
          <h3 className="text-lg font-semibold mb-6">Engagement Trends</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={engagementHistory}>
                <defs>
                  <linearGradient id="engColor" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="time" stroke="#94a3b8" fontSize={12} />
                <YAxis stroke="#94a3b8" fontSize={12} domain={[0, 100]} />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px' }} />
                <Area type="monotone" dataKey="score" stroke="#10b981" fillOpacity={1} fill="url(#engColor)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Live Tracking Table */}
        <div className="bg-slate-800 p-6 rounded-2xl border border-slate-700 overflow-hidden">
          <h3 className="text-lg font-semibold mb-6 text-slate-100">Person Tracking Feed</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-slate-700 text-slate-400 text-sm">
                  <th className="pb-3 px-2">ID</th>
                  <th className="pb-3 px-2">Events</th>
                  <th className="pb-3 px-2">Eng Score</th>
                  <th className="pb-3 px-2 text-right">Status</th>
                </tr>
              </thead>
              <tbody>
                {data.map(person => (
                  <tr key={person.id} className="border-b last:border-0 border-slate-700/50 hover:bg-slate-700/30 transition-colors">
                    <td className="py-4 px-2 font-mono text-blue-400">#00{person.id}</td>
                    <td className="py-4 px-2">
                      <div className="flex gap-1 flex-wrap">
                        {person.events.map(e => (
                          <span key={e} className="px-2 py-0.5 rounded text-xs bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 capitalize">{e.replace('_', ' ')}</span>
                        ))}
                      </div>
                    </td>
                    <td className="py-4 px-2 text-slate-300 font-medium">{person.engagement_score}%</td>
                    <td className="py-4 px-2 text-right">
                      <span className="w-2 h-2 rounded-full inline-block bg-emerald-400" />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

const MetricCard = ({ label, value, icon }) => (
  <div className="bg-slate-800 p-5 rounded-2xl border border-slate-700 flex items-center gap-4">
    <div className="p-3 bg-slate-900 rounded-xl text-blue-400 shadow-inner">
      {icon}
    </div>
    <div>
      <p className="text-slate-400 text-sm mb-1">{label}</p>
      <h4 className="text-2xl font-bold text-slate-100">{value}</h4>
    </div>
  </div>
);

export default RBISDashboard;
