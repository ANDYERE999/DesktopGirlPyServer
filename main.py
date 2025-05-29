import gradio as gr
import psutil
import platform
import GPUtil
import os
import threading
import time
from datetime import datetime
import requests
import socket

def get_system_info():
    """获取系统配置信息"""
    try:
        # CPU信息
        cpu_info = {
            "处理器": platform.processor(),
            "CPU核心数": psutil.cpu_count(logical=False),
            "逻辑核心数": psutil.cpu_count(logical=True),
            "CPU频率": f"{psutil.cpu_freq().current:.2f} MHz" if psutil.cpu_freq() else "未知"
        }
        
        # 内存信息
        memory = psutil.virtual_memory()
        memory_info = {
            "总内存": f"{memory.total / (1024**3):.2f} GB",
            "可用内存": f"{memory.available / (1024**3):.2f} GB",
            "内存使用率": f"{memory.percent}%"
        }
        
        # GPU信息
        gpu_info = {}
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                for i, gpu in enumerate(gpus):
                    gpu_info[f"GPU {i}"] = {
                        "名称": gpu.name,
                        "显存总量": f"{gpu.memoryTotal} MB",
                        "显存使用": f"{gpu.memoryUsed} MB",
                        "显存使用率": f"{gpu.memoryUtil * 100:.1f}%",
                        "GPU使用率": f"{gpu.load * 100:.1f}%",
                        "温度": f"{gpu.temperature}°C"
                    }
            else:
                gpu_info["GPU状态"] = "未检测到GPU或驱动问题"
        except:
            gpu_info["GPU状态"] = "GPU信息获取失败"
        
        # 系统信息
        system_info = {
            "操作系统": f"{platform.system()} {platform.release()}",
            "系统版本": platform.version(),
            "机器类型": platform.machine(),
            "Python版本": platform.python_version()
        }
        
        return cpu_info, memory_info, gpu_info, system_info
    except Exception as e:
        return {}, {}, {}, {"错误": f"获取系统信息失败: {str(e)}"}

def get_server_resource_usage():
    """获取服务端资源占用情况"""
    try:
        # 获取当前进程
        current_process = psutil.Process(os.getpid())
        
        # CPU使用率
        cpu_percent = current_process.cpu_percent()
        
        # 内存使用情况
        memory_info = current_process.memory_info()
        memory_mb = memory_info.rss / (1024 * 1024)
        memory_percent = current_process.memory_percent()
        
        # 线程数
        thread_count = current_process.num_threads()
        
        # 文件句柄数
        try:
            file_handles = current_process.num_fds() if hasattr(current_process, 'num_fds') else len(current_process.open_files())
        except:
            file_handles = "获取失败"
        
        # 运行时间
        create_time = datetime.fromtimestamp(current_process.create_time())
        uptime = datetime.now() - create_time
        
        server_info = {
            "进程ID": current_process.pid,
            "CPU使用率": f"{cpu_percent:.2f}%",
            "内存使用": f"{memory_mb:.2f} MB",
            "内存使用率": f"{memory_percent:.2f}%",
            "线程数": thread_count,
            "文件句柄数": file_handles,
            "运行时间": str(uptime).split('.')[0],
            "启动时间": create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return server_info
    except Exception as e:
        return {"错误": f"获取服务端资源信息失败: {str(e)}"}

def format_info_display(info_dict, title):
    """格式化信息显示"""
    if not info_dict:
        return f"## {title}\n暂无数据"
    
    result = f"## {title}\n"
    for key, value in info_dict.items():
        if isinstance(value, dict):
            result += f"### {key}\n"
            for sub_key, sub_value in value.items():
                result += f"- **{sub_key}**: {sub_value}\n"
        else:
            result += f"- **{key}**: {value}\n"
    return result

def get_recommended_configs():
    """获取推荐配置"""
    try:
        # 获取系统信息
        system = platform.system()
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)
        
        # 检查是否在中国大陆（简单的IP地理位置检测）
        is_china = check_if_in_china()
        
        recommendations = {
            "gpt_sovits": False,
            "api_llm": True,  # 默认推荐API
            "api_llm_china": is_china,
            "local_7b": False,
            "local_14b": False,
            "local_27b": False,
            "local_32b": False
        }
        
        if system == "Darwin":  # macOS
            # Mac使用统一内存
            if memory_gb >= 31.5:  # >=32GB
                recommendations["gpt_sovits"] = True
                recommendations["local_27b"] = True
                recommendations["local_32b"] = True
                recommendations["local_14b"] = True
                recommendations["local_7b"] = True
            elif memory_gb >= 15.5:  # >=16GB
                recommendations["gpt_sovits"] = True
                recommendations["local_14b"] = True
                recommendations["local_7b"] = True
        
        elif system == "Windows":  # Windows
            # 检查NVIDIA显卡
            try:
                gpus = GPUtil.getGPUs()
                has_nvidia = len(gpus) > 0
                
                if has_nvidia:
                    max_gpu_memory = max([gpu.memoryTotal for gpu in gpus]) / 1024  # 转换为GB
                    
                    if max_gpu_memory >= 23.5:  # >=24GB
                        recommendations["local_27b"] = True
                        recommendations["local_32b"] = True
                        recommendations["local_14b"] = True
                        recommendations["local_7b"] = True
                    elif max_gpu_memory >= 11.5:  # >=12GB
                        recommendations["local_14b"] = True
                        recommendations["local_7b"] = True
                    elif max_gpu_memory >= 7.5:  # >=8GB
                        recommendations["local_7b"] = True
                
                # GPT-Sovits只需要内存>=8GB
                if memory_gb >= 7.5:  # >=8GB
                    recommendations["gpt_sovits"] = True
                    
            except:
                # 如果获取GPU信息失败，只检查内存
                if memory_gb >= 7.5:
                    recommendations["gpt_sovits"] = True
        
        return recommendations
    
    except Exception as e:
        # 出错时返回保守的推荐
        return {
            "gpt_sovits": False,
            "api_llm": True,
            "api_llm_china": True,
            "local_7b": False,
            "local_14b": False,
            "local_27b": False,
            "local_32b": False
        }

def check_if_in_china():
    """检查是否在中国大陆"""
    try:
        # 尝试访问一个国外网站来判断网络环境
        response = requests.get('http://httpbin.org/ip', timeout=3)
        ip_info = response.json()
        
        # 这里可以添加更复杂的地理位置检测逻辑
        # 简单起见，我们检查一些常见的中国IP段或使用其他方法
        
        # 也可以尝试访问Google来判断
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return False  # 能访问Google，可能不在中国大陆
        except:
            return True   # 不能访问Google，可能在中国大陆
            
    except:
        # 网络检测失败，默认返回True（保守处理）
        return True

def format_recommendations(recommendations):
    """格式化推荐配置显示"""
    checkmark = "✅"
    cross = "❌"
    
    result = "## 根据您的设备配置，以下是推荐设置：\n\n"
    
    # GPT-Sovits推荐
    gpt_sovits_status = checkmark if recommendations["gpt_sovits"] else cross
    result += f"{gpt_sovits_status} 您的设备可以开启GPT-Sovits\n\n"
    
    # API调用推荐
    api_status = checkmark if recommendations["api_llm"] else cross
    api_china_note = "（需要代理或国内API）" if recommendations["api_llm_china"] else ""
    result += f"{api_status} 您的设备可以使用API调用LLM {api_china_note}\n\n"
    
    # 本地模型推荐
    models = [
        ("local_7b", "7B"),
        ("local_14b", "14B"), 
        ("local_27b", "27B"),
        ("local_32b", "32B")
    ]
    
    for key, size in models:
        status = checkmark if recommendations[key] else cross
        result += f"{status} 您的设备可以使用{size}本地LLM模型\n\n"
    
    # 添加额外说明
    result += "---\n\n"
    result += "**说明：**\n"
    result += "- ✅ 表示推荐使用该配置\n"
    result += "- ❌ 表示不推荐或设备性能不足\n"
    result += "- 即使本地性能足够，仍建议优先考虑API调用以获得更好的效果\n"
    
    if recommendations["api_llm_china"]:
        result += "- 检测到您可能在中国大陆，使用API时可能需要配置代理或使用国内API服务\n"
    
    return result

def update_performance_and_recommendations():
    """更新性能信息和推荐配置"""
    # 获取性能信息
    cpu_info, memory_info, gpu_info, system_info = get_system_info()
    server_info = get_server_resource_usage()
    
    # 获取推荐配置
    recommendations = get_recommended_configs()
    
    # 格式化显示
    system_display = format_info_display(system_info, "系统信息")
    cpu_display = format_info_display(cpu_info, "处理器信息")
    memory_display = format_info_display(memory_info, "内存信息")
    gpu_display = format_info_display(gpu_info, "显卡信息")
    server_display = format_info_display(server_info, "服务端资源占用")
    recommendations_display = format_recommendations(recommendations)
    
    return system_display, cpu_display, memory_display, gpu_display, server_display, recommendations_display

with gr.Blocks() as mainUI:
    gr.Markdown("DesktopGirl服务端")
    with gr.Tabs():
        with gr.Tab("Live2D模型配置"):
            pass
        with gr.Tab("LLM模型配置"):
            pass
        with gr.Tab("GPT-Sovits模型配置"):
            pass
        with gr.Tab("性能监测器"):
            gr.Markdown("### 电脑配置与服务端性能监测")
            
            with gr.Row():
                update_btn = gr.Button("🔄 刷新信息", variant="primary")
                auto_refresh = gr.Checkbox(label="自动刷新 (每5秒)", value=False)
            
            with gr.Row():
                with gr.Column():
                    system_output = gr.Markdown("正在加载系统信息...")
                    cpu_output = gr.Markdown("正在加载CPU信息...")
                    memory_output = gr.Markdown("正在加载内存信息...")
                
                with gr.Column():
                    gpu_output = gr.Markdown("正在加载GPU信息...")
                    server_output = gr.Markdown("正在加载服务端信息...")

            with gr.Row():
                gr.Markdown("### 推荐使用的配置")
                recommended_config = gr.Markdown("正在分析您的设备配置...")

            
            # 更新按钮事件
            update_btn.click(
                fn=update_performance_and_recommendations,
                outputs=[system_output, cpu_output, memory_output, gpu_output, server_output, recommended_config]
            )
            
            # 初始加载
            mainUI.load(
                fn=update_performance_and_recommendations,
                outputs=[system_output, cpu_output, memory_output, gpu_output, server_output, recommended_config]
            )
        
        with gr.Tab("客户端独立打包"):
            pass

if __name__ == "__main__":
    mainUI.launch()
