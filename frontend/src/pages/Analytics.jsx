import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { EmptyChart } from '../components/common/EmptyChart'
import MetricCard from '../components/dashboard/MetricCard'

export default function Analytics({ metricCards, trends }) {
  return (
    <><div className="pagehead"><div><div className="eyebrow">FRAUD INSIGHTS</div><h1>Analytics</h1><p>Activity trends from recorded model predictions.</p></div></div><div className="metrics compact">{metricCards.map(card=><MetricCard key={card[0]} card={card} compact/>)}</div><section className="card analytics-chart"><div className="cardhead"><div><h2>Daily activity and fraud flags</h2><p>Counts by prediction date</p></div></div>{trends.length?<ResponsiveContainer width="100%" height={320}><BarChart data={trends}><CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--line)"/><XAxis dataKey="date" tick={{fill:'var(--muted)',fontSize:11}} axisLine={false} tickLine={false}/><YAxis tick={{fill:'var(--muted)',fontSize:11}} axisLine={false} tickLine={false}/><Tooltip contentStyle={{background:'var(--panel)',border:'1px solid var(--line)',borderRadius:10}}/><Bar dataKey="transactions" fill="#62e6bd" radius={[4,4,0,0]}/><Bar dataKey="fraud" fill="#ff6b78" radius={[4,4,0,0]}/></BarChart></ResponsiveContainer>:<EmptyChart text="Analytics will populate as predictions are stored."/>}</section></>
  )
}

