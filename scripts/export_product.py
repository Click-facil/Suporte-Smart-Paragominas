# scripts/export_products.py

import csv
# Importa as configurações do app a partir do diretório pai
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db, Product, Category

# Define o nome do arquivo de saída na pasta principal do projeto
OUTPUT_FILENAME = os.path.join(os.path.dirname(__file__), '..', 'produtos_exportados.csv')

def export_data():
    """Lê os produtos do banco de dados e os salva em um arquivo CSV."""
    with app.app_context():
        print("Iniciando exportação de produtos do banco de dados local...")
        
        products = Product.query.all()
        if not products:
            print("Nenhum produto encontrado para exportar.")
            return

        with open(OUTPUT_FILENAME, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Escreve o cabeçalho
            writer.writerow([
                'name', 'description', 'price', 'promo_price', 
                'image_file', 'is_featured', 'category_name'
            ])
            
            # Escreve os dados de cada produto
            for product in products:
                writer.writerow([
                    product.name,
                    product.description,
                    str(product.price),
                    str(product.promo_price) if product.promo_price else '',
                    product.image_file,
                    product.is_featured,
                    product.category.name
                ])

        print(f"Exportação concluída! {len(products)} produtos salvos em '{OUTPUT_FILENAME}'.")

if __name__ == '__main__':
    export_data()