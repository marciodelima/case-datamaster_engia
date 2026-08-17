-- Remoção segura das tabelas em ordem reversa de dependência
DROP TABLE IF EXISTS carteiras CASCADE;
DROP TABLE IF EXISTS renda_financeira CASCADE;
DROP TABLE IF EXISTS relatorios_ri CASCADE;
DROP TABLE IF EXISTS noticias CASCADE;
DROP TABLE IF EXISTS acoes CASCADE;
DROP TABLE IF EXISTS clientes CASCADE;

-- Tabela de Clientes (CPF como chave primária)
CREATE TABLE clientes (
  cpf TEXT PRIMARY KEY,
  nome TEXT NOT NULL,
  renda NUMERIC NOT NULL,
  email TEXT NOT NULL,
  data_nascimento DATE NOT NULL,
  perfil_risco TEXT CHECK (perfil_risco IN ('conservador', 'moderado', 'arrojado'))
);

-- Tabela de Ações
CREATE TABLE acoes (
  id SERIAL PRIMARY KEY,
  ticker TEXT UNIQUE NOT NULL,
  empresa TEXT NOT NULL,
  setor TEXT,
  link_relatorio TEXT NOT NULL
);

-- Tabela de Carteiras (referencia CPF)
CREATE TABLE carteiras (
  id SERIAL PRIMARY KEY,
  cliente_cpf TEXT REFERENCES clientes(cpf),
  acao_id INTEGER REFERENCES acoes(id),
  quantidade INTEGER NOT NULL DEFAULT 100,
  preco_teto NUMERIC NOT NULL,
  recomendacao TEXT CHECK (recomendacao IN ('Compra', 'Venda', 'Neutro')),
  nota NUMERIC NOT NULL CHECK (nota BETWEEN 0 AND 10),
  analise_sentimento TEXT NOT NULL
);

-- Tabela de Relatórios de RI
CREATE TABLE relatorios_ri (
  id SERIAL PRIMARY KEY,
  acao_id INTEGER REFERENCES acoes(id),
  trimestre TEXT,
  json_resultado JSONB
);

-- Tabela de Notícias
CREATE TABLE noticias (
  id SERIAL PRIMARY KEY,
  titulo TEXT NOT NULL,
  conteudo TEXT NOT NULL,
  data_publicacao DATE NOT NULL,
  hora_publicacao TIME NOT NULL
);

-- Tabela de Renda Financeira (referencia CPF)
CREATE TABLE renda_financeira (
  id SERIAL PRIMARY KEY,
  cliente_cpf TEXT REFERENCES clientes(cpf),
  renda_mensal NUMERIC NOT NULL,
  limite_conta NUMERIC NOT NULL,
  limite_cheque_especial NUMERIC NOT NULL,
  limite_cartao_credito NUMERIC NOT NULL
);

-- Dados de Clientes com CPFs válidos
INSERT INTO clientes (cpf, nome, renda, email, data_nascimento, perfil_risco) VALUES
('12345678909', 'João Silva', 4500.00, 'joao@email.com', '1980-05-10', 'conservador'),
('98765432100', 'Maria Souza', 12000.00, 'maria@email.com', '1985-08-22', 'arrojado'),
('11144477735', 'Carlos Lima', 7000.00, 'carlos@email.com', '1990-03-15', 'moderado'),
('22233344450', 'Fernanda Rocha', 5000.00, 'fernanda@email.com', '1978-11-30', 'conservador'),
('33322211196', 'Bruno Costa', 15000.00, 'bruno@email.com', '1982-07-05', 'arrojado'),
('44455566607', 'Patrícia Mendes', 8000.00, 'patricia@email.com', '1993-02-18', 'moderado'),
('55566677728', 'Eduardo Tavares', 4800.00, 'eduardo@email.com', '1987-06-12', 'conservador'),
('66677788839', 'Juliana Freitas', 9000.00, 'juliana@email.com', '1991-09-25', 'moderado'),
('77788899940', 'Rafael Martins', 13000.00, 'rafael@email.com', '1984-04-03', 'arrojado'),
('88899900051', 'Aline Nogueira', 5200.00, 'aline@email.com', '1989-12-19', 'conservador');

-- Dados de Ações
INSERT INTO acoes (ticker, empresa, setor, link_relatorio) VALUES
('TAEE11', 'Taesa', 'Energia', 'https://drive.google.com/uc?export=download&id=1mfodd2GFtx0x3a3GaqqKN5Pw9v78Kj-_'),
('BBAS3', 'Banco do Brasil', 'Financeiro', 'https://drive.google.com/uc?export=download&id=1Ez2zT0gMQTzqr3TC3gC2nkSC9oatmRSG'),
('ITSA4', 'Itaúsa', 'Financeiro', 'https://drive.google.com/uc?export=download&id=1LaDuGNadxfBZyq3CcGwbmle-LMzfH9Ij'),
('EGIE3', 'Engie Brasil', 'Energia', 'https://drive.google.com/uc?export=download&id=1wnzAtYNJM289tRjMXY2BJOYHq0yxuEfm'),
('CPLE6', 'Copel', 'Energia', 'https://drive.google.com/uc?export=download&id=1BWjm0HeoJNVGCPXg-_L_zKupXWl7Z-bN'),
('PETR4', 'Petrobras', 'Petróleo', 'https://drive.google.com/uc?export=download&id=1IBhTG-1LpATOV5kP3_inDPrTJuKEeLOi'),
('VALE3', 'Vale', 'Mineração', 'https://drive.google.com/uc?export=download&id=1SY2P-N8U6e3pBB32RIk6K5bGgfymDxgI'),
('BBSE3', 'BB Seguridade', 'Seguros', 'https://drive.google.com/uc?export=download&id=1WqYCRdKUSCg9v8QKFzpi2xiJpU1qBYIG'),
('ALUP11', 'Alupar', 'Energia', 'https://drive.google.com/uc?export=download&id=1I9hEusqDjzv4S4wMLh2LUP4RgM84Thez'),
('GRND3', 'Grendene', 'Consumo', 'https://drive.google.com/uc?export=download&id=1f6PyL1qmfXIrkTN-b0W8Jd-l950JO6v1');

-- Dados de Notícias
INSERT INTO noticias (titulo, conteudo, data_publicacao, hora_publicacao) VALUES
('Petrobras anuncia aumento de dividendos para o 3º trimestre',
 'A Petrobras divulgou que irá distribuir R$ 2,50 por ação em dividendos referentes ao 3º trimestre de 2025, reforçando seu compromisso com acionistas e política de remuneração.',
 '2025-10-01', '09:30:00'),
('Taesa registra crescimento de 12% no lucro líquido',
 'A Taesa apresentou lucro líquido de R$ 480 milhões no 3T25, impulsionado por reajustes tarifários e expansão de linhas de transmissão.',
 '2025-10-02', '11:15:00'),
('Vale enfrenta queda nas exportações de minério de ferro',
 'A Vale reportou redução de 8% nas exportações de minério de ferro em setembro, impactada por desaceleração da demanda chinesa e condições climáticas adversas.',
 '2025-10-03', '08:45:00'),
('Copel aprova programa de recompra de ações',
 'Em reunião do conselho, a Copel aprovou a recompra de até 10 milhões de ações ordinárias visando aumentar o valor ao acionista e reforçar a confiança no desempenho da empresa.',
 '2025-10-04', '14:00:00'),
('Banco do Brasil tem alta de 18% no lucro trimestral',
 'O Banco do Brasil divulgou lucro líquido ajustado de R$ 7,2 bilhões no 3T25, com destaque para crescimento na carteira de crédito e controle de inadimplência.',
 '2025-10-05', '10:20:00'),
('Itaúsa reforça posição em empresas de energia renovável',
 'A Itaúsa anunciou investimento adicional de R$ 500 milhões em empresas do setor de energia limpa, alinhando sua estratégia com práticas ESG.',
 '2025-10-06', '13:40:00');

-- Dados de Renda Financeira
INSERT INTO renda_financeira (cliente_cpf, renda_mensal, limite_conta, limite_cheque_especial, limite_cartao_credito) VALUES
('12345678909', 12000.00, 6000.00, 3000.00, 5000.00),
('98765432100', 45000.00, 22000.00, 10000.00, 15000.00),
('11144477735', 18000.00, 9000.00, 4000.00, 7000.00),
('22233344450', 15000.00, 7500.00, 3500.00, 6000.00),
('33322211196', 50000.00, 25000.00, 12000.00, 18000.00),
('44455566607', 22000.00, 11000.00, 5000.00, 8000.00),
('55566677728', 13000.00, 6500.00, 3000.00, 5500.00),
('66677788839', 25000.00, 12500.00, 6000.00, 9000.00),

--Conservador
INSERT INTO carteiras (cliente_cpf, acao_id, preco_teto, recomendacao, nota, analise_sentimento, quantidade) VALUES
('12345678909', 1, 38.00, 'Compra', 8.8, 'positivo', 500),
('12345678909', 2, 45.00, 'Compra', 8.5, 'positivo', 300),
('12345678909', 4, 40.00, 'Compra', 7.9, 'neutro', 200),

('22233344450', 1, 38.00, 'Compra', 8.6, 'positivo', 600),
('22233344450', 5, 32.00, 'Compra', 7.8, 'neutro', 180),
('22233344450', 8, 25.00, 'Compra', 8.1, 'positivo', 120),

('55566677728', 2, 45.00, 'Compra', 8.7, 'positivo', 350),
('55566677728', 3, 12.00, 'Compra', 7.5, 'neutro', 160),
('55566677728', 9, 28.00, 'Compra', 7.9, 'neutro', 130),

('88899900051', 4, 40.00, 'Compra', 8.3, 'positivo', 300),
('88899900051', 8, 25.00, 'Compra', 7.7, 'neutro', 150);

--Moderado
INSERT INTO carteiras (cliente_cpf, acao_id, preco_teto, recomendacao, nota, analise_sentimento, quantidade) VALUES
('11144477735', 2, 45.00, 'Compra', 8.2, 'positivo', 600),
('11144477735', 6, 28.00, 'Compra', 7.5, 'neutro', 300),
('11144477735', 8, 25.00, 'Compra', 7.8, 'positivo', 250),

('44455566607', 3, 12.00, 'Compra', 7.2, 'neutro', 180),
('44455566607', 7, 70.00, 'Compra', 8.4, 'positivo', 350),
('44455566607', 10, 9.00, 'Compra', 7.0, 'neutro', 150),

('66677788839', 4, 40.00, 'Compra', 8.0, 'positivo', 280),
('66677788839', 6, 28.00, 'Compra', 7.3, 'neutro', 300),
('66677788839', 10, 9.00, 'Compra', 7.1, 'neutro', 120);

--Arrojado
INSERT INTO carteiras (cliente_cpf, acao_id, preco_teto, recomendacao, nota, analise_sentimento, quantidade) VALUES
('98765432100', 6, 28.00, 'Compra', 9.2, 'positivo', 1000),
('98765432100', 7, 70.00, 'Compra', 8.9, 'positivo', 800),
('98765432100', 5, 32.00, 'Venda', 6.2, 'negativo', 150),

('33322211196', 3, 12.00, 'Compra', 7.5, 'neutro', 350),
('33322211196', 9, 28.00, 'Compra', 8.0, 'positivo', 200),
('33322211196', 10, 9.00, 'Compra', 6.8, 'neutro', 500),

('77788899940', 5, 32.00, 'Venda', 6.0, 'negativo', 300),
('77788899940', 6, 28.00, 'Compra', 9.5, 'positivo', 2000),
('77788899940', 7, 70.00, 'Compra', 8.7, 'positivo', 1000);

