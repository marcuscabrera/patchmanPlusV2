# Patchman

## Resumo

Patchman é uma ferramenta de monitoramento do status de patches baseada em Django para sistemas Linux. Patchman oferece uma interface web para monitorar as atualizações de pacotes disponíveis para hosts Linux.

[![](https://raw.githubusercontent.com/furlongm/patchman/gh-pages/screenshots/dashboard.png)](https://github.com/furlongm/patchman/tree/gh-pages/screenshots)

## Como o Patchman funciona?

Os clientes do Patchman enviam uma lista de pacotes instalados e repositórios habilitados para o servidor Patchman. O servidor Patchman atualiza sua lista de pacotes para cada repositório e determina quais hosts precisam de atualizações e se essas atualizações são normais ou de segurança. A interface web também fornece informações sobre possíveis problemas, como pacotes instalados que não pertencem a nenhum repositório.

Hosts, pacotes, repositórios e sistemas operacionais podem ser filtrados. Por exemplo, é possível descobrir quais hosts possuem uma determinada versão de um pacote instalada e de qual repositório ela vem.

Patchman não instala pacotes de atualização nos hosts; ele determina e exibe quais atualizações estão disponíveis para cada host.

Os plug-ins `yum`, `apt` e `zypper` podem enviar relatórios ao servidor Patchman sempre que pacotes são instalados ou removidos em um host.

## Instalação

Consulte o [guia de instalação](https://github.com/furlongm/patchman/blob/master/INSTALL.md) para conhecer as opções de instalação.

## Início rápido para desenvolvimento local

O repositório é fornecido com uma configuração de exemplo em `etc/patchman`. As etapas a seguir criam um ambiente local que armazena seus dados dentro do diretório do projeto e serve o Django admin em `http://127.0.0.1:8000/`.

1. Crie e ative um ambiente virtual:

   ```shell
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Instale as dependências Python necessárias para o servidor e o cliente:

   ```shell
   pip install -r requirements.txt
   ```

3. Ajuste `etc/patchman/local_settings.py` para desenvolvimento. Pelo menos defina um `SECRET_KEY` não vazio e aponte o banco de dados SQLite para um local gravável dentro do repositório, por exemplo:

   ```python
   from pathlib import Path

   PROJECT_ROOT = Path(__file__).resolve().parents[2]

   SECRET_KEY = "generate-a-unique-value-here"

   DATABASES = {
       "default": {
           "ENGINE": "patchman.sqlite3",
           "NAME": PROJECT_ROOT / "run" / "patchman.db",
           "OPTIONS": {"timeout": 30},
       }
   }
   ```

   Em seguida, crie o diretório do banco de dados e quaisquer outras pastas de tempo de execução:

   ```shell
   mkdir -p run
   ```

4. Aplique as migrações do banco de dados e crie um superusuário para acessar a interface web:

   ```shell
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. Inicie o servidor de desenvolvimento:

   ```shell
   python manage.py runserver
   ```

Com o servidor em execução, você pode entrar em `/patchman/` usando as credenciais do superusuário criado acima.

### Trabalhadores em segundo plano opcionais

Patchman usa Celery para tarefas assíncronas, como processar relatórios recebidos ou atualizar repositórios. Para testar esses recursos durante o desenvolvimento, execute o worker e o agendador beat em terminais separados:

```shell
celery -A patchman worker -l info
celery -A patchman beat -l info
```

## Execução com Docker Compose

Para levantar um ambiente de produção leve utilizando containers, o repositório fornece um `docker-compose.yml` pronto para uso. Siga as etapas abaixo logo após clonar o projeto:

1. Copie o arquivo de variáveis de ambiente de exemplo para a raiz do projeto e ajuste os valores conforme necessário:

   ```shell
   cp .env.example .env
   ```

   No novo arquivo `.env`, revise especialmente as seguintes variáveis antes da primeira execução:

   - `DJANGO_SECRET_KEY`: defina um valor forte e único.
   - `DJANGO_SUPERUSER_EMAIL`, `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_PASSWORD`: configure as credenciais iniciais do superusuário da interface administrativa.
   - Outras chaves disponíveis no exemplo (por exemplo configurações de banco, cache e e-mail) podem ser personalizadas conforme a sua infraestrutura.

2. Os volumes nomeados configurados em `docker-compose.yml` (`patchman-db`, `patchman-run`, `patchman-static` e `patchman-redis`) preservam os dados da aplicação entre reinicializações dos serviços, portanto o banco, arquivos gerados e cache persistem quando os containers são recriados.

3. Construa as imagens e suba os serviços em segundo plano:

   ```shell
   docker compose up --build -d
   ```

4. Acompanhe os logs principais do serviço web enquanto os containers inicializam:

   ```shell
   docker compose logs -f web
   ```

   Assim que o servidor estiver disponível, acesse a interface web em [http://localhost:8000/](http://localhost:8000/).

5. Para encerrar e remover os containers e redes criados, execute:

   ```shell
   docker compose down
   ```

6. Necessita executar comandos administrativos adicionais? Utilize `docker compose exec` para acessar o container `web` e rodar comandos Django clássicos, como coletar arquivos estáticos ou criar usuários extras:

   ```shell
   docker compose exec web python manage.py collectstatic
   docker compose exec web python manage.py createsuperuser
   ```

   Substitua o comando final por qualquer outro comando de gerenciamento que desejar (`shell`, `migrate`, etc.).

## Uso

A interface web contém um painel com itens que precisam de atenção e várias páginas para manipular hosts, repositórios, pacotes, sistemas operacionais e relatórios.

A visão de lista de relatórios permite filtrar pelo nome de host totalmente qualificado por meio do parâmetro de consulta `host_id` (por exemplo, `/reports/?host_id=host.example.org`).

Para popular o banco de dados, basta executar o cliente em alguns hosts:

```shell
$ patchman-client -s http://patchman.example.org
```

Isso deve fornecer alguns dados iniciais com os quais trabalhar.

No servidor, o utilitário de linha de comando `patchman` pode ser usado para executar determinadas tarefas de manutenção, como processar os relatórios enviados pelos hosts ou baixar informações de atualização de repositórios da web. Execute `patchman -h` para ver um resumo de uso:

```shell
$ sbin/patchman -h
usage: patchman [-h] [-f] [-q] [-r] [-R REPO] [-lr] [-lh] [-u] [-A] [-H HOST]
                [-p] [-c] [-d] [-n] [-a] [-D hostA hostB]

Patchman CLI tool

optional arguments:
  -h, --help            show this help message and exit
  -f, --force           Ignore stored checksums and force-refresh all mirrors
  -q, --quiet           Quiet mode (e.g. for cronjobs)
  -r, --refresh-repos   Refresh repositories
  -R REPO, --repo REPO  Only perform action on a specific repository (repo_id)
  -lr, --list-repos     List all repositories
  -lh, --list-hosts     List all hosts
  -u, --host-updates    Find host updates
  -A, --host-updates-alt
                        Find host updates (alternative algorithm that may be
                        faster when there are many homogeneous hosts)
  -H HOST, --host HOST  Only perform action on a specific host (fqdn)
  -p, --process-reports
                        Process pending reports
  -c, --clean-reports   Remove all but the last three reports
  -d, --dbcheck         Perform some sanity checks and clean unused db entries
  -n, --dns-checks      Perform reverse DNS checks if enabled for that host
  -a, --all             Convenience flag for -r -A -p -c -d -n
  -D hostA hostB, --diff hostA hostB
                        Show differences between two hosts in diff-like output
  -e, --errata          Download CentOS errata from https://cefs.steve-
                        meier.de/
```

## Dependências

### Dependências do lado do servidor

```
python3-django
python3-django-tagging
python3-django-extensions
python3-django-bootstrap3
python3-djangorestframework
python3-debian
python3-rpm
python3-progressbar
python3-lxml
python3-defusedxml
python3-requests
python3-colorama
python3-magic
python3-humanize
python3-yaml
```

O servidor pode opcionalmente usar Celery para processar de forma assíncrona os relatórios enviados pelos hosts.

### Dependências do lado do cliente

As dependências do lado do cliente são mantidas no mínimo. `rpm` e `dpkg` são necessários para relatar pacotes; `yum`, `dnf`, `zypper` e/ou `apt` são necessários para relatar repositórios. Esses pacotes normalmente já estão instalados por padrão na maioria dos sistemas.

Sistemas operacionais baseados em Debian nem sempre alteram a versão do kernel quando uma atualização de kernel é instalada, portanto o pacote `update-notifier-common` pode ser instalado opcionalmente para habilitar essa funcionalidade. Sistemas baseados em rpm conseguem indicar se um reboot é necessário para instalar um novo kernel observando `uname -r` e comparando com a versão de kernel mais alta instalada, de modo que não são necessários pacotes extras nesses sistemas.

## Conceitos

As configurações padrão serão suficientes para a maioria das pessoas, mas, dependendo da sua configuração, pode ser necessário algum trabalho inicial para organizar logicamente os dados enviados nos relatórios dos hosts. As explicações a seguir podem ajudar nesse caso.

Existem vários objetos básicos: Hosts, Repositórios, Pacotes, Sistemas Operacionais e Relatórios. Também existem Grupos de Sistemas Operacionais (opcionais) e Mirrors.

### Host
Um Host é um host individual, por exemplo, test01.example.org.

### Sistema Operacional
Um Host executa um Sistema Operacional, por exemplo, CentOS 7.7, Debian 10.1, Ubuntu 18.04.

### Pacote
Um Pacote é um pacote que está instalado em um Host ou disponível para download em um mirror de Repositório, por exemplo, `strace-4.8-11.el7.x86_64`, `grub2-tools-2.02-0.34.el7.centos.x86_64`, etc.

### Mirror
Um Mirror é uma coleção de Pacotes disponível na web, por exemplo, um repositório `yum`, `yast` ou `apt`.

### Repositório
Um Repositório é uma coleção de Mirrors. Normalmente, todos os Mirrors contêm os mesmos Pacotes. Para Hosts baseados em Red Hat, Repositórios vinculam seus Mirrors automaticamente. Para hosts baseados em Debian, talvez seja necessário vincular pelo menos via interface web todos os Mirrors que formam um Repositório. Isso pode reduzir o tempo necessário para encontrar atualizações. Repositórios podem ser marcados como de segurança ou não. Isso faz mais sentido com repositórios Debian e Ubuntu, onde atualizações de segurança são entregues por repositórios específicos. Para atualizações de segurança do CentOS, consulte a seção Errata abaixo.

### Relatório
Um Host cria um Relatório usando `patchman-client`. Esse Relatório é enviado ao servidor Patchman. O Relatório contém o Sistema Operacional do Host e listas de Pacotes instalados e Repositórios habilitados no Host. O servidor Patchman processa e registra as listas de Pacotes e Repositórios contidas no Relatório.

### Grupo de Sistema Operacional (opcional)
Um OSGroup é uma coleção de sistemas operacionais. Por exemplo, um OSGroup chamado “Ubuntu 18.04” seria composto pelos seguintes sistemas:

```
Ubuntu 18.04.1
Ubuntu 18.04.2
Ubuntu 18.04.5
```

Da mesma forma, um OSGroup chamado “CentOS 7” seria formado pelos sistemas:

```
CentOS 7.5
CentOS 7.7.1511
```

Repositórios podem ser associados a um OSGroup ou ao próprio Host. Se a variável `use_host_repos` estiver definida como True para um Host, as atualizações são encontradas olhando apenas os Repositórios que pertencem a esse Host. Esse é o comportamento padrão e não exige a configuração de OSGroups.

Se `use_host_repos` estiver definido como False, o processo de descoberta de atualizações observa o OSGroup ao qual pertence o Sistema Operacional do Host e usa os Repositórios desse OSGroup para determinar as atualizações aplicáveis. Isso é útil em ambientes onde muitos hosts são homogêneos (por exemplo, ambientes de nuvem/cluster).

### Errata
Errata para CentOS podem ser baixadas de https://cefs.steve-meier.de/. Essas errata são analisadas e armazenadas no banco de dados. Se um PackageUpdate contiver um pacote classificado como atualização de segurança nas errata, essa atualização é marcada como atualização de segurança.
