import streamlit as st
import hashlib

def get_client_ip():
    """
    Tenta obter o IP do cliente verificando proxies ou conexão direta.
    Requer Streamlit >= 1.37 para funcionar corretamente.
    """
    try:
        headers = st.context.headers
        
        # X-Forwarded-For é usado por proxies (como Nginx)
        x_forwarded_for = headers.get("X-Forwarded-For")
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
            
        # Pega o IP real configurado no Nginx
        x_real_ip = headers.get("X-Real-IP")
        if x_real_ip:
            return x_real_ip

        return "127.0.0.1" # Fallback local
    except Exception:
        return "Unknown"

def get_user_agent():
    try:
        return st.context.headers.get("User-Agent", "Unknown")
    except Exception:
        return "Unknown"

def get_user_hash():
    """
    Gera um identificador único e consistente para a sessão do usuário baseado em IP e navegador.
    Trata-se de um 'Passive Fingerprinting'.
    """
    ip = get_client_ip()
    user_agent = get_user_agent()
    
    unique_string = f"{ip}-{user_agent}"
    user_hash = hashlib.sha256(unique_string.encode('utf-8')).hexdigest()
    
    return user_hash, ip
