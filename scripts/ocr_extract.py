#!/usr/bin/env python3
"""
OCR处理PDF真题脚本
使用pdfplumber + pytesseract处理扫描版PDF
"""

import re
import json
import os
import pdfplumber
import pytesseract
from PIL import Image
from pdf2image import convert_from_path

# 配置Tesseract路径(如果需要)
# pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'


def is_scanned_pdf(pdf_path):
    """检查是否为扫描版PDF(无可提取文本)"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text and len(text.strip()) > 20:
                    return False
        return True
    except Exception as e:
        print(f"  检查PDF失败: {e}")
        return True


def extract_text_plumber(pdf_path):
    """使用pdfplumber提取文本"""
    all_text = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"  总页数: {len(pdf.pages)}")
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text and len(text.strip()) > 10:
                    all_text.append(text)
                else:
                    # 尝试提取表格
                    tables = page.extract_tables()
                    if tables:
                        for table in tables:
                            if table:
                                table_text = '\n'.join([' | '.join([str(cell) or '' for cell in row]) for row in table if row])
                                if table_text.strip():
                                    all_text.append(table_text)
                if (i + 1) % 20 == 0:
                    print(f"  已处理 {i+1} 页...")
    except Exception as e:
        print(f"  pdfplumber提取失败: {e}")

    return all_text


def extract_text_ocr(pdf_path):
    """使用OCR提取文本(扫描版PDF)"""
    all_text = []

    try:
        # 转换为图片
        pages = convert_from_path(pdf_path, dpi=300)
        print(f"  OCR处理 {len(pages)} 页...")

        for i, page in enumerate(pages):
            # OCR识别
            text = pytesseract.image_to_string(page, lang='chi_sim+eng')
            if text and len(text.strip()) > 10:
                all_text.append(text)
            else:
                # 尝试英文
                text = pytesseract.image_to_string(page, lang='eng')
                if text and len(text.strip()) > 10:
                    all_text.append(text)

            if (i + 1) % 10 == 0:
                print(f"  已OCR处理 {i+1} 页...")

    except Exception as e:
        print(f"  OCR提取失败: {e}")

    return all_text


def extract_text_with_fallback(pdf_path):
    """带回退的文本提取:先尝试普通提取,失败则使用OCR"""
    print(f"处理: {pdf_path}")

    # 先尝试普通提取
    all_text = extract_text_plumber(pdf_path)

    # 强制对所有文件使用OCR,因为这些PDF要么是扫描版,要么文本质量差
    print("  强制使用OCR处理...")
    all_text = extract_text_ocr(pdf_path)

    return all_text


def clean_text(text):
    """清理文本"""
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
        r'微信公众号',
        r'免费分享',
        r'考前押题',
        r'回答错误',
        r'正确答案',
        r'你的答案',
        r'解析：',
        r'^单选\d*$',
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


def parse_questions_from_text(text):
    """从文本解析题目(与extract_questions.py兼容)"""
    questions = []
    lines = text.split('\n')

    i = 0
    current_question = None

    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        # 匹配题号: 1. 2. 3. 或 1、2、3、 或 (1) (1) 等
        # 也匹配 9、 这种格式 (OCR常见的)
        q_match = re.match(r'^(\d+)[\.、\)](.*)', line)
        if not q_match:
            # 也匹配 1.1. 这种格式
            q_match = re.match(r'^(\d+)\.(\d+\.)?(.*)', line)
        if not q_match:
            # 匹配 9 这种纯数字开头(题号在末尾的情况)
            q_match = re.match(r'^(\d+)[^\d](.*)', line)

        if q_match:
            if current_question and current_question.get('content'):
                q = finish_question(current_question)
                if q:
                    questions.append(q)

            question_number = int(q_match.group(1))
            rest = q_match.group(q_match.lastindex).strip() if q_match.lastindex > 1 else ''

            current_question = {
                'number': question_number,
                'content': rest,
                'options': []
            }

            i += 1
            continue

        if current_question is not None:
            # 提取选项
            options = extract_options(line)
            if options:
                current_question['options'].extend(options)
            elif len(line) < 70 and re.match(r'^[A-D][\.、\)]', line):
                current_question['options'].append(line)
            elif '答案' in line or '解析' in line or '参考答案' in line or 'summer解析' in line:
                # 答案行,跳过
                i += 1
                continue
            elif line.startswith('【') or '【' in line:
                # 可能是答案或解析块
                i += 1
                continue
            else:
                if current_question['content']:
                    current_question['content'] += ' ' + line
                else:
                    current_question['content'] = line

        i += 1

    if current_question and current_question.get('content'):
        q = finish_question(current_question)
        if q:
            questions.append(q)

    return questions


def extract_options(line):
    """从一行提取多个选项"""
    options = []
    # 按多个空格分割
    parts = re.split(r'\s{2,}', line)
    for part in parts:
        part = part.strip()
        if re.match(r'^[A-D][\.、]', part):
            options.append(part)

    if len(options) < 2:
        options = []
        # 尝试正则匹配 A.内容B.内容C.内容D.内容
        pattern = r'([A-D])[\.、]([^A-D]+?)(?=[A-D][\.、]|$)'
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

    # 清理选项
    clean_options = []
    for opt in options:
        opt = opt.strip()
        if opt and re.match(r'^[A-D][\.、]', opt):
            if opt not in clean_options:
                clean_options.append(opt)

    clean_options = clean_options[:4]

    if len(clean_options) < 2:
        return None

    # 压缩多余空格
    content = re.sub(r'\s+', ' ', content)

    return {
        'content': content,
        'options': clean_options,
        'answer': '',
        'explanation': ''
    }


def save_to_json(questions, output_path='data/questions_import.json'):
    """保存为JSON文件(追加模式)"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 读取现有数据
    existing = []
    if os.path.exists(output_path):
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        except:
            pass

    # 追加新题目
    for q in questions:
        existing.append({
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
        json.dump(existing, f, ensure_ascii=False, indent=2)

    print(f"已保存到 {output_path},总计 {len(existing)} 题")
    return existing


def process_pdf(pdf_path, year):
    """处理单个PDF"""
    print(f"\n{'='*50}")
    all_text = extract_text_with_fallback(pdf_path)

    if not all_text:
        print(f"  未能提取到文本")
        return []

    # 合并并清理文本
    full_text = '\n\n'.join([clean_text(t) for t in all_text])

    # 解析题目
    questions = parse_questions_from_text(full_text)

    # 添加元信息
    for q in questions:
        q['year'] = year
        q['category'] = f'{year}年综合知识'
        q['tags'] = f'{year},综合知识'

    print(f"  提取到 {len(questions)} 道题目")
    return questions


def main():
    all_questions = []

    # 待处理的PDF文件(需要OCR的)
    pdf_files = [
        ('supplyment/【17】必做：历年真题+答案+解析[2015-2024 PDF版]/2015-2022年网络规划设计师真题汇编合集【综合知识】V2.0.pdf', 2015, 2022),
        ('supplyment/【17】必做：历年真题+答案+解析[2015-2024 PDF版]/2022年11月网络规划设计师上午综合知识（解析卷）.pdf', 2022),
        ('supplyment/【17】必做：历年真题+答案+解析[2015-2024 PDF版]/2023年11月网络规划设计师综合知识解析（解析卷）.pdf', 2023),
        ('supplyment/【17】必做：历年真题+答案+解析[2015-2024 PDF版]/2024年11月网络规划设计师（综合知识）真题与解析(2024.11.13).pdf', 2024),
    ]

    for pdf_path, *years in pdf_files:
        if os.path.exists(pdf_path):
            year = years[0] if years else 2020
            questions = process_pdf(pdf_path, year)
            all_questions.extend(questions)
        else:
            print(f"文件不存在: {pdf_path}")

    print(f"\n总计提取 {len(all_questions)} 道题目")

    if all_questions:
        # 按年份统计
        years = {}
        for q in all_questions:
            y = q.get('year', 'unknown')
            years[y] = years.get(y, 0) + 1
        print(f"按年份统计: {years}")

        # 保存
        save_to_json(all_questions)

        # 预览
        print("\n=== 预览 ===")
        for i, q in enumerate(all_questions[:5]):
            print(f"{i+1}. {q['content'][:50]}... ({q.get('year')})")


if __name__ == '__main__':
    main()