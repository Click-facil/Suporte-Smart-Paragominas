import csv
import os
from sqlalchemy import create_engine, text

# ==============================================================================
# 🔴 🔴 🔴 COLOQUE O LINK DO RENDER ABAIXO (DENTRO DAS ASPAS) 🔴 🔴 🔴
# Exemplo: LINK_DO_RENDER = "postgres://usuario:senha@host..."
# ==============================================================================

LINK_DO_RENDER = "postgresql://suportesmart_db_user:HlsVgN8NEFYNmqfcY9veJlJ43w3y1eP0@dpg-d2vhcljuibrs738k29p0-a.oregon-postgres.render.com/suportesmart_db"

# ==============================================================================

def fazer_backup_nuvem():
    print("1. 🚀 Conectando diretamente na Nuvem (Render)...")
    
    if "COLE_AQUI" in LINK_DO_RENDER:
        print("❌ ERRO: Você esqueceu de colar o link do Render na linha 10 do código!")
        return

    # Corrige o link se necessário (Render usa postgres:// mas o Python prefere postgresql://)
    url_corrigida = LINK_DO_RENDER.replace("postgres://", "postgresql://")
    
    # Adiciona modo SSL se não tiver (Obrigatório para Render)
    if "?" not in url_corrigida:
        url_corrigida += "?sslmode=require"
    elif "sslmode" not in url_corrigida:
        url_corrigida += "&sslmode=require"

    try:
        # Cria a conexão direta, sem usar o Flask/App
        engine = create_engine(url_corrigida)
        
        with engine.connect() as conn:
            print("2. ✅ Conexão estabelecida com o Render! Baixando produtos...")
            
            # Pega os produtos
            result = conn.execute(text("SELECT * FROM product"))
            colunas = result.keys()
            produtos = result.fetchall()
            
            if not produtos:
                print("⚠️  O BANCO DO RENDER ESTÁ VAZIO (0 produtos).")
                print("   Isso significa que os produtos reais NÃO estão lá.")
                print("   Verifique se você não cadastrou eles no 'localhost' sem querer.")
                return

            print(f"3. 📦 Encontrados {len(produtos)} produtos REAIS. Salvando...")

            # Salva na pasta do projeto
            caminho_atual = os.getcwd()
            arquivo_destino = os.path.join(caminho_atual, 'BACKUP_RENDER_REAL.csv')

            with open(arquivo_destino, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(colunas)
                writer.writerows(produtos)
            
            print("-" * 30)
            print(f"🎉 SUCESSO! Backup dos produtos online realizado.")
            print(f"📂 Arquivo: {arquivo_destino}")
            print("-" * 30)

    except Exception as e:
        print(f"❌ ERRO DE CONEXÃO: {e}")
        print("   Verifique se o link foi copiado corretamente.")

if __name__ == "__main__":
    fazer_backup_nuvem()