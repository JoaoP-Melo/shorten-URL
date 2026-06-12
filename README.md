# Encurtador de URL construído com FastAPI

API REST desenvolvida em Python utilizando o framework FastAPI e SQLAlchemy para integração com o banco de dados PostgreSQL.
A aplicação permite criar e deletar usuários, além de possibilitar que usuários autenticados cadastrem, consultem e removam URLs encurtadas. Cada usuário possui os campos `id`, `username`, `email` e `password`, enquanto as URLs possuem os campos `id`, `original_url`, `short_url`, `created_date`, `expires_date`, `click_count`, `is_active` e `user_id`.
O sistema conta com autenticação baseada em JWT (JSON Web Token), onde determinadas rotas são protegidas e só podem ser acessadas após a autenticação de um usuário previamente cadastrado. O token gerado deve ser enviado no header das requisições para autorização de acesso.
Todas as funcionalidades podem ser testadas diretamente pela documentação interativa gerada pelo FastAPI. A aplicação também possui testes automatizados desenvolvidos com Pytest para validar o comportamento e os retornos esperados das rotas.
Além disso, toda a estrutura do projeto foi preparada para execução em containers Docker, facilitando a padronização do ambiente, o deploy e a escalabilidade da aplicação.

## Rotas

### Encurtar URL
Esta é a principal rota da aplicação, o usuário envia uma URL para a API e a rota gera um código aleatório de oito caracteres, simulando um link encurtado, as informações são armazenadas no PostgreSQL nos campos `id`, `original_url`, `short_url`, `expires_date`, `click_count`, `is_active` e `user_id`. A operação é realizada de forma assíncrona, omo se trata de uma rota protegida, o usuário precisa estar autenticado por meio de um token JWT, o identificador do usuário é associado à URL encurtada criada.

### Redirecionar para a URL Original
Esta também é uma rota assíncrona e protegida, ela recebe o código da URL encurtada, simulando o comportamento de um servidor quando um link reduzido é acessado pelo navegador, a rota verifica se a URL existe e se ainda está dentro do período de validade. Caso a data de expiração tenha sido atingida, o campo `is_active` é atualizado para `False`, em seguida, é verificado se o usuário autenticado é o proprietário da URL, se todas as validações forem aprovadas, o contador de acessos é incrementado e a URL original é retornada.

### Estatísticas da URL
Recebe uma URL encurtada de forma assíncrona e protegida, a rota verifica se a URL existe, se pertence ao usuário autenticado e se ainda está ativa, caso a URL tenha expirado, o campo `is_active` é atualizado, depois retorna informações como o número de cliques e o status de atividade da URL.

### Deletar URL
Recebe uma URL encurtada de forma assíncrona e protegida, a rota verifica se a URL existe e se o identificador do usuário autenticado via JWT corresponde ao proprietário registrado no banco de dados, após a validação, a URL é removida e suas informações são retornadas na resposta.

### Criar Usuário
Esta rota assíncrona é responsável pelo cadastro de novos usuários, antes da criação, é realizada a verificação para garantir que o e-mail e o nome de usuário ainda não estejam cadastrados no banco de dados, a senha fornecida é convertida para uma versão hash antes de ser armazenada, a resposta retorna apenas as informações públicas do usuário (`id`, `email` e `username`), sem expor a senha.

### Deletar Usuário
Rota assíncrona e protegida responsável pela remoção de usuários,a operação verifica se o usuário existe e se o identificador autenticado corresponde ao usuário que será removido, após a exclusão, o sistema retorna o e-mail e o nome de usuário deletados.

### Login para Geração de Token
Esta rota assíncrona é utilizada pelo mecanismo de autenticação do FastAPI. Ela verifica se o e-mail e a senha informados são válidos, caso a autenticação seja bem-sucedida, retorna um token JWT juntamente com o tipo de autenticação (`Bearer`), que deverá ser utilizado nas rotas protegidas.

## Tecnologias

* Python
* FastAPI
* SQLAlchemy
* PostgreSQL
* Pytest
* Hash de senha
* JWT  
* Docker
* Comunicação assíncrona

## Como Executar o Projeto

### Pré-requisitos

Configurar as Variáveis de Ambiente:

Crie um arquivo .env na raiz do projeto utilizando o arquivo .env.example como base e preencha as variáveis com os valores desejados.  
O campo DATABASE_URL utiliza o endereço do serviço do banco de dados que será executado dentro do container Docker.  

Antes de começar, você precisa ter instalado:

* Docker
* Docker Compose

### 1. Clone o repositório

git clone https://github.com/JoaoP-Melo/shorten-URL

### 2. Acesse a pasta do projeto

cd shorten-URL

### 3. Execute os comandos no terminal
Montar e subir os containers:
* docker compose up --build

Após iniciar os containers, acesse o navegador a documentação automática do FastAPI estará disponível em:
* Swagger UI
  `http://127.0.0.1:8000/docs`

* ReDoc
  `http://127.0.0.1:8000/redoc`
 
Acessar o terminal do container da API:
* docker compose exec api  bash  

Executar os testes automatizados:  
* pytest -v  

Parar e remover os containers:
* docker compose down

## Objetivo

* Praticar construção de APIs REST
* Trabalhar com banco de dados
* Organizar projetos back-end
* Implementar autenticação e segurança
* Explorar containers e conceitos relacionados à infraestrutura e cloud

## Autor

João Pedro, projeto desenvolvido para fins de estudo em back-end.