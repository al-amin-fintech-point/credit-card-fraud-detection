import { Activity, ArrowUpRight } from 'lucide-react'
import MetricCard from '../components/dashboard/MetricCard'
import TransactionChart from '../components/dashboard/TransactionChart'
import DetectionSplit from '../components/dashboard/DetectionSplit'
import RiskDistribution from '../components/dashboard/RiskDistribution'
import RiskSignals from '../components/dashboard/RiskSignals'
import AmountAnalysis from '../components/dashboard/AmountAnalysis'
import { TransactionTable } from '../components/transactions/TransactionTable'

export default function Overview({ metricCards, refresh, trends, stats, pie, history, setPage, health, amounts }) {
  return (
    <><div className="pagehead"><div><div className="eyebrow"><span className="pulse"/> LIVE MONITORING</div><h1>Good morning, Alex <span>✦</span></h1><p>Here’s what’s happening across your transaction network today.</p></div><div className="head-right"><button className="btn secondary" onClick={refresh}><Activity size={16}/> Refresh</button><span className="updated"><span className="pulse"/> Updated just now</span></div></div>
      <div className="metrics">{metricCards.map((card,i)=><MetricCard key={card[0]} card={card} index={i}/>)}</div>
      <div className="grid-main"><TransactionChart trends={trends}/>
      <DetectionSplit stats={stats} pie={pie}/></div>
      <div className="bottom-grid"><section className="card"><div className="cardhead"><div><h2>Recent transactions</h2><p>Latest model decisions</p></div><button className="linkbtn" onClick={()=>setPage('Transactions')}>View all <ArrowUpRight size={14}/></button></div><TransactionTable items={history.slice(0,5)}/></section><RiskSignals stats={stats} health={health}/>
      <RiskDistribution stats={stats}/>
      <AmountAnalysis amounts={amounts}/></div></>
  )
}

