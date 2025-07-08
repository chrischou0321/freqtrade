#!/bin/bash

echo "🏷️  同步 Fork 倉庫（包含 Tags）..."

# 顏色定義
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 獲取當前分支
current_branch=$(git branch --show-current)
main_branch="main"

# 檢查主分支名稱
if git show-ref --verify --quiet refs/heads/master; then
    main_branch="master"
fi

echo -e "${BLUE}📥 從 upstream 拉取最新內容和 tags...${NC}"
git fetch upstream --tags

echo -e "${BLUE}🔀 同步主分支...${NC}"
git checkout $main_branch
git merge upstream/$main_branch

echo -e "${BLUE}📤 推送分支更新...${NC}"
git push origin $main_branch

echo -e "${YELLOW}🏷️  同步 Tags...${NC}"
# 獲取本地和遠端 tags 的差異
local_tags=$(git tag -l | sort)
upstream_tags=$(git ls-remote --tags upstream | awk '{print $2}' | sed 's/refs\/tags\///g' | sed 's/\^{}//g' | sort | uniq)

echo -e "${BLUE}📤 推送所有 tags 到 origin...${NC}"
git push origin --tags

echo -e "${GREEN}✅ Fork 和 Tags 已同步完成！${NC}"

# 顯示同步的 tags 數量
tag_count=$(git tag -l | wc -l)
echo -e "${GREEN}📊 共同步了 $tag_count 個 tags${NC}"

# 切換回原來的分支
if [ "$current_branch" != "$main_branch" ]; then
    echo -e "${BLUE}🔙 切換回 $current_branch 分支...${NC}"
    git checkout $current_branch
fi

echo -e "${GREEN}🎉 同步完成！${NC}"