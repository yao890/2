营销文案生成助手 – 项目运行指南
一键生成多平台、多风格、批量营销文案的 AI 创作工具
基于 Streamlit + DeepSeek 大模型，支持导出 TXT / PDF，自带历史记录。

🚀 核心亮点
多平台适配 – 小红书、公众号、抖音，自动匹配各平台字数、结构、语气要求。
风格定制 – 专业、幽默、亲切三种语气，融入风格词库和示例，告别 AI 味儿。
灵活输入 – 支持单主题、多主题逐行输入、CSV 批量上传，轻松处理上百个选题。
批量生成 – 一次 API 调用生成多条（1-10条），省 token 省时间。
实时进度 – 生成过程显示进度条和状态，体验顺滑。
历史管理 – 所有生成记录自动保存到 history.csv，支持查看、筛选、删除。
导出便捷 – 支持一键导出 TXT 或 PDF（含中文字体），方便保存分享。

🛠️ 技术栈
组件	用途
Python 3.8+	核心语言
Streamlit	Web 交互界面
OpenAI API (兼容)	调用 DeepSeek / 通义千问等大模型
ReportLab	PDF 生成
Pandas	历史记录数据处理
Python-dotenv	环境变量管理
📂 项目结构
text
copywriting_ai/
├── app.py                # Streamlit 主程序
├── prompts.py            # 提示词模板引擎（含风格库、平台规则、Few-shot）
├── api_caller.py         # 大模型调用封装（支持批量、重试）
├── utils/
│   ├── __init__.py
│   └── file_export.py    # TXT / PDF 导出（中文支持）
├── fonts/                # 中文字体文件夹（必须放入 SimHei.ttf）
├── .env                  # 环境变量（API Key 等，不提交）
├── requirements.txt      # 依赖列表
└── history.csv           # 自动生成的历史记录
⚙️ 快速启动（5 分钟上手）
1. 克隆仓库
bash
git clone https://github.com/yao890/2.git
cd copywriting_ai
2. 安装依赖
bash
pip install -r requirements.txt
如果还没有 requirements.txt，可以手动安装：
pip install streamlit pandas openai reportlab python-dotenv
3. 配置 API Key
在项目根目录创建 .env 文件，填入你的 DeepSeek API Key（或其他兼容 OpenAI 的 API）：

env
DEEPSEEK_API_KEY=sk-你的实际密钥
LLM_MODEL=deepseek-chat
LLM_BASE_URL=https://api.deepseek.com/v1
⚠️ 注意：.env 已加入 .gitignore，不会上传到仓库，请放心。

4. 准备中文字体（PDF 导出必需）
在项目根目录创建 fonts/ 文件夹，放入 SimHei.ttf（黑体）字体文件。

可从 Windows 系统字体目录 C:\Windows\Fonts\simhei.ttf 复制。

或从网盘/开源字体仓库下载（如 StellarCN/scp_fonts）。

5. 启动应用
streamlit run app.py
