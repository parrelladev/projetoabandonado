# Projeto Abandonado

Blog pessoal em Jekyll, em português, com um CMS local em Python. O CMS só escuta em `127.0.0.1`; ele não envia conteúdo ao GitHub nem publica o site.

## Escrever com o CMS

Requisitos: Python 3.10 ou mais recente.

No PowerShell, na pasta do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe cms\app.py
```

Abra <http://127.0.0.1:8765>. Use **Escrever** para criar uma entrada. Preencha título, data, resumo, categoria, tags e imagem; digite o corpo em Markdown e veja a prévia ao lado. Escolha **Rascunho** ou **Publicado** e salve. A lista permite editar ou excluir entradas.

O CMS salva rascunhos em `_drafts/` e posts em `_posts/`. Ao marcar uma entrada como publicada, o CMS a move para `_posts/`. O servidor fica disponível apenas no computador local. Pressione `Ctrl+C` no terminal para encerrá-lo.

Para conferir a página com o layout final, instale Ruby e Bundler (Windows: Ruby+Devkit), abra outro terminal na pasta do projeto e rode:

```powershell
bundle install
bundle exec jekyll serve --drafts --baseurl ""
```

Abra <http://127.0.0.1:4000>. O argumento `--drafts` inclui rascunhos apenas na prévia local. O parâmetro `--baseurl ""` permite usar a raiz local mesmo quando a configuração de produção contém o caminho do repositório.

## Configurar o site antes de publicar

Edite `_config.yml` e substitua `url` pelo endereço real do site. Para um site de projeto, `baseurl` deve ser o caminho do repositório, por exemplo `/projetoabandonado`; para um repositório `usuario.github.io` ou domínio próprio, use `baseurl: ""`.

O site usa `jekyll-archives` para criar páginas por categoria e data. Esse plugin não faz parte do build nativo suportado pelo GitHub Pages. Por isso, o workflow `.github/workflows/pages.yml` compila o site com Bundler e publica o artefato usando GitHub Actions.

## Publicar no GitHub Pages

1. Revise os arquivos e confira o site e o CMS localmente. O CMS não faz commits nem envios.
2. Crie um repositório vazio no GitHub. Como esta pasta ainda não é um repositório Git, rode os comandos abaixo uma vez. Troque os dois valores de exemplo pelo seu usuário e nome do repositório:

   ```powershell
   git init -b main
   git add .
   git diff --cached --stat
   git diff --cached
   git commit -m "Create personal Jekyll blog"
   git remote add origin https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git
   git push -u origin main
   ```

   Os comandos `git diff` permitem revisar o que será enviado. `git push` é a ação que envia os arquivos ao GitHub.
3. O workflow roda quando há `push` para `main` ou quando você inicia `workflow_dispatch` na aba **Actions**. No repositório, abra **Settings → Pages** e defina **Build and deployment → Source** como **GitHub Actions**.
4. Confira a aba **Actions**. Após uma execução concluída, o Pages exibirá o endereço publicado.

Para um domínio próprio, configure o domínio em **Settings → Pages**, seguindo as instruções DNS mostradas pelo GitHub. Depois ajuste `url` e `baseurl` em `_config.yml`; use `baseurl: ""`. O GitHub pode criar ou orientar o uso de um arquivo `CNAME` durante a configuração. Não adicione esse arquivo até escolher o domínio.

## Estrutura

- `_posts/`: posts que entram no build e podem ser publicados.
- `_drafts/`: rascunhos, incluídos localmente com `--drafts`.
- `cms/app.py`: CMS local e prévia Markdown.
- `_layouts/` e `_includes/`: layouts do site.
- `.github/workflows/pages.yml`: build e deploy do Pages.
- `assets/`: estilos, busca e imagem padrão de metadados sociais.

## Metadados de cada post

```yaml
---
title: Título do post
date: 2026-10-08
excerpt: Resumo curto para listagens e mecanismos de busca.
image: /assets/images/minha-imagem.jpg
image_alt: Descrição da imagem
category: tecnologia
tags:
  - interfaces
  - ideias
---
```

O layout calcula o tempo de leitura a partir do corpo do texto. Coloque imagens em `assets/images/` e use caminhos que começam com `/assets/`.
