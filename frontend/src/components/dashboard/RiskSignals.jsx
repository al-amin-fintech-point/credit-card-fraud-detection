import { Clock3, Shield } from 'lucide-react'
import { DatabaseIcon } from '../common/DatabaseIcon'

export default function RiskSignals({ stats, health }) {
  return (
    <section className="card attention"><div className="cardhead"><div><h2>Risk signals</h2><p>Latest system status</p></div><span className="live-tag">● LIVE</span></div><div className="signal"><span className="signal-icon mint"><Shield size={17}/></span><div><b>Model connection</b><small>{health?.model_available?'Active model responding':'No trained model loaded'}</small></div><span className={health?.model_available?'status-ok':'status-warn'}>{health?.model_available?'Operational':'Setup needed'}</span></div><div className="signal"><span className="signal-icon blue"><DatabaseIcon/></span><div><b>Prediction history</b><small>{stats?.total_transactions||0} records stored</small></div><span className="status-ok">Ready</span></div><div className="signal"><span className="signal-icon amber"><Clock3 size={17}/></span><div><b>Outcome feedback</b><small>Ground-truth field is available for a review workflow</small></div><span className="status-neutral">Manual</span></div></section>
  )
}

