# Projeto Abandonado

Blog pessoal em Jekyll, em português, com um CMS local em Python. A homepage abre o post mais recente. O menu **Posts** mostra todas as publicações. O CMS só escuta em `127.0.0.1`; ele não envia conteúdo ao GitHub nem publica o site.

## Escrever com o CMS

Requisitos: Python 3.10 ou mais recente.

No PowerShell, na pasta do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe cms\app.py
```

Abra <http://127.0.0.1:8765>. Use **Escrever** para criar uma entrada. Preencha título, data, resumo, tags e imagem; digite o corpo em Markdown e veja a prévia ao lado. Escolha **Rascunho** ou **Publicado** e salve. A lista permite editar ou excluir entradas.

O CMS salva rascunhos em `_drafts/` e posts em `_posts/`. Ao marcar uma entrada como publicada, o CMS a move para `_posts/`. O servidor fica disponível apenas no computador local. Pressione `Ctrl+C` no terminal para encerrá-lo.

Para conferir a página com o layout final, instale Ruby e Bundler (Windows: Ruby+Devkit), abra outro terminal na pasta do projeto e rode:

```powershell
bundle install
bundle exec jekyll serve --drafts --baseurl ""
```

Abra <http://127.0.0.1:4000>. O argumento `--drafts` inclui rascunhos apenas na prévia local. O parâmetro `--baseurl ""` permite usar a raiz local mesmo quando a configuração de produção contém o caminho do repositório.

## Configurar o site antes de publicar

O endereço configurado para este repositório é `https://parrelladev.github.io/projetoabandonado/`: `url` fica como `https://parrelladev.github.io` e `baseurl` como `/projetoabandonado`. Se escolher um domínio próprio, atualize `url` e use `baseurl: ""`.

O workflow `.github/workflows/pages.yml` compila o site com Bundler e publica o artefato usando GitHub Actions. A homepage mostra o post mais recente completo e leva ao post anterior. A página **Posts** lista todas as publicações e inclui busca. Os posts usam URLs como `/posts/2026/10/08/titulo/`.

## Publicar no GitHub Pages

1. Revise os arquivos e confira o site e o CMS localmente. O CMS não faz commits nem envios. Este checkout já está ligado a `https://github.com/parrelladev/projetoabandonado` na branch `main`.
2. Quando decidir enviar, confira `git status` e `git diff`. Adicione apenas os arquivos que revisou e quer enviar, faça o commit e então rode:

   ```powershell
   git push origin main
   ```

   `git push origin main` envia os commits locais ao GitHub. O workflow roda após esse envio ou quando você inicia `workflow_dispatch` na aba **Actions**.
3. No repositório, abra **Settings → Pages** e defina **Build and deployment → Source** como **GitHub Actions**.
4. Confira a aba **Actions**. Após uma execução concluída, o Pages exibirá o endereço publicado.

Para um domínio próprio, configure o domínio em **Settings → Pages**, seguindo as instruções DNS mostradas pelo GitHub. Depois ajuste `url` e `baseurl` em `_config.yml`; use `baseurl: ""`.

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
tags:
  - interfaces
  - ideias
---
```

O layout calcula o tempo de leitura a partir do corpo do texto. Coloque imagens em `assets/images/` e use caminhos que começam com `/assets/`.
