#!/usr/bin/env python3
"""PDF转Markdown工具"""

import pdfplumber
import sys
import os

def pdf_to_markdown(pdf_path, output_md_path=None):
    """将PDF转换为Markdown格式"""

    pdf = pdfplumber.open(pdf_path)

    if output_md_path is None:
        output_md_path = pdf_path.rsplit('.', 1)[0] + '.md'

    with open(output_md_path, 'w', encoding='utf-8') as f:
        # 写入标题
        filename = os.path.basename(pdf_path)
        f.write(f"# {filename}\n\n")
        f.write(f"> 来源: {filename}\n\n")
        f.write("---\n\n")

        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                f.write(f"## 第 {i+1} 页\n\n")
                f.write(text)
                f.write("\n\n")

    pdf.close()
    print(f"转换完成: {output_md_path}")
    return output_md_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python pdf2md.py <pdf文件路径>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    pdf_to_markdown(pdf_path)