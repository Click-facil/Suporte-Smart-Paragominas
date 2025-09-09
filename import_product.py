import csv
from decimal import Decimal
from app import app, db, Product, Category

CSV_FILENAME = 'produtos_exportados.csv'

def import_data():
    """Lê os produtos do arquivo CSV e os salva no banco de dados."""
    with app.app_context():
        print("Iniciando importação de produtos...")
        
        try:
            with open(CSV_FILENAME, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader) # Pula o cabeçalho

                for row in reader:
                    # Pega o nome da categoria do CSV e encontra o objeto Categoria correspondente
                    category_name = row[7]
                    category = Category.query.filter_by(name=category_name).first()

                    if not category:
                        print(f"AVISO: Categoria '{category_name}' não encontrada. Pulando produto '{row[1]}'. Certifique-se de que as categorias já existem no painel do Render.")
                        continue

                    # Converte os valores de volta para os tipos corretos
                    price = Decimal(row[3])
                    promo_price = Decimal(row[4]) if row[4] else None
                    is_featured = True if row[6].lower() == 'true' else False

                    # Cria o novo produto
                    new_product = Product(
                        name=row[1],
                        description=row[2],
                        price=price,
                        promo_price=promo_price,
                        image_file=row[5],
                        is_featured=is_featured,
                        category_id=category.id
                    )
                    db.session.add(new_product)
                
                db.session.commit()
                print("Importação concluída com sucesso!")

        except FileNotFoundError:
            print(f"ERRO: Arquivo '{CSV_FILENAME}' não encontrado.")
        except Exception as e:
            db.session.rollback()
            print(f"Ocorreu um erro durante a importação: {e}")

if __name__ == '__main__':
    import_data()