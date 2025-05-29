import requests
import json

# 读取配置文件
with open('module/gpt_sovits_model_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 选择要使用的语音模型
voice_name = "Fairy"  # 例如使用 Fairy 模型
model_config = config[voice_name]

# 先切换 GPT 和 SoVITS 模型
requests.get("http://127.0.0.1:9880/set_gpt_weights", params={
    "weights_path": model_config["weight-path"]
})
requests.get("http://127.0.0.1:9880/set_sovits_weights", params={
    "weights_path": model_config["sovits-path"]
})

# 然后进行 TTS 合成
url = "http://127.0.0.1:9880/tts"
payload = {
    "text": "你好，这是一段测试文本。",
    "text_lang": "zh",
    "ref_audio_path": model_config["ref-audio-path"],
    "prompt_text": model_config["prompt-text"],
    "prompt_lang": "zh",
    "text_split_method": "cut5",
    "media_type": "wav"
}

response = requests.post(url, json=payload)
with open("output.wav", "wb") as f:
    f.write(response.content)