import streamlit as st
import streamlit.components.v1 as components

def render_toc(sections, title="ÍNDICE"):
    """
    Renderiza um sumário flutuante na lateral direita da tela.
    `sections` deve ser uma lista de tuplas: (Rotulo, ID_do_elemento)
    O ID_do_elemento é geralmente o ID que o Streamlit gera automaticamente 
    para um cabeçalho, ex: st.header("Meu Título") -> id="meu-t-tulo"
    """
    if not sections:
        return

    # 1. Gerar os HTML dos pontos (dots)
    dots_html = ""
    js_ids = []
    
    for label, element_id in sections:
        dots_html += f'<a href="#{element_id}" class="toc-dot" id="dot-{element_id}"><span class="toc-label">{label}</span></a>'
        js_ids.append(element_id)
        
    # 2. CSS para estilização e animação da sirene
    # Sem as tags <style> pois injetaremos via JS
    css = """
    .floating-toc {
        position: fixed;
        top: 50%;
        right: 25px;
        transform: translateY(-50%);
        z-index: 999999;
        display: flex;
        flex-direction: column;
        gap: 15px;
        pointer-events: auto;
        align-items: center;
    }
    
    .toc-header {
        font-size: 10px;
        font-weight: 600;
        color: rgba(200, 200, 200, 0.9);
        letter-spacing: 0.5px;
        margin-bottom: 5px;
        pointer-events: none;
        user-select: none;
        text-transform: uppercase;
        text-shadow: 0 0 3px rgba(0,0,0,0.5);
    }
    
    .toc-dot {
        width: 14px;
        height: 14px;
        border-radius: 50%;
        background-color: rgba(150, 150, 150, 0.5);
        cursor: pointer;
        position: relative;
        transition: all 0.3s ease;
        text-decoration: none;
        display: block;
        box-shadow: 0 0 3px rgba(0,0,0,0.3);
    }
    
    .toc-dot:hover {
        background-color: rgba(150, 150, 150, 0.9);
        transform: scale(1.2);
    }
    
    .toc-label {
        position: absolute;
        right: 25px;
        top: 50%;
        transform: translateY(-50%);
        opacity: 0;
        white-space: nowrap;
        background-color: rgba(30, 30, 30, 0.95);
        color: white;
        padding: 5px 12px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 500;
        pointer-events: none;
        transition: opacity 0.3s ease, transform 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.4);
    }
    
    .toc-dot:hover .toc-label {
        opacity: 1;
        transform: translateY(-50%) translateX(-5px);
    }
    
    /* Animação suave de sirene de polícia */
    @keyframes sirene {
        0% { background-color: rgba(255, 50, 50, 0.9); box-shadow: 0 0 10px rgba(255, 50, 50, 0.8); }
        50% { background-color: rgba(50, 50, 255, 0.9); box-shadow: 0 0 10px rgba(50, 50, 255, 0.8); }
        100% { background-color: rgba(255, 50, 50, 0.9); box-shadow: 0 0 10px rgba(255, 50, 50, 0.8); }
    }
    
    .toc-dot.active {
        animation: sirene 1.5s infinite ease-in-out; 
        transform: scale(1.3);
    }
    """
    
    # 3. Javascript para injetar HTML e CSS no window.parent.document e controlar Observer
    js_ids_str = str(js_ids)
    
    js = f"""
    <script>
    document.addEventListener("DOMContentLoaded", function() {{
        const parentDoc = window.parent.document;
        
        // Remove TOC anterior se existir (quando o Streamlit re-renderiza)
        const existingToc = parentDoc.getElementById('floating-toc-container');
        if (existingToc) {{
            existingToc.remove();
        }}
        
        const existingStyle = parentDoc.getElementById('floating-toc-style');
        if (existingStyle) {{
            existingStyle.remove();
        }}
        
        // Injeta CSS no <head> da janela principal
        const style = parentDoc.createElement('style');
        style.id = 'floating-toc-style';
        style.innerHTML = `{css}`;
        parentDoc.head.appendChild(style);
        
        // Cria a Div do sumário e anexa diretamente no <body>
        const tocContainer = parentDoc.createElement('div');
        tocContainer.id = 'floating-toc-container';
        tocContainer.className = 'floating-toc';
        
        const tocInnerHtml = `<div class='toc-header'>{title}</div>` + `{dots_html}`;
        tocContainer.innerHTML = tocInnerHtml;
        parentDoc.body.appendChild(tocContainer);
        
        const sectionIds = {js_ids_str};
        
        // Observer
        setTimeout(() => {{
            const observer = new IntersectionObserver((entries) => {{
                entries.forEach(entry => {{
                    if (entry.isIntersecting) {{
                        // Remove 'active' de todos
                        const allDots = parentDoc.querySelectorAll('.toc-dot');
                        allDots.forEach(dot => dot.classList.remove('active'));
                        
                        // Adiciona 'active' no dot correspondente
                        const targetId = entry.target.id;
                        const activeDot = parentDoc.getElementById('dot-' + targetId);
                        if (activeDot) {{
                            activeDot.classList.add('active');
                        }}
                    }}
                }});
            }}, {{ 
                root: null,
                rootMargin: '-10% 0px -60% 0px', 
                threshold: 0 
            }});
            
            sectionIds.forEach(id => {{
                const el = parentDoc.getElementById(id);
                if (el) {{
                    observer.observe(el);
                }}
            }});
            
            // Controle de scroll suave ao clicar na bolinha
            const dots = parentDoc.querySelectorAll('.toc-dot');
            dots.forEach(dot => {{
                dot.addEventListener('click', function(e) {{
                    e.preventDefault();
                    const targetId = this.getAttribute('href').substring(1);
                    const targetEl = parentDoc.getElementById(targetId);
                    if (targetEl) {{
                        targetEl.scrollIntoView({{ behavior: 'smooth' }});
                        window.parent.history.pushState(null, null, '#' + targetId);
                    }}
                }});
            }});
            
        }}, 1000); 
    }});
    </script>
    """
    
    # Injetamos o script num iframe invisível que cuidará de tudo na DOM parent
    components.html(js, height=0, width=0)
