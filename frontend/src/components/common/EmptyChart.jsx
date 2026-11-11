import { BarChart3 } from 'lucide-react'

export function EmptyChart({text}){return <div className="empty-chart"><div className="empty-icon"><BarChart3 size={19}/></div><span>{text}</span></div>}
