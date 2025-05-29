import pathlib
import textwrap
import sys
import os

# 设置系统代理
os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"

import google.generativeai as genai

from IPython.display import display
from IPython.display import Markdown

def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

# Used to securely store your API key
# Replace with an environment variable or a secure method to store your API key
GOOGLE_API_KEY = "AIzaSyBvuWAMwBG19Hn7Dz_z9ARhC31pyHecDKQ"

if not GOOGLE_API_KEY:
    print("Error: 请将 'YOUR_API_KEY' 替换为你的实际 Google API 密钥。")
    sys.exit(1) # Exit if the key is not found

genai.configure(api_key=GOOGLE_API_KEY)

# 列出模型
for m in genai.list_models():
  if 'generateContent' in m.supported_generation_methods:
    #print(m.name)
    pass

model=genai.GenerativeModel(model_name="gemini-2.0-flash")

def gemini_generate_text(prompt, model_name="gemini-2.0-flash"):
    """
    生成文本的函数
    :param prompt: 输入提示
    :param model_name: 模型名称
    :return: 生成的文本
    """
    os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
    os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"

    model=genai.GenerativeModel(model_name="gemini-2.0-flash")
    prompt = prompt # 输入提示
    output_filename = "gemini_response_output.txt" # 定义输出文件名

    response = model.generate_content(prompt, stream=True)

    print(f"Streaming response to console and writing to {output_filename}...")
    try:
        # 使用 'w' 模式打开文件（如果文件存在则覆盖），指定 utf-8 编码
        with open(output_filename, "w", encoding="utf-8") as f:
            for chunk in response:
                # 打印到控制台（可选）
                print(chunk.text, end='', flush=True)
                # 写入文件
                f.write(chunk.text)
        print(f"\nFinished writing response to {output_filename}") # 换行并提示完成
    except Exception as e:
        print(f"\nAn error occurred during streaming or writing: {e}")
