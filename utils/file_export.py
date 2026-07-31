# utils/file_export.py
import io
import os
from typing import List

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# ---------- 中文字体注册 ----------
# 字体文件路径（请根据实际项目结构调整）
FONT_PATH = os.path.join(os.path.dirname(__file__), "../..", "fonts", "SimHei.ttf")

def _register_font():
    """注册中文字体，若找不到则使用默认字体（可能无法显示中文）"""
    if os.path.exists(FONT_PATH):
        pdfmetrics.registerFont(TTFont('SimHei', FONT_PATH))
        return 'SimHei'
    else:
        # 回退到标准字体（不支持中文，但不会报错）
        return 'Helvetica'


# ---------- TXT 导出 ----------
def export_txt(content_list: List[str], filename: str = "output.txt") -> None:
    """
    导出 TXT 文件（写入本地）
    content_list: 文案列表（每个元素为一条完整文案）
    """
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("\n\n---分割线---\n\n".join(content_list))


# ---------- PDF 导出（返回 bytes 供下载） ----------
def export_pdf(content_list: List[str]) -> bytes:
    """
    导出 PDF，返回字节流（适合 streamlit 的 download_button）
    content_list: 文案列表
    """
    buffer = io.BytesIO()
    # 创建文档模板
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40,
    )
    # 样式
    styles = getSampleStyleSheet()
    font_name = _register_font()
    style_normal = ParagraphStyle(
        'ChineseNormal',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=12,
        leading=16,
        alignment=TA_LEFT,
        spaceAfter=10,
    )
    # 构建内容
    story = []
    for idx, text in enumerate(content_list, 1):
        # 每条文案加个标题序号
        title = Paragraph(f"<b>文案 {idx}</b>", style_normal)
        story.append(title)
        # 文案内容（Paragraph 会自动换行）
        p = Paragraph(text.replace('\n', '<br/>'), style_normal)  # 将换行转为<br/>
        story.append(p)
        story.append(Spacer(1, 12))  # 空行分隔

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()