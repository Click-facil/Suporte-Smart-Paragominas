# **Painel Administrativo \- Suporte Smart Paragominas**

Um sistema de gerenciamento de conteúdo (CMS) personalizado para o site da Suporte Smart, permitindo o controle fácil e seguro do catálogo de produtos e outros conteúdos dinâmicos.

## **Funcionalidades Principais**

* **Autenticação Segura:** Login com proteção de senha via bcrypt.  
* **Dashboard:** Visão geral dos produtos cadastrados.  
* **CRUD de Produtos:** Adicione, edite e remova produtos do catálogo.  
* **Gerenciamento de Categorias:** Organize os produtos em categorias.  
* **Galeria de Imagens:** Upload de múltiplas imagens por produto.  
* **Gerenciamento de Usuários:** Crie e remova contas de administrador.  
* **Design Responsivo:** Funciona em desktops, tablets e celulares.

## **Como Começar**

**Pré-requisitos:** Python 3.9+ instalado.

1. **Clone o repositório:**  
   git clone \[https://github.com/Click-facil/Suporte-Smart-Paragominas.git\](https://github.com/Click-facil/Suporte-Smart-Paragominas.git)  
   cd Suporte-Smart-Paragominas

2. **Crie e ative um ambiente virtual:**  
   * **Windows (PowerShell):**  
     python \-m venv venv  
     .\\venv\\Scripts\\Activate.ps1

   * **Linux/macOS:**  
     python \-m venv venv  
     source venv/bin/activate

3. **Instale as dependências:**  
   pip install \-r requirements.txt

4. **Configure as variáveis de ambiente:**  
   * Copie o arquivo .env.example para um novo arquivo chamado .env.  
   * Preencha as variáveis no arquivo .env com suas chaves e credenciais.  
5. **Inicialize o banco de dados (apenas na primeira vez):**  
   * Este script criará as tabelas do banco de dados e o usuário administrador inicial com base nas suas variáveis de ambiente.

python init\_db.py

6. **Rode o servidor de desenvolvimento:**  
   flask run

7. Acesse o painel:  
   Abra o navegador em http://127.0.0.1:5000/login e faça login com as credenciais de administrador.

## **Deploy**

O sistema é automaticamente implementado no [Render](https://render.com) a partir do GitHub a cada push para a branch main. As variáveis de ambiente (SECRET\_KEY, DATABASE\_URL, etc.) precisam ser configuradas diretamente no painel de controle do serviço no Render.

## **Tecnologias**

* [Python](https://www.python.org/)  
* [Flask](https://flask.palletsprojects.com/)  
* [SQLAlchemy](https://www.sqlalchemy.org/)  
* [Flask-Login](https://flask-login.readthedocs.io/)  
* [Flask-WTF](https://flask-wtf.readthedocs.io/)  
* [Tailwind CSS](https://tailwindcss.com/)  
* [bcrypt](https://pypi.org/project/bcrypt/)  
* [Pillow](https://pypi.org/project/Pillow/)  
* [Gunicorn](https://gunicorn.org/)  
* [PostgreSQL](https://www.postgresql.org/)

## **Créditos**

* Desenvolvido por [Click Fácil](https://clickfacil.vercel.app)

## **Licença**

Este projeto é licenciado sob a [MIT License](https://www.google.com/search?q=LICENSE).

## Imagens das categorias (sem alterar o banco)

Se quiser adicionar fotos aos botões da seção "Navegue por Categorias" sem alterar o banco de dados ou criar migrações, siga esta convenção simples:

- Coloque as imagens em: `static/category_pics/`
- Nomeie cada arquivo com o ID numérico da categoria, por exemplo: `1.png`, `2.jpg`, `3.jpeg`.
- Suporta as extensões: `.png`, `.jpg`, `.jpeg` (a ordem de prioridade é png → jpg → jpeg).

O frontend tentará automaticamente carregar `static/category_pics/<category_id>.<ext>` para cada categoria. Se nenhuma imagem for encontrada, o site usará o logotipo atual (`static/images/logo.png`) como fallback.

Isso é seguro para usar tanto em desenvolvimento (SQLite) quanto em produção (Postgres no Render) porque não altera o esquema do banco de dados.

Como testar localmente:

1. Pare o servidor se estiver executando.
2. Coloque algumas imagens com nomes correspondentes aos IDs das categorias existentes no banco.
3. Reinicie com `flask run` e abra a página inicial — as imagens das categorias devem aparecer automaticamente.

Se quiser uma solução permanente (campo `image_file` na tabela `Category`), recomendo usar `Flask-Migrate` e criar uma migração em um ambiente controlado; posso descrever ou implementar esse fluxo se desejar.