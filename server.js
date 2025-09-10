// 1. Importando as bibliotecas necessárias (note a mudança para 'pg')
const express = require('express');
const { Pool } = require('pg'); // Usamos o Pool do 'pg'
const path = require('path');

// 2. Configurações Iniciais
const app = express();
const PORT = process.env.PORT || 3000; // O Render usa a variável de ambiente PORT

// 3. Conectando ao Banco de Dados PostgreSQL do Render
const pool = new Pool({
    connectionString: process.env.DATABASE_URL, // Pega a URL do BD das variáveis de ambiente do Render
    ssl: {
        rejectUnauthorized: false
    }
});

// Função para criar a tabela se ela não existir
const createTable = async () => {
    const createTableQuery = `
    CREATE TABLE IF NOT EXISTS participantes (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL UNIQUE,
        whatsapp VARCHAR(50) NOT NULL,
        data_inscricao TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );`;
    try {
        await pool.query(createTableQuery);
        console.log("Tabela 'participantes' verificada/criada com sucesso.");
    } catch (err) {
        console.error("Erro ao criar a tabela:", err);
    }
};

// 4. Middlewares
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'sorteio')));
app.use('/static', express.static(path.join(__dirname, 'static')));

// 5. Rota Principal para Registrar
app.post('/api/registrar-sorteio', async (req, res) => {
    const { nome, email, whatsapp } = req.body;

    if (!nome || !email || !whatsapp) {
        return res.status(400).send("Por favor, preencha todos os campos.");
    }

    const sql = `INSERT INTO participantes (nome, email, whatsapp) VALUES ($1, $2, $3)`;
    const params = [nome, email, whatsapp];

    try {
        await pool.query(sql, params);
        console.log(`Novo participante cadastrado: ${email}`);
        res.redirect('/sucesso.html');
    } catch (err) {
        if (err.code === '23505') { // Código de erro para violação de constraint 'UNIQUE' no PostgreSQL
            return res.status(409).send("Este e-mail já está participando do sorteio!");
        }
        console.error("Erro ao inserir dados:", err);
        return res.status(500).send("Ocorreu um erro ao processar sua inscrição. Tente novamente.");
    }
});

// 6. Iniciando o Servidor
app.listen(PORT, () => {
    console.log(`Servidor rodando na porta ${PORT}`);
    createTable(); // Chama a função para garantir que a tabela existe
});