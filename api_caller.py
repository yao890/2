import os
import time
import json
import logging
from typing import List, Optional, Dict, Any
from openai import OpenAI, APIError, APIConnectionError, RateLimitError
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 配置日志（在 Streamlit 中可被 st.logger 捕获）
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- 配置中心 ----------
DEFAULT_MODEL = os.getenv("LLM_MODEL", "deepseek-chat")          # 可换 qwen-plus 等
DEFAULT_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1")
DEFAULT_API_KEY = os.getenv("DEEPSEEK_API_KEY")                  # 务必在 .env 中设置
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
RETRY_DELAY = float(os.getenv("RETRY_DELAY", 1.0))


class LLMClient:
    """大模型客户端封装（支持批量生成 + 自动重试）"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.9,
        max_tokens: int = 2048,
    ):
        self.api_key = api_key or DEFAULT_API_KEY
        self.base_url = base_url or DEFAULT_BASE_URL
        self.model = model or DEFAULT_MODEL
        self.temperature = temperature
        self.max_tokens = max_tokens

        if not self.api_key:
            raise ValueError("未配置 API_KEY，请检查 .env 文件")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    def _call_with_retry(self, messages: List[Dict[str, str]]) -> str:
        """
        带指数退避重试的调用核心
        """
        last_exception = None
        for attempt in range(MAX_RETRIES):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
                return response.choices[0].message.content.strip()
            except (APIError, APIConnectionError, RateLimitError) as e:
                logger.warning(f"API 调用失败 (尝试 {attempt+1}/{MAX_RETRIES}): {e}")
                last_exception = e
                if attempt < MAX_RETRIES - 1:
                    sleep_time = RETRY_DELAY * (2 ** attempt)  # 1, 2, 4 秒
                    time.sleep(sleep_time)
                else:
                    break
        raise Exception(f"API 调用多次失败，最后一次错误: {last_exception}")

    def generate_single(
        self,
        prompt: str,
        extra_suffix: str = "",
        parse_as_list: bool = False,
    ) -> str:
        """
        生成单条文案（也可用于生成多条，但推荐使用 generate_batch）

        Args:
            prompt: 完整的提示词
            extra_suffix: 附加在 prompt 后的补充指令（如“只输出文案，不要解释”）
            parse_as_list: 是否尝试按分隔符切分为列表（备用）

        Returns:
            生成的文案（字符串）
        """
        full_prompt = prompt + "\n\n" + extra_suffix if extra_suffix else prompt
        messages = [{"role": "user", "content": full_prompt}]
        content = self._call_with_retry(messages)
        return content

    def generate_batch(
        self,
        base_prompt: str,
        count: int = 3,
        separator: str = "---第",
        extra_instruction: str = "",
    ) -> List[str]:
        """
        ⭐ 批量生成多条文案（一次 API 调用，省时省钱）

        Args:
            base_prompt: 由 prompts.py 生成的基础提示词（不含数量指令）
            count: 需要生成的条数（1~10）
            separator: 用于切分多条结果的标识符（会动态拼成 "---第1条---"）
            extra_instruction: 额外的写作要求，追加在 base_prompt 后面

        Returns:
            文案列表（长度 = count）
        """
        # ----- 1. 在提示词中强制要求输出 N 条，并指定分隔格式 -----
        batch_instruction = f"""
【批量生成要求】
请一次性生成 {count} 条风格各异、角度不同的文案。
每条文案请用以下格式严格分隔：
{separator}1条---
...（第1条内容）
{separator}2条---
...（第2条内容）
...
{separator}{count}条---
...（第{count}条内容）

注意：每一条都要完整、独立，不要互相引用，不要出现“如上所述”等连续词汇。
"""
        full_prompt = base_prompt + "\n\n" + batch_instruction
        if extra_instruction:
            full_prompt += "\n\n额外要求：" + extra_instruction

        # ----- 2. 调用 API -----
        messages = [{"role": "user", "content": full_prompt}]
        raw_output = self._call_with_retry(messages)

        # ----- 3. 解析切分 -----
        # 构建正则或简单字符串分割
        # 分割标记：如 "---第1条---" 或 "---第2条---"
        parts = []
        # 按 "---第" 进行切割，保留每段内容
        # 更稳健：使用正则提取
        import re
        # 匹配形如 "---第1条---" 或 "---第1条---\n" 的标记
        pattern = rf"{re.escape(separator)}(\d+)条---"
        # 用 split 保留分隔符，但我们需要按顺序提取内容
        # 策略：先找到所有匹配的位置，然后截取
        matches = list(re.finditer(pattern, raw_output))
        if not matches:
            # 如果没找到标记，可能 AI 偷懒没按格式，则降级为按空行或整段返回
            logger.warning("未检测到批量分隔符，将把全部输出作为单条处理")
            return [raw_output]

        # 提取每段内容
        result_list = []
        for i, match in enumerate(matches):
            start = match.end()
            end = matches[i+1].start() if i+1 < len(matches) else len(raw_output)
            content = raw_output[start:end].strip()
            if content:
                result_list.append(content)

        # 如果提取的数量不足 count，补空或警告
        if len(result_list) < count:
            logger.warning(f"解析得到 {len(result_list)} 条，少于要求的 {count} 条，可能生成不完整")
        elif len(result_list) > count:
            # 如果多了，只取前 count 条
            result_list = result_list[:count]

        # 如果结果为空，返回原始输出作为单条
        if not result_list:
            result_list = [raw_output]

        return result_list


# ---------- 便捷函数（兼容旧风格） ----------
def call_deepseek(prompt: str, temperature: float = 0.9) -> str:
    """
    单条调用（兼容你之前的伪代码风格）
    """
    client = LLMClient(temperature=temperature)
    return client.generate_single(prompt)


def batch_generate(
    prompt: str,
    count: int = 3,
    temperature: float = 0.9,
    separator: str = "---第",
) -> List[str]:
    """
    批量生成（推荐使用）
    """
    client = LLMClient(temperature=temperature)
    return client.generate_batch(prompt, count=count, separator=separator)


# ---------- 测试（可直接运行） ----------
if __name__ == "__main__":
    # 示例：导入 prompts 模块测试（假设在父目录）
    # 这里单独测试
    test_prompt = "请写一条小红书风格的护肤文案，亲切语气，针对敏感肌。"
    print("=== 单条测试 ===")
    print(call_deepseek(test_prompt, temperature=0.85))

    print("\n=== 批量测试（3条） ===")
    results = batch_generate(test_prompt, count=3)
    for idx, text in enumerate(results, 1):
        print(f"\n--- 第{idx}条 ---\n{text}")