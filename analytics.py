import streamlit as st
import hashlib
import json
from collections import Counter
from datetime import datetime, date
from database import get_db_session, AnalyticsSession, AnalyticsEvent, get_br_time
from user_tracking import get_user_hash, get_user_agent, get_client_ip

def get_browser_info(user_agent: str):
    os_name = "Unknown"
    browser_name = "Unknown"
    
    if not user_agent:
        return os_name, browser_name
        
    ua_lower = user_agent.lower()
    
    if "windows" in ua_lower: os_name = "Windows"
    elif "mac os" in ua_lower or "macos" in ua_lower: os_name = "macOS"
    elif "android" in ua_lower: os_name = "Android"
    elif "iphone" in ua_lower or "ipad" in ua_lower: os_name = "iOS"
    elif "linux" in ua_lower: os_name = "Linux"
        
    if "edg" in ua_lower: browser_name = "Edge"
    elif "opr" in ua_lower or "opera" in ua_lower: browser_name = "Opera"
    elif "chrome" in ua_lower: browser_name = "Chrome"
    elif "firefox" in ua_lower: browser_name = "Firefox"
    elif "safari" in ua_lower: browser_name = "Safari"
        
    return os_name, browser_name

def get_session_id():
    ip = get_client_ip()
    ua = get_user_agent()
    today = date.today().isoformat()
    return hashlib.sha256(f"{ip}-{ua}-{today}".encode('utf-8')).hexdigest()

def ensure_session():
    """Garante que a sessão atual exista na tabela AnalyticsSession"""
    db = get_db_session()
    session_id = get_session_id()
    
    session = db.query(AnalyticsSession).filter_by(session_id=session_id).first()
    if not session:
        user_hash, _ = get_user_hash()
        os_name, browser_name = get_browser_info(get_user_agent())
        
        session = AnalyticsSession(
            session_id=session_id,
            user_hash=user_hash,
            os_name=os_name,
            browser_name=browser_name
        )
        db.add(session)
        db.commit()
    else:
        session.last_activity = get_br_time()
        db.commit()
        
    db.close()
    return session_id

def log_event(event_type: str, event_data: dict = None):
    try:
        session_id = ensure_session()
        db = get_db_session()
        
        event = AnalyticsEvent(
            session_id=session_id,
            event_type=event_type,
            event_data=json.dumps(event_data, ensure_ascii=False) if event_data else None
        )
        db.add(event)
        db.commit()
        
        # Após logar, tenta atualizar a persona inferida
        infer_persona(session_id, db)
        
        db.close()
    except Exception as e:
        print(f"Silent Analytics Error: {e}")

def infer_persona(session_id: str, db):
    """
    Deduz a persona baseado no histórico de eventos.
    Regras:
    - Policial Civil: Muito foco no Modo 1 (matriz) e cargos específicos.
    - Legislador/Político: Foco no Modo 3 e explicações Políticas.
    - Estudioso/Professor: Explicações Acadêmicas longas.
    - Curioso: Uso genérico.
    """
    events = db.query(AnalyticsEvent).filter_by(session_id=session_id).all()
    
    view_modes = []
    explanations = []
    cargos_selecionados = []
    language_pref = "PT-BR"
    
    for e in events:
        data = json.loads(e.event_data) if e.event_data else {}
        if e.event_type == "change_mode":
            if "mode" in data: view_modes.append(data["mode"])
        elif e.event_type == "toggle_explanations":
            if "tone" in data: explanations.append(data["tone"])
        elif e.event_type == "filter_change" and data.get("filter") == "cargos":
            cargos_selecionados.extend(data.get("values", []))
        elif e.event_type == "change_language":
            language_pref = data.get("language", "PT-BR")
            
    persona = "Cidadão/Curioso"
    
    if language_pref == "EN":
        persona = "Estrangeiro"
    else:
        # Se filtrou muitos cargos ou usou modo 1 (matriz interna), pode ser policial
        cargos_especificos = [c for c in cargos_selecionados if c in ["Delegado de Polícia", "Investigador de Polícia", "Escrivão de Polícia", "Perito Criminal", "Médico Legista"]]
        
        if "1." in str(view_modes) or len(cargos_especificos) > 0:
            if len(cargos_especificos) > 0:
                contagem = Counter(cargos_especificos)
                cargo_mais_frequente = contagem.most_common(1)[0][0]
                if "Delegado" in cargo_mais_frequente:
                    persona = "Policial Civil (Possível Delegado)"
                elif "Investigador" in cargo_mais_frequente:
                    persona = "Policial Civil (Possível Investigador)"
                elif "Escrivão" in cargo_mais_frequente:
                    persona = "Policial Civil (Possível Escrivão)"
                elif "Perito" in cargo_mais_frequente:
                    persona = "Policial Civil (Possível Perito)"
                elif "Médico" in cargo_mais_frequente:
                    persona = "Policial Civil (Possível Médico Legista)"
                else:
                    persona = f"Policial Civil (Possível {cargo_mais_frequente})"
            else:
                persona = "Policial Civil"
                
        # Se interagiu com tom Crítico no Modo 3 -> Legislador
        if "3." in str(view_modes) and "Crítico" in str(explanations):
            persona = "Legislador/Político"
            
        # Se focou em Acadêmico
        if "Acadêmico" in str(explanations) and persona == "Cidadão/Curioso":
            persona = "Estudioso/Professor"
    session = db.query(AnalyticsSession).filter_by(session_id=session_id).first()
    if session and session.inferred_persona != persona:
        session.inferred_persona = persona
        db.commit()
