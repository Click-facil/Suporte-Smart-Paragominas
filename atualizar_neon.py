#!/usr/bin/env python3
"""
Script para adicionar coluna is_visible diretamente no Neon
"""
from sqlalchemy import create_engine, text

# Cole aqui sua URL do Neon (a mesma do Vercel)
NEON_URL = "postgresql://neondb_owner:npg_oUMNDZFVW94T@ep-shiny-bush-adsocvw3-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"

def criar_coluna_neon():
    print("1. 🚀 Conectando ao Neon...")
    engine = create_engine(NEON_URL)
    
    with engine.connect() as conn:
        print("2. 🏗️ Adicionando coluna 'is_visible'...")
        try:
            sql = text("ALTER TABLE product ADD COLUMN is_visible BOOLEAN DEFAULT TRUE;")
            conn.execute(sql)
            conn.commit()
            print("✅ SUCESSO! Coluna criada no Neon.")
        except Exception as e:
            if "already exists" in str(e):
                print("⚠️ A coluna já existia, tudo certo.")
            else:
                print(f"❌ Erro: {e}")

if __name__ == "__main__":
    criar_coluna_neon()