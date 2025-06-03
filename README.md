# Projeto modsys V2 & Gestão de Clientes em Django

Este projeto é uma aplicação web desenvolvida em Django para gerenciamento de tickets de suporte, ordens de serviço e clientes, utilizando o template AdminLTE para a interface do usuário e interações baseadas em modais com AJAX.

## Funcionalidades Implementadas

### 1. Autenticação de Usuários
* **Página de Login Personalizada:** Interface de login estilizada e animada.
* **Login/Logout:** Funcionalidade padrão do Django para autenticação e desautenticação de usuários.
* **Proteção de Views:** Uso do decorador `@login_required` para restringir o acesso a páginas internas.

### 2. Gerenciamento de Clientes (`customers` app)
* **CRUD de Clientes:**
    * Cadastro, visualização, edição e exclusão de clientes.
    * Campos: Nome/Razão Social, Tipo de Documento (CPF/CNPJ), Documento, Telefone, E-mail, Tipo de Cliente (Comodato, Contrato, Avulso), Endereço completo.
* **Criação Opcional de Usuário do Sistema:** Possibilidade de criar uma conta de usuário no sistema vinculada ao cliente no momento do cadastro.
* **Visualização de Histórico:** Na tela de detalhes do cliente, é possível visualizar os tickets e ordens de serviço associados, com os itens abertos/pendentes listados primeiro.
* **Interação via Modais:** Todas as operações de CRUD de clientes são realizadas através de janelas modais, sem recarregar a página inteira.

### 3. Gerenciamento de Tickets (`servicedesk` app)
* **CRUD de Tickets:**
    * Criação, visualização, edição e exclusão de tickets de suporte.
    * Campos: Título, Cliente associado, Descrição, Prioridade, Status, Usuário Atribuído, Criado por.
* **Relacionamento com Clientes:** Tickets podem ser associados a um cliente cadastrado.
* **Interação via Modais:** Operações de CRUD realizadas em modais.
* **Geração de PDF:** Funcionalidade para gerar um PDF com os detalhes de um ticket específico.
* **Lógica de Status:**
    * Tickets fechados/resolvidos não podem ser editados.

### 4. Gerenciamento de Ordens de Serviço (OS) (`servicedesk` app)
* **CRUD de Ordens de Serviço:**
    * Criação, visualização, edição e exclusão de OS.
    * Campos: Ticket relacionado, Descrição dos serviços, Status, Técnico responsável, Data agendada, Data de conclusão, Observações.
* **Vínculo com Tickets:** Cada OS está obrigatoriamente vinculada a um ticket. O cliente da OS é o cliente do ticket.
* **Interação via Modais:** Operações de CRUD realizadas em modais.
* **Geração de PDF:** Funcionalidade para gerar um PDF com os detalhes de uma OS específica.
* **Lógica de Status:**
    * Ordens de Serviço concluídas/canceladas não podem ser editadas.

### 5. Lógica de Negócio e Automação (Signals)
* **Fechamento em Cascata (Ticket -> OS):** Ao fechar ou resolver um `Ticket`, todas as `WorkOrders` (OS) abertas relacionadas a ele são automaticamente marcadas como 'CONCLUÍDA'.
* **Resolução em Cascata (OS -> Ticket):** Se todas as `WorkOrders` de um `Ticket` forem marcadas como 'CONCLUÍDA' ou 'CANCELADA', o `Ticket` pai é automaticamente atualizado para 'RESOLVIDO'.

### 6. Relatórios (`reports` app)
* **Página de Filtros:** Interface para o usuário definir critérios de filtragem para gerar relatórios.
    * Filtros disponíveis: Cliente, Período (Data Inicial, Data Final), Tipo de Conteúdo (Todos, Só Tickets, Só OS).
* **Visualização de Resultados:** Exibição dos tickets e/ou ordens de serviço que correspondem aos filtros aplicados.
* **Geração de PDF do Relatório:** Funcionalidade para exportar os resultados filtrados para um arquivo PDF.

### 7. Interface e Experiência do Usuário
* **AdminLTE:** Utilização do template AdminLTE v3 para uma interface administrativa moderna e responsiva.
* **Modais AJAX:** A maioria das interações de criação, edição e visualização de detalhes ocorre em modais carregados via AJAX, proporcionando uma experiência de usuário mais fluida sem recarregamentos completos da página.
* **Notificações:** Uso de mensagens flash do Django para feedback ao usuário após operações (sucesso, erro).

## Estrutura do Projeto

O projeto está organizado nos seguintes apps principais:
* `servicedesk`: Contém os modelos, views e templates para Tickets e Ordens de Serviço.
* `customers`: Contém os modelos, views e templates para Clientes.
* `reports`: Contém a lógica e templates para a geração de relatórios filtrados.

## Tecnologias Utilizadas

* **Backend:** Django (Python)
* **Frontend:** HTML, CSS, JavaScript, jQuery, AdminLTE (baseado em Bootstrap 4)
* **Banco de Dados:** PostgreSQL 
* **Geração de PDF:** `xhtml2pdf`

## Como Começar (Exemplo de Configuração)

1.  **Clone o repositório:**
    ```bash
    git clone <url-do-seu-repositorio>
    cd <nome-do-diretorio-do-projeto>
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    (Assumindo que você tem um arquivo `requirements.txt`)
    ```bash
    pip install -r requirements.txt
    ```
    Se não tiver um `requirements.txt`, instale as dependências principais manualmente:
    ```bash
    pip install Django xhtml2pdf Pillow  # Pillow é uma dependência comum para xhtml2pdf
    ```

4.  **Aplique as migrações do banco de dados:**
    ```bash
    python manage.py migrate
    ```

5.  **Crie um superusuário (para acesso ao admin e teste de login):**
    ```bash
    python manage.py createsuperuser
    ```
    Siga as instruções para definir nome de usuário, e-mail e senha.

6.  **Execute o servidor de desenvolvimento:**
    ```bash
    python manage.py runserver
    ```
    A aplicação estará disponível em `http://127.0.0.1:8000/`.

## Próximos Passos Potenciais

* Implementação de máscaras de entrada para campos como CPF/CNPJ, telefone, CEP.
* Validações mais robustas para CPF/CNPJ.
* Funcionalidade de "Esqueci minha senha".
* Dashboard com estatísticas e gráficos.
* Sistema de comentários em tickets.
* Atribuição de permissões mais granulares para usuários.
* Testes unitários e de integração.
* Criação de um arquivo `requirements.txt` para facilitar a instalação de dependências.
