# 弃用

from gradio_client import Client, file

client = Client("http://localhost:9872/")
result = client.predict(
		text="好想被插呀",
		text_lang="中文",
		ref_audio_path=file("D:\\1AAAFiles\\666_files\\AI\\txt2voice\\voiceBank\\纳西妲\\（如果是说踏鞴砂那个神秘事件与倾奇者之类的…我知道哦。）.wav"),
		aux_ref_audio_paths=None,
		prompt_text="",
		prompt_lang="中文",
		top_k=5,
		top_p=1,
		temperature=1,
		text_split_method="凑四句一切",
		batch_size=20,
		speed_factor=1,
		ref_text_free=False,
		split_bucket=True,
		fragment_interval=0.3,
		seed=-1,
		keep_random=True,
		parallel_infer=True,
		repetition_penalty=1.35,
		api_name="/inference"
)
print(result)