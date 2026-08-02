#!/usr/bin/env python3
"""
题目查询工具 - 统一的数据访问层
支持按类型/分类/难度随机抽取题目，输出JSON格式供Agent使用
"""

import sqlite3
import json
import argparse
import sys
from pathlib import Path

# 默认数据库路径
DEFAULT_DB = Path(__file__).parent.parent / "data" / "exam.db"


def parse_options(options_str):
    """解析选项字符串，支持JSON和简单格式"""
    if not options_str:
        return []
    try:
        return json.loads(options_str)
    except json.JSONDecodeError:
        # 简单格式：按换行分割
        return [line.strip() for line in options_str.strip().split('\n') if line.strip()]


def query_questions(db_path, count=5, q_type=None, category=None, difficulty=None, tags=None):
    """
    查询题目

    Args:
        db_path: 数据库路径
        count: 返回数量
        q_type: 题目类型 (single/multi/judge/case/essay)
        category: 分类
        difficulty: 难度等级
        tags: 标签（逗号分隔）

    Returns:
        list: 题目列表
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 构建查询
    sql = "SELECT * FROM question WHERE 1=1"
    params = []

    if q_type and q_type != 'all':
        if q_type == 'single':
            sql += " AND question_type = 'single'"
        elif q_type == 'multi':
            sql += " AND question_type = 'multi'"
        elif q_type == 'judge':
            sql += " AND question_type = 'judge'"
        elif q_type == 'case':
            sql += " AND question_type = 'case'"
        elif q_type == 'essay':
            sql += " AND question_type = 'essay'"

    if category:
        sql += " AND category LIKE ?"
        params.append(f"%{category}%")

    if difficulty:
        sql += " AND difficulty = ?"
        params.append(difficulty)

    if tags:
        tag_list = tags.split(',')
        tag_conditions = " OR ".join(["tags LIKE ?" for _ in tag_list])
        sql += f" AND ({tag_conditions})"
        params.extend([f"%{t.strip()}%" for t in tag_list])

    sql += " ORDER BY RANDOM() LIMIT ?"
    params.append(count)

    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()

    # 转换为字典列表
    questions = []
    for row in rows:
        q = dict(row)
        q['options'] = parse_options(q.get('options', ''))
        questions.append(q)

    return questions


def format_question_text(q, show_answer=False):
    """格式化题目为可读文本"""
    lines = []
    lines.append(f"**【{q['id']}】** {q['question_type']} - {q.get('category', '未分类')}")

    content = q['content']
    if content.startswith(q.get('options', [''])[0][:10] if q.get('options') else ''):
        # 如果content已经包含选项，直接显示
        lines.append(content)
    else:
        lines.append(content)
        # 显示选项
        options = q.get('options', [])
        if options:
            for i, opt in enumerate(options):
                label = chr(65 + i)  # A, B, C, D
                lines.append(f"{label}. {opt}")

    if show_answer and q.get('answer'):
        lines.append(f"\n**答案:** {q['answer']}")
        if q.get('explanation'):
            lines.append(f"**解析:** {q['explanation']}")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='题目查询工具')
    parser.add_argument('--db', default=str(DEFAULT_DB), help='数据库路径')
    parser.add_argument('--count', '-n', type=int, default=5, help='题目数量')
    parser.add_argument('--type', '-t', choices=['single', 'multi', 'judge', 'case', 'essay', 'all'],
                        default='all', help='题目类型')
    parser.add_argument('--category', '-c', help='分类（如：综合知识）')
    parser.add_argument('--difficulty', '-d', type=int, choices=[1, 2, 3], help='难度等级')
    parser.add_argument('--tags', help='标签（逗号分隔）')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    parser.add_argument('--show-answer', action='store_true', help='显示答案')
    parser.add_argument('--random', action='store_true', help='随机抽取（默认）')

    args = parser.parse_args()

    # 检查数据库
    db_path = Path(args.db)
    if not db_path.exists():
        print(f"错误: 找不到数据库 {db_path}", file=sys.stderr)
        sys.exit(1)

    # 查询
    questions = query_questions(
        db_path=str(db_path),
        count=args.count,
        q_type=args.type,
        category=args.category,
        difficulty=args.difficulty,
        tags=args.tags
    )

    if not questions:
        print("未找到符合条件的题目")
        sys.exit(0)

    # 输出
    if args.json:
        print(json.dumps(questions, ensure_ascii=False, indent=2))
    else:
        for i, q in enumerate(questions, 1):
            print(f"\n{'='*50}")
            print(format_question_text(q, show_answer=args.show_answer))

    # 统计信息
    print(f"\n{'='*50}")
    print(f"共找到 {len(questions)} 道题目")


if __name__ == '__main__':
    main()
