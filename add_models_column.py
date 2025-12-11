#!/usr/bin/env python3
"""
Script para adicionar a coluna 'models' à tabela Product
Execute este script uma única vez após implementar as mudanças no código.
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Carrega as variáveis de ambiente
load_dotenv()

def add_models_column():
    """Adiciona a coluna models à tabela product se ela não existir."""
    
    # Pega a URL do banco de dados do ambiente
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///suportesmart.db')
    
    # Garante que a URL do PostgreSQL seja compatível com o SQLAlchemy
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    try:
        # Cria a conexão com o banco
        engine = create_engine(database_url)
        
        with engine.connect() as connection:
            # Verifica se a coluna já existe
            if 'sqlite' in database_url.lower():
                # SQLite
                result = connection.execute(text("PRAGMA table_info(product)"))
                columns = [row[1] for row in result.fetchall()]
                
                if 'models' not in columns:
                    print("Adicionando coluna 'models' à tabela product (SQLite)...")
                    connection.execute(text("ALTER TABLE product ADD COLUMN models VARCHAR(1000)"))
                    connection.commit()
                    print("✅ Coluna 'models' adicionada com sucesso!")
                else:
                    print("ℹ️  Coluna 'models' já existe na tabela product.")
                    
            else:
                # PostgreSQL
                # Verifica se a coluna existe
                result = connection.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'product' AND column_name = 'models'
                """))
                
                if not result.fetchone():
                    print("Adicionando coluna 'models' à tabela product (PostgreSQL)...")
                    connection.execute(text("ALTER TABLE product ADD COLUMN models VARCHAR(1000)"))
                    connection.commit()
                    print("✅ Coluna 'models' adicionada com sucesso!")
                else:
                    print("ℹ️  Coluna 'models' já existe na tabela product.")
                    
    except Exception as e:
        print(f"❌ Erro ao adicionar coluna: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🔧 Executando migração para adicionar coluna 'models'...")
    add_models_column()
    print("🎉 Migração concluída!")