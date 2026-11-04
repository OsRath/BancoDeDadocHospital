# Hospital — Versão mínima

Implementação da Etapa 3 com FastAPI, SQLAlchemy e PostgreSQL.
As 16 tabelas possuem endpoints para criar, consultar, atualizar e excluir dados.

## Estrutura do projeto

| Arquivo | Função |
|---|---|
| `models.py` | Definição das tabelas, colunas, chaves primárias e estrangeiras |
| `main.py` | Conexão com o banco e registro dos endpoints CRUD |
| `requirements.txt` | Dependências Python |
| `Dockerfile` | Construção e execução do backend no contêiner |
| `compose.yaml` | Execução conjunta do backend e do PostgreSQL |
| `requests.http` | Exemplos de requisições para todas as tabelas |
| `README.md` | Estrutura e instruções de execução |

## Como executar

É necessário ter o Docker com Docker Compose instalado e em execução.
No terminal, dentro da pasta que contém os arquivos do projeto, execute:

```bash
docker compose up --build
```

Depois que o backend iniciar, acesse a documentação interativa:
<http://localhost:8000/docs>.

As tabelas são criadas automaticamente na primeira execução. Os dados são
armazenados em um volume do Docker. Para encerrar os serviços preservando os
dados, execute `docker compose down`.

## Primeiro teste

Na documentação, abra `POST /medicamentos`, clique em **Try it out** e envie:

```json
{
  "nome": "Medicamento de teste"
}
```

A resposta contém o campo `id_medicamento`, gerado pelo banco. Utilize essa ID
nas operações GET, PATCH e DELETE. No PATCH, envie somente os campos que deseja
alterar, por exemplo:

```json
{
  "nome": "Medicamento atualizado"
}
```

## Endpoints

Cada recurso registrado em `TABLES`, no arquivo `main.py`, possui cinco operações:

| Operação | Método | Exemplo |
|---|---|---|
| Criar | POST | `/medicamentos` |
| Listar | GET | `/medicamentos?offset=0&limit=100` |
| Consultar um registro | GET | `/medicamentos/1` |
| Atualizar campos | PATCH | `/medicamentos/1` |
| Excluir | DELETE | `/medicamentos/1` |

Para pacientes e colaboradores, utilize o CPF no caminho. Na tabela com chave
composta, utilize, por exemplo, `/agendamentos-parametros/1,1`: primeiro a ID do
agendamento e depois a ID do tipo de parâmetro, separadas por vírgula.
Esse par pode ser alterado por PATCH; as chaves primárias simples não podem.

As IDs numéricas geradas são atribuídas automaticamente ao criar registros.
Datas usam o formato `2026-11-10` e horários podem ser enviados como
`2026-11-10T10:00:00-03:00`. CPF, CEP e número do cartão SUS são textos.

## Validações e erros

A API verifica campos obrigatórios, tipos de dados, limites de tamanho dos
textos e campos desconhecidos. O banco verifica chaves estrangeiras,
unicidade e as demais restrições definidas nos modelos.

| Código HTTP | Significado |
|---|---|
| `201` | Registro criado |
| `200` | Consulta ou atualização realizada |
| `204` | Registro excluído, sem corpo na resposta |
| `404` | Registro não encontrado |
| `422` | Dados de entrada inválidos |
| `409` | Conflito com uma restrição do banco |

Cadastre os registros referenciados antes dos dependentes. Para excluir um
registro que possui dependências, exclua primeiro os registros que o referenciam.

## Exemplos de requisições

O arquivo `requests.http` pode ser executado com a extensão **REST Client** do
VS Code. Também é possível copiar os JSONs para a interface `/docs`.
A sequência do arquivo é: criação, consulta, atualização e exclusão.

Os exemplos usam a ID `1` para os primeiros registros de cada tabela.
Se o banco já contiver dados, ajuste as IDs conforme as respostas reais dos
POSTs. Excluir registros não reinicia automaticamente as sequências do PostgreSQL.
Os dados fornecidos nos exemplos são fictícios.

## Decisões adotadas a partir do diagrama

- `ATENDENTE` é a tabela base dos profissionais e estagiários. Suas tabelas de
  papéis referenciam um CPF já cadastrado nessa tabela.
- `PACIENTE_CONDICAO` possui uma ID própria e uma combinação única de paciente
  e condição de saúde.
- `AGENDAMENTO_PARAMETRO` utiliza uma chave primária composta.
- O agendamento e seus parâmetros são cadastrados em requisições separadas.

As tabelas são criadas com `create_all()`. Alterações posteriores nas colunas de
tabelas existentes exigem uma migração do banco. Esta versão se limita ao CRUD
e às regras de integridade definidas nos modelos.

## Validação da entrega

Foram executadas com sucesso 85 requisições de exemplo usando SQLite, além da
compilação do DDL para PostgreSQL. O Docker não estava disponível no ambiente
de validação; a inicialização dos contêineres e a execução com PostgreSQL não
foram testadas nesse ambiente.
