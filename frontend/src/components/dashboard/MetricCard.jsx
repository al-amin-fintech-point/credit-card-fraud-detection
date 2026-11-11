export default function MetricCard({ card, index, compact = false }) {
  const [label, value, note, Icon] = card
  return compact ? (
    <div className="metric" key={label}><div className="metric-top"><span>{label}</span><Icon size={16}/></div><strong>{value}</strong><div className="metric-note">{note}</div></div>
  ) : (
    <div className="metric" key={label}><div className="metric-top"><span>{label}</span><span className={`metric-icon i${index}`}><Icon size={17}/></span></div><strong>{value}</strong><div className="metric-note">{note}</div></div>
  )
}

