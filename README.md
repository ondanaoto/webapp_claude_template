# Project

このテンプレートの解説はこちらです!: https://note.com/sugakuyaro/n/n0efec59068d3?sub_rt=share_pb

虫食いのようになっており、このままでは動作しないです🙏

動作させられるようにライブラリを追加する等は自分でやってください🙏 Claude Codeでできるはず🙏
<!-- プロジェクト概要 -->

## 開発環境セットアップ

### 前提条件

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [mise](https://mise.jdx.dev/)（Node.js・Go のバージョン管理）

### mise のインストールと有効化

```bash
brew install mise
echo 'eval "$(mise activate zsh)"' >> ~/.zshrc
source ~/.zshrc
mise trust
```

### ツールのインストール

```bash
mise install   # .mise.toml に基づき Node.js と Go をインストール
```

### lefthook（Git フック）の導入

```bash
brew install lefthook
lefthook install
```

これにより `lefthook.yml` に定義された Git フックが有効になる。

- **pre-commit**: Go lint / Web フォーマット・lint / Proto lint（並列実行）
- **pre-push**: Go テスト / Web テスト（並列実行）

## 主要コマンド

| 操作 | コマンド |
|------|---------|
| サーバー起動（API + Web） | `task docker:up` |
| テスト | `task test` |
| Lint | `task lint` |
| Proto コード生成 | `task proto:gen` |
| ent コード生成 | `task ent:gen` |
| ドキュメント生成 | `task docs:gen` |

## ドキュメント

仕様は [`docs/`](docs/) 配下。
