import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'

export default function DetectionSplit({ stats, pie }) {
  return (
    <section className="card distribution"><div className="cardhead"><div><h2>Detection split</h2><p>All scored transactions</p></div><button className="more">···</button></div>{stats?.total_transactions?<div className="pie-wrap"><ResponsiveContainer width="100%" height={190}><PieChart><Pie data={pie} dataKey="value" innerRadius={58} outerRadius={79} paddingAngle={3} stroke="none">{pie.map((entry,i)=><Cell key={i} fill={entry.color}/>)}</Pie><Tooltip contentStyle={{background:'var(--panel)',border:'1px solid var(--line)',borderRadius:10}}/></PieChart></ResponsiveContainer><div className="pie-center"><b>{((stats.fraud_detected/stats.total_transactions)*100).toFixed(1)}%</b><small>flagged</small></div></div>:<div className="pie-wrap empty-pie"><div><span>—</span><small>No predictions yet</small></div></div>}<div className="split-list">{pie.map(item=><div key={item.name}><span><i style={{background:item.color}}/>{item.name}</span><b>{item.value.toLocaleString()}</b></div>)}</div></section>
  )
}

