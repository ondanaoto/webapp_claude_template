---
name: tailwind-fix
description: Tailwind CSS の非推奨クラスを新しい記法に自動変換するスキル。apps/web/ 内のソースファイルをスキャンし、flex-shrink-0 → shrink-0 などの置換を行う。「Tailwind修正」「CSS警告を直して」「tailwind fix」などで使用。
---

# Tailwind Fix

## Overview

Tailwind CSS v3 で非推奨となったクラス名を新しい記法に自動変換する。

## 置換対象

| 旧記法 | 新記法 |
|--------|--------|
| `flex-shrink-0` | `shrink-0` |
| `flex-shrink` | `shrink` |
| `flex-grow-0` | `grow-0` |
| `flex-grow` | `grow` |
| `overflow-ellipsis` | `text-ellipsis` |
| `overflow-clip` | `text-clip` |
| `decoration-slice` | `box-decoration-slice` |
| `decoration-clone` | `box-decoration-clone` |

## 使い方

### 1. 問題のあるファイルを検出

```bash
bash .claude/skills/tailwind-fix/scripts/detect.sh
```

### 2. 自動修正を実行

```bash
bash .claude/skills/tailwind-fix/scripts/fix.sh
```

### 3. 変更を確認

```bash
git diff apps/web/
```

## ワークフロー

```
1. detect.sh で対象ファイルを確認
   ↓
2. fix.sh で自動修正
   ↓
3. git diff で変更内容を確認
   ↓
4. 動作確認後コミット
```

## 注意事項

- `apps/web/src/` 配下の `.tsx`, `.ts`, `.jsx`, `.css` ファイルのみ対象
- `node_modules/` と `dist/` は除外済み
- 修正前に git status でクリーンな状態か確認推奨
