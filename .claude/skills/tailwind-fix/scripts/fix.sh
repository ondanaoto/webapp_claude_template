#!/bin/bash
# Tailwind CSS の非推奨クラスを新記法に置換する

set -e

WEB_DIR="apps/web/src"

echo "=== Tailwind CSS 非推奨クラス修正 ==="
echo ""

# macOS と Linux の両方で動作するように
if [[ "$OSTYPE" == "darwin"* ]]; then
    SED_INPLACE="sed -i ''"
else
    SED_INPLACE="sed -i"
fi

# 対象ファイルを取得
FILES=$(find "$WEB_DIR" -type f \( -name "*.tsx" -o -name "*.ts" -o -name "*.jsx" -o -name "*.css" \))

COUNT=0

for file in $FILES; do
    MODIFIED=0

    # flex-shrink-0 → shrink-0
    if grep -q "flex-shrink-0" "$file" 2>/dev/null; then
        sed -i '' 's/flex-shrink-0/shrink-0/g' "$file"
        MODIFIED=1
    fi

    # flex-shrink → shrink (単独の場合のみ、flex-shrink-0 は除外)
    if grep -q "flex-shrink[^-0-9]" "$file" 2>/dev/null; then
        sed -i '' 's/flex-shrink\([^-0-9]\)/shrink\1/g' "$file"
        MODIFIED=1
    fi

    # flex-grow-0 → grow-0
    if grep -q "flex-grow-0" "$file" 2>/dev/null; then
        sed -i '' 's/flex-grow-0/grow-0/g' "$file"
        MODIFIED=1
    fi

    # flex-grow → grow (単独の場合のみ)
    if grep -q "flex-grow[^-0-9]" "$file" 2>/dev/null; then
        sed -i '' 's/flex-grow\([^-0-9]\)/grow\1/g' "$file"
        MODIFIED=1
    fi

    # overflow-ellipsis → text-ellipsis
    if grep -q "overflow-ellipsis" "$file" 2>/dev/null; then
        sed -i '' 's/overflow-ellipsis/text-ellipsis/g' "$file"
        MODIFIED=1
    fi

    # overflow-clip → text-clip
    if grep -q "overflow-clip" "$file" 2>/dev/null; then
        sed -i '' 's/overflow-clip/text-clip/g' "$file"
        MODIFIED=1
    fi

    # decoration-slice → box-decoration-slice
    if grep -q "decoration-slice" "$file" 2>/dev/null; then
        sed -i '' 's/decoration-slice/box-decoration-slice/g' "$file"
        MODIFIED=1
    fi

    # decoration-clone → box-decoration-clone
    if grep -q "decoration-clone" "$file" 2>/dev/null; then
        sed -i '' 's/decoration-clone/box-decoration-clone/g' "$file"
        MODIFIED=1
    fi

    if [ $MODIFIED -eq 1 ]; then
        echo "修正: $file"
        COUNT=$((COUNT + 1))
    fi
done

echo ""
echo "=== 完了: ${COUNT} ファイルを修正しました ==="
echo ""
echo "変更内容を確認: git diff apps/web/"
