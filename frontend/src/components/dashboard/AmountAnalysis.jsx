import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { EmptyChart } from '../common/EmptyChart'

export default function AmountAnalysis({ amounts }) {
  return (
    <section className="card"><div className="cardhead"><div><h2>Transaction amount analysis</h2><p>Amount bands across prediction history</p></div></div>{amounts.length?<ResponsiveContainer width="100%" height={180}><BarChart data={amounts}><CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--line)"/><XAxis dataKey="amount_range" tick={{fill:'var(--muted)',fontSize:9}} axisLine={false} tickLine={false}/><YAxis tick={{fill:'var(--muted)',fontSize:9}} axisLine={false} tickLine={false}/><Tooltip contentStyle={{background:'var(--panel)',border:'1px solid var(--line)',borderRadius:10}}/><Bar dataKey="transactions" fill="#6c9cff" radius={[4,4,0,0]}/><Bar dataKey="fraud" fill="#ff6b78" radius={[4,4,0,0]}/></BarChart></ResponsiveContainer>:<EmptyChart text="Amount bands appear when predictions are recorded."/>}</section>
  )
}

