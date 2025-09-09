import csv
from app import app, db, Product, Category

# O nome do arquivo que vamos gerar
CSV_FILENAME = 'produtos_exportados.csv'

def export_data():
    """Lê os produtos do banco de dados e os salva em um arquivo CSV."""
    with app.app_context():
        print("Iniciando exportação de produtos...")
        
        products = Product.query.all()
        if not products:
            print("Nenhum produto encontrado no banco de dados local.")
            return

        with open(CSV_FILENAME, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Escreve o cabeçalho da planilha
            writer.writerow([
                'id', 'name', 'description', 'price', 'promo_price', 
                'image_file', 'is_featured', 'category_name'
            ])
            
            # Escreve os dados de cada produto
            for product in products:
                writer.writerow([
                    product.id,
                    product.name,
                    product.description,
                    str(product.price), # Converte para string
                    str(product.promo_price) if product.promo_price else '', # Converte para string
                    product.image_file,
                    product.is_featured,
                    product.category.name # Salva o NOME da categoria
                ])

        print(f"Exportação concluída com sucesso! {len(products)} produtos foram salvos em '{CSV_FILENAME}'.")

if __name__ == '__main__':
    export_data()