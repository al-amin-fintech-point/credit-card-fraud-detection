import { Activity, Search } from 'lucide-react'
import { TransactionTable } from '../components/transactions/TransactionTable'

export default function Transactions({ refresh, filtered, search, setSearch }) {
  return (
    <><div className="pagehead"><div><div className="eyebrow">AUDIT TRAIL</div><h1>Transaction history</h1><p>Stored prediction records contain no cardholder details.</p></div><button className="btn secondary" onClick={refresh}><Activity size={16}/> Refresh</button></div><section className="card history-card"><div className="cardhead"><div><h2>All predictions</h2><p>{filtered.length} records shown</p></div><div className="search table-search"><Search size={15}/><input placeholder="Search reference or risk" value={search} onChange={e=>setSearch(e.target.value)}/></div></div><TransactionTable items={filtered}/></section></>
  )
}

