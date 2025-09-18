import os
import secrets
from dotenv import load_dotenv
from PIL import Image
from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response, jsonify
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
# Novo import para upload múltiplo
from flask_wtf.file import FileField, FileAllowed, MultipleFileField
from wtforms import StringField, TextAreaField, DecimalField, SubmitField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, ValidationError, Optional
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required

load_dotenv() # Carrega as variáveis de ambiente do arquivo .env

app = Flask(__name__)

# --- CONFIGURAÇÃO ---
# Usa variáveis de ambiente para segurança e flexibilidade
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'uma-chave-secreta-padrao-para-desenvolvimento')

# --- Configurações de Cookie para maior segurança e compatibilidade ---
# Isso é crucial para que o login funcione corretamente em todos os navegadores,
# especialmente em dispositivos móveis e em produção (HTTPS).
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['REMEMBER_COOKIE_SAMESITE'] = 'Lax'

# Em produção (como no Render), o tráfego é via HTTPS, então os cookies devem ser 'Secure'.
if not app.debug:
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['REMEMBER_COOKIE_SECURE'] = True

# Pega a URL do banco de dados do ambiente, com um fallback para o SQLite local
database_url = os.environ.get('DATABASE_URL', 'sqlite:///suportesmart.db')

# Garante que a URL do PostgreSQL seja compatível com o SQLAlchemy, pois alguns serviços usam "postgres://"
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Aumenta o tamanho máximo de upload para permitir várias imagens
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'Por favor, faça login para aceder a esta página.'

# --- MODELOS DO BANCO DE DADOS ---
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True) # Alterado para Text para descrições mais longas
    price = db.Column(db.Numeric(10, 2), nullable=False)
    promo_price = db.Column(db.Numeric(10, 2), nullable=True)
    # Esta será a imagem principal/de capa
    image_file = db.Column(db.String(100), nullable=False, default='placeholder.png')
    is_featured = db.Column(db.Boolean, nullable=False, default=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    # Relação com a nova tabela de imagens
    images = db.relationship('ProductImage', backref='product', lazy=True, cascade="all, delete-orphan")

# NOVA TABELA PARA A GALERIA DE IMAGENS
class ProductImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_filename = db.Column(db.String(100), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

# --- PROCESSADOR DE CONTEXTO ---
@app.context_processor
def inject_context():
    all_categories = Category.query.order_by(Category.name).all()
    cart = session.get('cart', {})
    # Usamos .get('quantity', 0) para segurança caso a estrutura do item seja inesperada
    cart_item_count = sum(item.get('quantity', 0) for item in cart.values())
    return dict(all_categories=all_categories, cart_item_count=cart_item_count)


# --- FORMULÁRIOS ---
class ProductForm(FlaskForm):
    name = StringField('Nome do Produto', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Descrição')
    price = DecimalField('Preço (ex: 1299.90)', validators=[DataRequired()])
    promo_price = DecimalField('Preço Promocional (Opcional)', validators=[Optional()])
    # Este campo agora só atualiza a imagem principal
    picture = FileField('Atualizar Imagem Principal', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    category = SelectField('Categoria', coerce=int, validators=[DataRequired()])
    is_featured = BooleanField('Marcar como Destaque')
    submit = SubmitField('Salvar Produto')

# NOVO FORMULÁRIO PARA UPLOAD MÚLTIPLO
class ImageUploadForm(FlaskForm):
    pictures = MultipleFileField('Adicionar Imagens', validators=[DataRequired(), FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Enviar Imagens')

class LoginForm(FlaskForm):
    username = StringField('Utilizador', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember = BooleanField('Lembrar de mim')
    submit = SubmitField('Entrar')

class UserForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Adicionar Usuário')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Este nome de usuário já está em uso. Por favor, escolha outro.')

class CategoryForm(FlaskForm):
    name = StringField('Nome da Categoria', validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('Salvar Categoria')

    def validate_name(self, name):
        # Garante que a validação não ocorra num formulário já preenchido
        if request.endpoint == 'edit_category' and request.method == 'GET':
            return
        category = Category.query.filter_by(name=name.data).first()
        if category:
            raise ValidationError('Essa categoria já existe. Por favor, escolha um nome diferente.')


# --- FUNÇÃO HELPER PARA SALVAR IMAGENS ---
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/product_pics', picture_fn)
    output_size = (800, 800)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

def delete_picture(filename):
    """Apaga um arquivo de imagem da pasta static/product_pics."""
    # Não apagar a imagem padrão
    if filename and filename != 'placeholder.png':
        try:
            picture_path = os.path.join(app.root_path, 'static/product_pics', filename)
            if os.path.exists(picture_path):
                os.remove(picture_path)
        except Exception as e:
            # Em um app de produção, seria bom logar este erro
            print(f"Erro ao apagar a imagem {filename}: {e}")


# --- ROTAS DO SITE PÚBLICO ---
@app.route('/')
def home():
    products = Product.query.filter_by(is_featured=True).order_by(Product.id.desc()).all()
    return render_template('index.html', products=products)

@app.route('/loja')
def loja():
    products = Product.query.order_by(Product.id.desc()).all()
    return render_template('loja.html', products=products, title="Nossa Loja")

@app.route('/categoria/<int:category_id>')
def category_page(category_id):
    category = db.get_or_404(Category, category_id)
    return render_template('loja.html', products=category.products, title=f"Categoria: {category.name}", category=category)

@app.route('/produto/<int:product_id>')
def product_detail(product_id):
    # .get_or_404 é a melhor forma de buscar: ele retorna o produto
    # ou mostra uma página de erro 404 (Não Encontrado) automaticamente.
    product = Product.query.get_or_404(product_id)

    # Lógica para o botão "Voltar" inteligente
    referrer = request.referrer
    # Define um URL de retorno padrão para a seção de loja na página inicial
    back_url = url_for('home', _anchor='loja')

    # Se o usuário veio da página da loja ou de uma categoria, usamos esse URL de referência
    if referrer and ('/loja' in referrer or '/categoria/' in referrer):
        back_url = referrer

    return render_template("product_detail.html", title=product.name, product=product, back_url=back_url)

@app.route('/sitemap.xml')
def sitemap():
    """Gera o sitemap.xml para o site com o domínio correto."""
    
    # Define a URL base oficial do site
    base_url = "https://www.suportesmartparagominas.com.br"
    
    pages = []
    last_mod = datetime.now().date().isoformat()

    # Páginas estáticas
    pages.append({'loc': f"{base_url}/", 'lastmod': last_mod})
    pages.append({'loc': f"{base_url}/loja", 'lastmod': last_mod})

    # Páginas de produtos
    products = Product.query.all()
    for product in products:
        pages.append({'loc': f"{base_url}/produto/{product.id}", 'lastmod': last_mod})

    # Páginas de categorias
    categories = Category.query.all()
    for category in categories:
        pages.append({'loc': f"{base_url}/categoria/{category.id}", 'lastmod': last_mod})

    sitemap_template = render_template('sitemap.xml', pages=pages)
    response = make_response(sitemap_template)
    response.headers["Content-Type"] = "application/xml"
    return response

@app.route('/robots.txt')
def robots():
    return render_template('robots.txt')

# ROTA DE TESTE PARA DEBUG NO RENDER
@app.route('/teste-debug-123')
def debug_route():
    return "<h1>Atualizacao do sitemap - Teste final.</h1>"

# --- ROTAS DO CARRINHO DE COMPRAS ---
@app.route('/carrinho/adicionar/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    cart = session.get('cart', {})
    
    try:
        quantity = int(request.form.get('quantity', 1))
        if quantity < 1:
            quantity = 1
    except (ValueError, TypeError):
        quantity = 1

    product_id_str = str(product_id)

    if product_id_str in cart:
        cart[product_id_str]['quantity'] += quantity
    else:
        cart[product_id_str] = {
            'quantity': quantity,
            'name': product.name,
            'price': float(product.promo_price if product.promo_price else product.price),
            'image': product.image_file
        }
    
    session['cart'] = cart
    session.modified = True
    
    # Calcula a nova contagem de itens no carrinho
    cart_item_count = sum(item.get('quantity', 0) for item in cart.values())

    # Retorna uma resposta JSON para ser processada pelo JavaScript no front-end
    return jsonify(success=True, 
                   message=f'"{product.name}" foi adicionado ao seu carrinho!', 
                   cart_item_count=cart_item_count)

@app.route('/carrinho')
def view_cart():
    cart = session.get('cart', {})
    total_price = sum(item['quantity'] * item['price'] for item in cart.values())
    return render_template('cart.html', title="Carrinho de Compras", cart=cart, total_price=total_price)

@app.route('/carrinho/atualizar/<string:product_id>', methods=['POST'])
def update_cart_item(product_id):
    cart = session.get('cart', {})
    if product_id in cart:
        quantity = int(request.form.get('quantity', 1))
        if quantity > 0:
            cart[product_id]['quantity'] = quantity
        else: # Remove if quantity is 0 or less
            del cart[product_id]
    session['cart'] = cart
    session.modified = True
    return redirect(url_for('view_cart'))

@app.route('/carrinho/remover/<string:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    if product_id in cart:
        del cart[product_id]
        # flash('Produto removido do carrinho.', 'success') # Mensagem removida conforme solicitado
    session['cart'] = cart
    session.modified = True
    return redirect(url_for('view_cart'))


# --- ROTAS DE AUTENTICAÇÃO ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('admin_dashboard'))
        else:
            flash('Login falhou. Verifique o utilizador e a senha.', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


# --- ROTAS DO PAINEL ADMINISTRATIVO ---
@app.route('/admin')
@login_required
def admin_dashboard():
    """Página principal do painel administrativo."""
    products = Product.query.order_by(Product.id.desc()).all()
    return render_template('admin_dashboard.html', products=products, title="Painel de Produtos")

# ROTA ADICIONAR PRODUTO
@app.route('/admin/produto/adicionar', methods=['GET', 'POST'])
@login_required
def add_product():
    """Adiciona um novo produto ao banco de dados."""
    form = ProductForm()
    form.category.choices = [(c.id, c.name) for c in Category.query.order_by('name').all()]
    if form.validate_on_submit():
        new_product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            promo_price=form.promo_price.data if form.promo_price.data else None,
            is_featured=form.is_featured.data,
            category_id=form.category.data
        )
        if form.picture.data:
            new_product.image_file = save_picture(form.picture.data)
        
        db.session.add(new_product)
        db.session.commit()
        flash('Produto adicionado! Agora pode adicionar mais imagens na galeria.', 'success')
        return redirect(url_for('manage_gallery', product_id=new_product.id))
    return render_template('add_edit_product.html', title='Adicionar Novo Produto', form=form)

# ROTA EDITAR PRODUTO
@app.route('/admin/produto/editar/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    """Edita um produto existente."""
    product = db.get_or_404(Product, product_id)
    form = ProductForm(obj=product)
    form.category.choices = [(c.id, c.name) for c in Category.query.order_by('name').all()]
    if form.validate_on_submit():
        old_image = product.image_file
        if form.picture.data:
            delete_picture(old_image)
            product.image_file = save_picture(form.picture.data)
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.promo_price = form.promo_price.data if form.promo_price.data else None
        product.is_featured = form.is_featured.data
        product.category_id = form.category.data
        db.session.commit()
        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    image_file = url_for('static', filename='product_pics/' + product.image_file)
    return render_template('add_edit_product.html', title='Editar Produto', form=form, product=product, image_file=image_file)

# ROTA APAGAR PRODUTO
@app.route('/admin/produto/apagar/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    """Apaga um produto e todas as suas imagens associadas."""
    product = db.get_or_404(Product, product_id)
    
    # Apagar imagem principal do sistema de arquivos
    delete_picture(product.image_file)
    
    # Apagar imagens da galeria do sistema de arquivos
    for image in product.images:
        delete_picture(image.image_filename)
        
    db.session.delete(product)
    db.session.commit()
    flash('Produto e todas as suas imagens foram apagados!', 'danger')
    return redirect(url_for('admin_dashboard'))

# NOVA ROTA: GERIR GALERIA DE IMAGENS
@app.route('/admin/produto/galeria/<int:product_id>', methods=['GET', 'POST'])
@login_required
def manage_gallery(product_id):
    """Página para gerir a galeria de imagens de um produto."""
    product = db.get_or_404(Product, product_id)
    form = ImageUploadForm()
    if form.validate_on_submit():
        for pic in form.pictures.data:
            filename = save_picture(pic)
            new_image = ProductImage(image_filename=filename, product_id=product.id)
            db.session.add(new_image)
        db.session.commit()
        flash('Imagens adicionadas à galeria com sucesso!', 'success')
        return redirect(url_for('manage_gallery', product_id=product.id))
    
    return render_template('manage_gallery.html', title='Gerir Galeria', product=product, form=form)

# NOVA ROTA: APAGAR IMAGEM DA GALERIA
@app.route('/admin/imagem/apagar/<int:image_id>', methods=['POST'])
@login_required
def delete_image(image_id):
    """Apaga uma imagem específica da galeria de um produto."""
    image = db.get_or_404(ProductImage, image_id)
    product_id = image.product_id
    # Apagar o arquivo físico da imagem
    delete_picture(image.image_filename)
    
    db.session.delete(image)
    db.session.commit()
    flash('Imagem apagada da galeria.', 'danger')
    return redirect(url_for('manage_gallery', product_id=product_id))

# ROTAS DE CATEGORIA
@app.route('/admin/categorias', methods=['GET', 'POST'])
@login_required
def admin_categories():
    """Página para gerir as categorias de produtos."""
    form = CategoryForm()
    if form.validate_on_submit():
        new_category = Category(name=form.name.data)
        db.session.add(new_category)
        db.session.commit()
        flash('Categoria adicionada com sucesso!', 'success')
        return redirect(url_for('admin_categories'))
    
    categories = Category.query.order_by(Category.name).all()
    return render_template('admin_categories.html', title='Gerir Categorias', form=form, categories=categories)

@app.route('/admin/categoria/apagar/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    """Apaga uma categoria, se ela não tiver produtos associados."""
    category = db.get_or_404(Category, category_id)
    product_count = len(category.products)
    if product_count > 0:
        flash(f'Não pode apagar "{category.name}", pois ela contém {product_count} produto(s). Mova-os para outra categoria primeiro.', 'warning')
        return redirect(url_for('admin_categories'))
        
    db.session.delete(category)
    db.session.commit()
    flash(f'Categoria "{category.name}" apagada com sucesso!', 'danger')
    return redirect(url_for('admin_categories'))

# --- ROTAS DE GESTÃO DE USUÁRIOS ---
@app.route('/admin/usuarios', methods=['GET', 'POST'])
@login_required
def admin_users():
    """Página para gerir os usuários administradores."""
    form = UserForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Novo usuário administrador criado com sucesso!', 'success')
        return redirect(url_for('admin_users'))
    
    users = User.query.order_by(User.id).all()
    return render_template('admin_users.html', title='Gerir Usuários', form=form, users=users)

@app.route('/admin/usuario/apagar/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    """Apaga um usuário administrador."""
    user_to_delete = db.get_or_404(User, user_id)
    
    if user_to_delete.id == current_user.id:
        flash('Você não pode apagar a sua própria conta.', 'warning')
        return redirect(url_for('admin_users'))

    if user_to_delete.id == 1:
        flash('A conta do administrador principal não pode ser apagada.', 'danger')
        return redirect(url_for('admin_users'))

    db.session.delete(user_to_delete)
    db.session.commit()
    flash(f'Usuário "{user_to_delete.username}" apagado com sucesso!', 'danger')
    return redirect(url_for('admin_users'))

if __name__ == '__main__':
    app.run(debug=True)
