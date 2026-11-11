import { ChevronDown } from 'lucide-react'
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { EmptyChart } from '../common/EmptyChart'

export default function TransactionChart({ trends }) {
  return (
    <section className="card trend-card"><div className="cardhead"><div><h2>Transaction volume</h2><p>Predictions processed over time</p></div><button className="select">Last 7 days <ChevronDown size={14}/></button></div><div className="chart large">{trends.length?<ResponsiveContainer width="100%" height="100%"><AreaChart data={trends}><defs><linearGradient id="vol" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#62e6bd" stopOpacity={.25}/><stop offset="95%" stopColor="#62e6bd" stopOpacity={0}/></linearGradient></defs><CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--line)"/><XAxis dataKey="date" tick={{fill:'var(--muted)',fontSize:11}} axisLine={false} tickLine={false}/><YAxis tick={{fill:'var(--muted)',fontSize:11}} axisLine={false} tickLine={false}/><Tooltip contentStyle={{background:'var(--panel)',border:'1px solid var(--line)',borderRadius:10,color:'var(--text)'}}/><Area type="monotone" dataKey="transactions" stroke="#62e6bd" fill="url(#vol)" strokeWidth={2}/></AreaChart></ResponsiveContainer>:<EmptyChart text="Transaction activity will appear here after predictions are made."/>}</div><div className="chart-legend"><span><i className="legend-mint"/> All transactions</span><span className="legend-hint">Daily processed volume</span></div></section>
  )
}

