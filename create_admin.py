import os
from app import app, db, User, bcrypt

# Pega as credenciais das variáveis de ambiente
admin_user = os.environ.get('ADMIN_USERNAME', 'admin')
admin_pass = os.environ.get('ADMIN_PASSWORD', 'password')

with app.app_context():
    # Verifica se o usuário já existe
    user_exists = User.query.filter_by(username=admin_user).first()
    
    if not user_exists:
        print(f"Criando usuário administrador: {admin_user}...")
        hashed_password = bcrypt.generate_password_hash(admin_pass).decode('utf-8')
        user = User(username=admin_user, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        print("Usuário administrador criado com sucesso!")
    else:
        print(f"Usuário '{admin_user}' já existe. Nenhuma ação foi tomada.")