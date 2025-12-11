from app import app, db
from sqlalchemy import text

# Esse script adiciona a coluna 'models' no seu banco de dados local (SQLite)
with app.app_context():
    try:
        with db.engine.connect() as conn:
            # Comando SQL para adicionar a coluna
            conn.execute(text("ALTER TABLE product ADD COLUMN models VARCHAR(1000)"))
            conn.commit()
            print("✅ Sucesso! Coluna 'models' adicionada ao banco de dados local.")
    except Exception as e:
        print(f"❌ Erro ou a coluna já existe: {e}")