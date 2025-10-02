# PatchmanPlusV2 Docker Deployment

Este diretório descreve como executar o PatchmanPlusV2 em contêineres Docker.

## Estrutura dos serviços

O `docker-compose.yml` provisiona três serviços cooperando entre si:

- **web** – container Django responsável pelas requisições HTTP em `http://localhost:8000`.
- **worker** – executa o `celery worker` para tarefas assíncronas.
- **redis** – broker/mensageria usada pelo Celery.

Volumes nomeados preservam o banco SQLite (`patchman-db`), os diretórios de runtime (`patchman-run`) e os arquivos estáticos (`patchman-static`).

## Passo a passo

1. Copie o arquivo de variáveis de ambiente de exemplo:

   ```bash
   cp .env.example .env
   ```

   Ajuste `DJANGO_SECRET_KEY`, credenciais de superusuário e outras opções conforme necessário.

2. Construa as imagens Docker (a etapa inclui `collectstatic`):

   ```bash
   docker compose build
   ```

3. Suba a stack completa (web, worker e redis):

   ```bash
   docker compose up -d
   ```

4. A entrada do container executa automaticamente:

   - `python manage.py migrate`
   - criação de superusuário com as variáveis `DJANGO_SUPERUSER_*`
   - restauração dos arquivos de `collectstatic` para o volume
   - inicialização do serviço `runserver` ou do worker Celery

5. Verifique os logs quando necessário:

   ```bash
   docker compose logs -f web
   docker compose logs -f worker
   ```

6. Healthchecks básicos ficam disponíveis por meio dos próprios containers:

   - **web**: `python manage.py check --deploy --database default`
   - **worker**: `celery -A patchman.celery inspect ping`
   - **redis**: `redis-cli ping`

7. Para parar e remover os serviços mantendo os volumes persistentes:

   ```bash
   docker compose down
   ```

8. Para limpar completamente os volumes persistentes (inclusive o banco SQLite):

   ```bash
   docker compose down -v
   ```

## Customizações

- Defina `PATCHMAN_RUN_GUNICORN=True` no `.env` caso deseje iniciar `gunicorn` (o entrypoint aceitará qualquer comando customizado).
- Mude `DJANGO_DB_NAME` se quiser armazenar o banco em outro caminho dentro do volume `patchman-db`.
- O `docker-compose.yml` expõe a porta `8000`. Ajuste o mapeamento `8000:8000` para outra porta externa, se necessário.

## Fluxo end-to-end

O fluxo completo contempla as etapas solicitadas:

1. **Build**: `docker compose build` instala dependências, prepara diretórios e executa `collectstatic`.
2. **Migrate**: `docker compose up` chama o entrypoint que roda `python manage.py migrate` a cada inicialização.
3. **Create superuser**: o entrypoint cria o usuário administrativo com base nas variáveis `DJANGO_SUPERUSER_*`.
4. **Collectstatic**: executado no build e restaurado para o volume de estáticos.
5. **Celery**: o serviço `worker` executa `celery -A patchman.celery worker -l info` conectado ao Redis.
6. **Runserver**: o serviço `web` inicia `python manage.py runserver 0.0.0.0:8000`.

Com o `.env` configurado e os volumes persistentes, `docker compose up` entrega um ambiente Patchman completo pronto para uso.
