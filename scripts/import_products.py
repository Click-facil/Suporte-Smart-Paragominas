# scripts/import_products.py

import csv
from decimal import Decimal
# Importa as configurações do app a partir do diretório pai
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db, Product, Category

# ATENÇÃO: Altere este caminho dependendo de onde você vai rodar o script
# Para rodar localmente, use o caminho relativo
CSV_FILENAME = 'produtos_exportados.csv'
# Para rodar no Render com Disco Persistente, use o caminho absoluto do disco
# CSV_FILENAME = '/var/data/produtos_exportados.csv'

def import_data():
    """Lê produtos do CSV e os cria ou atualiza no banco de dados."""
    created_count = 0
    updated_count = 0
    
    with app.app_context():
        print("Iniciando importação/atualização de produtos...")
        
        try:
            with open(CSV_FILENAME, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader) # Pula o cabeçalho

                for row in reader:
                    # Mapeia a linha do CSV para um dicionário para fácil acesso
                    data = dict(zip(header, row))
                    
                    product_name = data.get('name')
                    if not product_name:
                        continue

                    category_name = data.get('category_name')
                    category = Category.query.filter_by(name=category_name).first()

                    if not category:
                        print(f"AVISO: Categoria '{category_name}' não encontrada. Pulando produto '{product_name}'.")
                        continue
                    
                    # Converte os valores
                    price = Decimal(data.get('price'))
                    promo_price = Decimal(data.get('promo_price')) if data.get('promo_price') else None
                    is_featured = True if data.get('is_featured', '').lower() == 'true' else False

                    # A LÓGICA PRINCIPAL: VERIFICA SE O PRODUTO JÁ EXISTE
                    product = Product.query.filter_by(name=product_name).first()

                    if product:
                        # SE EXISTE, ATUALIZA
                        product.description = data.get('description')
                        product.price = price
                        product.promo_price = promo_price
                        product.image_file = data.get('image_file', 'placeholder.png')
                        product.is_featured = is_featured
                        product.category_id = category.id
                        updated_count += 1
                    else:
                        # SE NÃO EXISTE, CRIA
                        new_product = Product(
                            name=product_name,
                            description=data.get('description'),
                            price=price,
                            promo_price=promo_price,
                            image_file=data.get('image_file', 'placeholder.png'),
                            is_featured=is_featured,
                            category_id=category.id
                        )
                        db.session.add(new_product)
                        created_count += 1
                
                db.session.commit()
                print("--- Resumo da Importação ---")
                print(f"Produtos criados: {created_count}")
                print(f"Produtos atualizados: {updated_count}")
                print("----------------------------")

        except FileNotFoundError:
            print(f"ERRO: Arquivo de importação '{CSV_FILENAME}' não foi encontrado.")
        except Exception as e:
            db.session.rollback()
            print(f"Ocorreu um erro inesperado. Nenhuma alteração foi salva. Erro: {e}")

if __name__ == '__main__':
    import_data()