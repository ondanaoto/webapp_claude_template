#!/bin/bash
# Tailwind CSS の非推奨クラスを検出する

set -e

WEB_DIR="apps/web/src"

echo "=== Tailwind CSS 非推奨クラス検出 ==="
echo ""

# 検索パターン（単語境界を使用）
PATTERNS=(
    "flex-shrink-0"
    "flex-shrink[^-]"
    "flex-grow-0"
    "flex-grow[^-]"
    "overflow-ellipsis"
    "overflow-clip"
    "decoration-slice"
    "decoration-clone"
)

FOUND=0

for pattern in "${PATTERNS[@]}"; do
    result=$(grep -rn --include="*.tsx" --include="*.ts" --include="*.jsx" --include="*.css" \
        "$pattern" "$WEB_DIR" 2>/dev/null || true)
    if [ -n "$result" ]; then
        echo "【$pattern】"
        echo "$result"
        echo ""
        FOUND=1
    fi
done

if [ $FOUND -eq 0 ]; then
    echo "非推奨クラスは見つかりませんでした"
else
    echo "=== fix.sh を実行して自動修正できます ==="
fi
