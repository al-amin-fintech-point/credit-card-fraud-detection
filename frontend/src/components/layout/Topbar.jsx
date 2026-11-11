import { Bell, Menu, Moon, Search, Sun } from 'lucide-react'

export default function Topbar({ page, search, setSearch, dark, setDark, setMobile }) {
  return (<header className="topbar"><button className="iconbtn menu-btn" onClick={()=>setMobile(true)}><Menu size={19}/></button><div className="crumb">Risk intelligence <span>/</span> <b>{page}</b></div><div className="top-actions"><div className="search"><Search size={16}/><input placeholder="Search transactions..." value={search} onChange={e=>setSearch(e.target.value)}/><kbd>⌘ K</kbd></div><button className="iconbtn" onClick={()=>setDark(!dark)} title="Toggle theme">{dark?<Sun size={18}/>:<Moon size={18}/>}</button><button className="iconbtn notification"><Bell size={18}/><i/></button><div className="avatar top-avatar">AR</div></div></header>)
}

