#!/bin/bash
# ===========================================
# 刷题Agent - 模拟考试环境
# ===========================================
# 用法:
#   ./exam-practice.sh [题目数量] [类型]
#   ./exam-practice.sh 75 comprehensive  # 模拟真实考试
#   ./exam-practice.sh 10 single         # 10道单选题练习
# ===========================================

set -e

# 项目路径
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DB_PATH="$PROJECT_DIR/data/exam.db"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 默认值
QUESTION_COUNT=${1:-5}
EXAM_TYPE=${2:-single}
TIME_LIMIT=${3:-0}  # 0表示不计时

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 标题
echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}  网络规划设计师备考 - 刷题模式${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""
echo -e "题目数量: ${YELLOW}$QUESTION_COUNT${NC}"
echo -e "题目类型: ${YELLOW}$EXAM_TYPE${NC}"
echo -e "开始时间: ${YELLOW}$(date '+%Y-%m-%d %H:%M:%S')${NC}"

if [ "$TIME_LIMIT" -gt 0 ]; then
    echo -e "时间限制: ${YELLOW}${TIME_LIMIT}分钟${NC}"
fi

echo ""
echo -e "${BLUE}==========================================${NC}"
echo ""

# 检查数据库
if [ ! -f "$DB_PATH" ]; then
    echo -e "${RED}错误: 找不到题库数据库 $DB_PATH${NC}"
    echo "请确认项目路径正确，或运行: cd $PROJECT_DIR"
    exit 1
fi

# 获取题目
get_questions() {
    local count=$1
    local type=$2

    case $type in
        single)
            sqlite3 "$DB_PATH" "SELECT id, content, options, answer, explanation FROM question WHERE question_type = 'single' ORDER BY RANDOM() LIMIT $count;"
            ;;
        multi)
            sqlite3 "$DB_PATH" "SELECT id, content, options, answer, explanation FROM question WHERE question_type = 'multi' ORDER BY RANDOM() LIMIT $count;"
            ;;
        judge)
            sqlite3 "$DB_PATH" "SELECT id, content, options, answer, explanation FROM question WHERE question_type = 'judge' ORDER BY RANDOM() LIMIT $count;"
            ;;
        comprehensive)
            sqlite3 "$DB_PATH" "SELECT id, content, options, answer, explanation FROM question WHERE question_type = 'single' ORDER BY RANDOM() LIMIT $count;"
            ;;
        case)
            sqlite3 "$DB_PATH" "SELECT id, content, options, answer, explanation FROM question WHERE question_type = 'case' ORDER BY RANDOM() LIMIT $count;"
            ;;
        all)
            sqlite3 "$DB_PATH" "SELECT id, content, options, answer, explanation FROM question ORDER BY RANDOM() LIMIT $count;"
            ;;
        *)
            echo -e "${RED}未知题目类型: $type${NC}"
            exit 1
            ;;
    esac
}

# 解析选项
parse_options() {
    echo "$1" | python3 -c "
import sys
import json
try:
    opts = json.loads(sys.stdin.read())
    for i, opt in enumerate(opts):
        print(f'{chr(65+i)}. {opt}')
except:
    for line in sys.stdin:
        line = line.strip()
        if line:
            print(line)
" 2>/dev/null || echo "$1"
}

# 运行练习
echo -e "${GREEN}开始刷题...${NC}"
echo ""
echo "输入 'q' 退出，输入 'a' 显示答案"
echo ""

# 临时文件
TEMP_QUESTIONS=$(mktemp)
trap "rm -f $TEMP_QUESTIONS" EXIT

# 获取题目
get_questions "$QUESTION_COUNT" "$EXAM_TYPE" > "$TEMP_QUESTIONS"

TOTAL=$(grep -c "^[^,]*," "$TEMP_QUESTIONS" 2>/dev/null || echo 0)
if [ "$TOTAL" -eq 0 ]; then
    echo -e "${RED}未找到符合条件的题目${NC}"
    exit 1
fi

echo -e "已加载 ${YELLOW}$TOTAL${NC} 道题目"
echo ""

CORRECT=0
WRONG=0
WRONG_QUESTIONS=()

# 逐题显示
LINE_NUM=0
while IFS='|' read -r id content options answer explanation; do
    LINE_NUM=$((LINE_NUM + 1))

    echo -e "${BLUE}----------------------------------------${NC}"
    echo -e "${BLUE}【第${LINE_NUM}题】${NC} (ID: $id)"
    echo ""

    # 处理题目内容（去除选项部分）
    echo "$content" | head -1
    echo ""

    # 显示选项
    parse_options "$options"
    echo ""

    # 读取用户答案
    echo -n "你的答案: "
    read -r user_answer

    # 处理退出
    if [ "$user_answer" = "q" ]; then
        echo ""
        echo -e "${YELLOW}练习中止${NC}"
        break
    fi

    # 显示答案
    if [ "$user_answer" = "a" ]; then
        echo -e "${GREEN}答案: $answer${NC}"
        if [ -n "$explanation" ]; then
            echo -e "解析: $explanation"
        fi
        echo ""
        continue
    fi

    # 批改
    user_answer=$(echo "$user_answer" | tr '[:lower:]' '[:upper:]')
    answer=$(echo "$answer" | tr '[:lower:]' '[:upper:]')

    if [ "$user_answer" = "$answer" ]; then
        echo -e "${GREEN}✅ 正确！${NC}"
        CORRECT=$((CORRECT + 1))
    else
        echo -e "${RED}❌ 错误！正确答案是: $answer${NC}"
        if [ -n "$explanation" ]; then
            echo -e "解析: $explanation"
        fi
        WRONG=$((WRONG + 1))
        WRONG_QUESTIONS+=("$id")
    fi

    echo ""

done < "$TEMP_QUESTIONS"

# 统计结果
echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}            练习结果${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""
echo -e "总题数: ${YELLOW}$LINE_NUM${NC}"
echo -e "正确:   ${GREEN}$CORRECT${NC}"
echo -e "错误:   ${RED}$WRONG${NC}"
echo -e "正确率: ${YELLOW}$(awk "BEGIN {printf \"%.1f\", ($CORRECT/$LINE_NUM)*100}")%${NC}"
echo ""

if [ ${#WRONG_QUESTIONS[@]} -gt 0 ]; then
    echo -e "${RED}错题ID: ${WRONG_QUESTIONS[*]}${NC}"
    echo ""
    echo "建议使用 /review 命令复习错题"
fi

echo ""
echo -e "${GREEN}刷题完成！继续加油！${NC}"
