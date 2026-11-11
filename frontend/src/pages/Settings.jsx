import { Activity, Gauge, Moon, SlidersHorizontal, Sun } from 'lucide-react'

export default function Settings({ health, dark, setDark }) {
  return (
    <><div className="pagehead"><div><div className="eyebrow">PREFERENCES</div><h1>Settings</h1><p>Runtime configuration and operational status.</p></div></div><section className="card settings-card"><h2>System status</h2><div className="signal"><span className="signal-icon mint"><Activity size={17}/></span><div><b>API status</b><small>{health?.status||'Checking connection'}</small></div><span className="status-ok">Connected</span></div><div className="signal"><span className="signal-icon blue"><Gauge size={17}/></span><div><b>Active model</b><small>{health?.model_version||'No trained model loaded'}</small></div><span className={health?.model_available?'status-ok':'status-warn'}>{health?.model_available?'Available':'Unavailable'}</span></div><div className="signal"><span className="signal-icon amber"><SlidersHorizontal size={17}/></span><div><b>Theme</b><small>Choose a comfortable display</small></div><button className="btn secondary" onClick={()=>setDark(!dark)}>{dark?<Sun size={15}/>:<Moon size={15}/>} Toggle</button></div></section></>
  )
}

