---
name: vps-management
description: Handles automated updates, log checking, and user management for the Hostgator VPS where the PCSP app is deployed.
---
# Instruções para Gerenciamento do VPS Hostgator

Quando o usuário pedir para "atualizar a aplicação no VPS", "verificar logs de acesso", ou "gerenciar usuários", siga estas regras:

## 1. Informações do Servidor
- **IP:** 143.95.219.248
- **Porta:** 22022
- **Usuário:** root
- **Pasta da aplicação:** `/root/aplicacao`

## 2. Como executar comandos
O agente NÃO deve tentar conectar via SSH interativamente (pois o terminal irá travar aguardando a senha digitada pelo usuário).
Em vez disso, o agente deve gerar o comando SSH completo que o usuário pode rodar diretamente do seu PowerShell, passando a instrução como uma string.

Por exemplo, para atualizar a aplicação:
```bash
ssh -o IPQoS=none root@143.95.219.248 -p 22022 "cd /root/aplicacao && git pull && docker compose up --build -d"
```

- **Atualizar Aplicação:** `cd /root/aplicacao && git pull && docker compose up --build -d`
- **Verificar Logs Nginx:** `tail -n 50 /var/log/nginx/access.log`
- **Adicionar Usuário Nginx:** `htpasswd /etc/nginx/.htpasswd <nome_do_usuario>` (NUNCA usar `-c` pois sobrescreve tudo).
- **Remover Usuário Nginx:** `htpasswd -D /etc/nginx/.htpasswd <nome_do_usuario>`
- **Ver Status do Serviço (Docker):** `cd /root/aplicacao && docker compose ps`
- **Ver Logs da Aplicação (Docker):** `cd /root/aplicacao && docker compose logs -f --tail=50`

*Aviso de Transição:* Se a aplicação estiver sendo executada no VPS antigamente pelo `systemctl`, lembre-se de rodar `systemctl stop streamlit` e `systemctl disable streamlit` pelo menos uma vez no servidor antes de subir o Docker, para liberar a porta 8501.

## 4. Próximos Passos (Automação Total)
Se o usuário quiser que o agente rode os comandos sem pedir para ele colar no PowerShell, sugira a criação de um par de chaves SSH no Windows local e a inserção da chave pública no `~/.ssh/authorized_keys` do VPS. Com isso, o agente conseguirá usar a tool `run_command` livremente para orquestrar o servidor sem travar na tela de senha.
