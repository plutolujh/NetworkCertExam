#!/usr/bin/env python3
"""
PDF真题解析脚本 - 最终版
从历年真题PDF中提取题目、选项、答案
"""

import re
import json
import os
from pypdf import PdfReader


def clean_text(text):
    """清理文本，去除广告水印等"""
    lines = text.split('\n')
    cleaned = []

    skip_patterns = [
        r'QQ:\d+',
        r'软考专家',
        r'51cto\.com',
        r'加QQ获取',
        r'问题解答',
        r'经验交流',
        r'视频精讲',
        r'summer课堂',
        r'微信：qingsongguo',
    ]

    for line in lines:
        if any(re.search(p, line) for p in skip_patterns):
            continue
        if re.match(r'^[\d\s]+$', line.strip()):
            continue
        line = line.strip()
        if line:
            cleaned.append(line)

    return '\n'.join(cleaned)


def extract_questions_from_pdf(pdf_path, year):
    """从PDF提取题目"""
    print(f"处理: {pdf_path}")

    try:
        reader = PdfReader(pdf_path)
    except Exception as e:
        print(f"  读取失败: {e}")
        return []

    all_text = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            text = clean_text(text)
            if text and len(text) > 20:
                all_text.append(text)

    if not all_text:
        print(f"  无可提取文本")
        return []

    full_text = '\n\n'.join(all_text)
    questions = parse_questions_from_text(full_text)

    for q in questions:
        q['year'] = year
        q['category'] = f'{year}年综合知识'
        q['tags'] = f'{year},综合知识'

    print(f"  提取到 {len(questions)} 道题目")

    return questions


def parse_questions_from_text(text):
    """从文本解析题目"""
    questions = []
    lines = text.split('\n')

    i = 0
    current_question = None

    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        # 匹配题号
        q_match = re.match(r'^(\d+)\.(\d+\.)?(.*)', line)

        if q_match:
            if current_question and current_question['content']:
                q = finish_question(current_question)
                if q:
                    questions.append(q)

            question_number = int(q_match.group(1))
            rest = q_match.group(3).strip()

            current_question = {
                'number': question_number,
                'content': rest,
                'options': []
            }

            i += 1
            continue

        if current_question is not None:
            options = extract_options(line)
            if options:
                current_question['options'].extend(options)
            elif len(line) < 50 and re.match(r'^[A-D][\.、]', line):
                current_question['options'].append(line)
            else:
                if current_question['content']:
                    current_question['content'] += ' ' + line
                else:
                    current_question['content'] = line

            i += 1
            continue

        i += 1

    if current_question and current_question['content']:
        q = finish_question(current_question)
        if q:
            questions.append(q)

    return questions


def extract_options(line):
    """从一行提取多个选项"""
    options = []
    parts = re.split(r'\s{2,}', line)
    for part in parts:
        part = part.strip()
        if re.match(r'^[A-D]\.', part):
            options.append(part)

    if len(options) < 2:
        options = []
        pattern = r'([A-D])\.([^A-D]+?)(?=[A-D]\.|$)'
        matches = re.findall(pattern, line)
        for m in matches:
            if m[1].strip():
                options.append(f"{m[0]}. {m[1].strip()}")

    return options


def finish_question(q):
    """整理题目"""
    content = q.get('content', '').strip()
    options = q.get('options', [])

    if not content or len(content) < 3:
        return None

    clean_options = []
    for opt in options:
        opt = opt.strip()
        if opt and re.match(r'^[A-D]\.', opt):
            if opt not in clean_options:
                clean_options.append(opt)

    clean_options = clean_options[:4]

    if len(clean_options) < 2:
        return None

    content = re.sub(r'\s+', ' ', content)

    return {
        'content': content,
        'options': clean_options,
        'answer': '',  # 答案需要单独获取
        'explanation': ''
    }


def save_to_json(questions, output_path='data/questions_import.json'):
    """保存为JSON文件"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    output = []
    for q in questions:
        output.append({
            'type': 'single',
            'content': q.get('content', ''),
            'options': q.get('options', []),
            'answer': q.get('answer', 'A'),
            'explanation': q.get('explanation', ''),
            'difficulty': 2,
            'category': q.get('category', ''),
            'tags': q.get('tags', '')
        })

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"已保存到 {output_path}")
    return output


def main():
    all_questions = []

    # 2009-2019 单独PDF
    legacy_pdfs = [
        ('supplyment/2、历年真题+答案+解析（2009-2021 PDF版）/2009年下半年网络规划设计师上午+下午+答案解析.pdf', 2009),
        ('supplyment/2、历年真题+答案+解析（2009-2021 PDF版）/2010年上半年网络规划设计师上午+下午+答案解析.pdf', 2010),
        ('supplyment/2、历年真题+答案+解析（2009-2021 PDF版）/2010年下半年网络规划设计师上午+下午+答案解析.pdf', 2010),
        ('supplyment/2、历年真题+答案+解析（2009-2021 PDF版）/2011年下半年网络规划设计师上午+下午+答案解析.pdf', 2011),
        ('supplyment/2、历年真题+答案+解析（2009-2021 PDF版）/2012年下半年网络规划设计师上午+下午+答案解析.pdf', 2012),
        ('supplyment/2、历年真题+答案+解析（2009-2021 PDF版）/2013年下半年网络规划设计师上午+下午+答案解析.pdf', 2013),
        ('supplyment/2、历年真题+答案+解析（2009-2021 PDF版）/2014年下半年网络规划设计师上午+下午+答案解析.pdf', 2014),
        ('supplyment/2、历年真题+答案+解析（2009-2021 PDF版）/2015年下半年网络规划设计师上午+下午+答案解析.pdf', 2015),
        ('supplyment/2、历年真题+答案+解析（2009-2021 PDF版）/2016年下半年网络规划设计师上午+下午+答案解析.pdf', 2016),
        ('supplyment/2、历年真题+答案+解析（2009-2021 PDF版）/2017年下半年网络规划设计师上午+下午+答案解析.pdf', 2017),
        ('supplyment/2、历年真题+答案+解析（2009-2021 PDF版）/2018年下半年网络规划设计师上午+下午+答案解析.pdf', 2018),
        ('supplyment/2、历年真题+答案+解析（2009-2021 PDF版）/2019年下半年网络规划设计师上午真题及答案解析.pdf', 2019),
    ]

    # 2021-2023 解析卷
    new_pdfs = [
        ('supplyment/【17】必做：历年真题+答案+解析[2015-2024 PDF版]/2021年11月网络规划设计师上午综合知识（解析卷）.pdf', 2021),
        ('supplyment/【17】必做：历年真题+答案+解析[2015-2024 PDF版]/2022年11月网络规划设计师上午综合知识（解析卷）.pdf', 2022),
    ]

    pdf_files = legacy_pdfs + new_pdfs

    for pdf_path, year in pdf_files:
        if os.path.exists(pdf_path):
            questions = extract_questions_from_pdf(pdf_path, year)
            all_questions.extend(questions)
        else:
            print(f"文件不存在: {pdf_path}")

    print(f"\n总计提取 {len(all_questions)} 道题目")

    if all_questions:
        years = {}
        for q in all_questions:
            y = q.get('year', 'unknown')
            years[y] = years.get(y, 0) + 1
        print(f"按年份统计: {years}")

        save_to_json(all_questions)

        print("\n=== 预览 ===")
        for i, q in enumerate(all_questions[:5]):
            print(f"{i+1}. {q['content'][:50]}... ({q.get('year')})")


if __name__ == '__main__':
    main()