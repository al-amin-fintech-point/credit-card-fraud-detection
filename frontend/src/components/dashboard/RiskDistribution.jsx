import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

export default function RiskDistribution({ stats }) {
  return (
    <section className="card"><div className="cardhead"><div><h2>Risk distribution</h2><p>Predictions by risk tier</p></div></div><ResponsiveContainer width="100%" height={180}><BarChart data={['LOW RISK','MEDIUM RISK','HIGH RISK'].map((name)=>({name:name.replace(' RISK',''),count:stats?.risk_distribution?.[name]||0}))}><CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--line)"/><XAxis dataKey="name" tick={{fill:'var(--muted)',fontSize:9}} axisLine={false} tickLine={false}/><YAxis tick={{fill:'var(--muted)',fontSize:9}} axisLine={false} tickLine={false}/><Tooltip contentStyle={{background:'var(--panel)',border:'1px solid var(--line)',borderRadius:10}}/><Bar dataKey="count" radius={[4,4,0,0]}>{['#62e6bd','#f4bd68','#ff6b78'].map((color,i)=><Cell key={i} fill={color}/>)}</Bar></BarChart></ResponsiveContainer></section>
  )
}

