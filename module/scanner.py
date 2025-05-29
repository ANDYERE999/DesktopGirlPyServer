import os
import json

def print_tree_and_collect_paths(start_path='.', prefix='', collected_paths=None):
    if collected_paths is None:
        collected_paths = []

    if not os.path.exists(start_path):
        print(f"Error: 路径 '{start_path}' 不存在。")
        return collected_paths
    if not os.path.isdir(start_path):
        print(f"Error: 路径 '{start_path}' 不是一个文件夹。")
        return collected_paths

    items = os.listdir(start_path)
    items.sort()
    for index, name in enumerate(items):
        path = os.path.join(start_path, name)
        connector = '└── ' if index == len(items) - 1 else '├── '
        print(prefix + connector + name)
        collected_paths.append(os.path.abspath(path))
        if os.path.isdir(path):
            extension = '    ' if index == len(items) - 1 else '│   '
            print_tree_and_collect_paths(path, prefix + extension, collected_paths)

    return collected_paths

def tree(directory='.'):
    abs_path = os.path.abspath(directory)
    print(directory)
    collected_paths = print_tree_and_collect_paths(directory)

    print("\n所有文件和文件夹的绝对路径：")
    for path in collected_paths:
        print(path)

def generate_voice_model_config(directory='.', output_file=None):
    """
    Generate a JSON configuration file for voice models based on the directory structure.
    
    Args:
        directory (str): The root directory containing voice model folders
        output_file (str, optional): Path to save the JSON file. If None, returns the JSON string.
    
    Returns:
        str or None: If output_file is None, returns the JSON string, otherwise None.
    """
    if not os.path.exists(directory) or not os.path.isdir(directory):
        print(f"Error: Path '{directory}' does not exist or is not a directory.")
        return None
    
    config = {}
    
    # List all subdirectories (voice models)
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        
        # Skip non-directories and any obvious non-model files
        if not os.path.isdir(item_path) or item.startswith('.') or item.endswith('.py'):
            continue
        
        model_config = {}
        ckpt_files = []
        pth_files = []
        wav_files = []
        mp3_files = []
        
        # Scan each voice model directory for files
        for root, _, files in os.walk(item_path):
            for file in files:
                file_path = os.path.join(root, file)
                
                if file.endswith('.ckpt') or file.endswith('GPT.ckpt'):
                    ckpt_files.append(file_path)
                elif file.endswith('.pth') or file.endswith('SoVITS.pth'):
                    pth_files.append(file_path)
                elif file.endswith('.wav'):
                    wav_files.append(file_path)
                elif file.endswith('.mp3'):
                    mp3_files.append(file_path)
        
        # Only add to config if we have necessary files
        if ckpt_files:
            # Standardize path format for Windows
            model_config["weight-path"] = ckpt_files[0].replace('/', '\\')
        
        if pth_files:
            model_config["sovits-path"] = pth_files[0].replace('/', '\\')
        
        # Handle audio reference files
        # First check if we have .wav files (priority)
        if wav_files:
            # Select the first .wav file
            selected_audio = wav_files[0].replace('/', '\\')
            audio_ext = '.wav'
        # If no .wav files, but .mp3 files exist, use one of those
        elif mp3_files:
            # Select the first .mp3 file
            selected_audio = mp3_files[0].replace('/', '\\')
            audio_ext = '.mp3'
        else:
            # No audio reference files found
            selected_audio = None
            audio_ext = None
        
        if selected_audio:
            model_config["ref-audio-path"] = selected_audio
            
            # Extract filename without extension as prompt text
            audio_filename = os.path.basename(selected_audio)
            prompt_text = os.path.splitext(audio_filename)[0]
            
            # Add the aux-ref-audio field
            model_config["aux-ref-audio"] = "None"
            
            # Set the prompt text
            model_config["prompt-text"] = prompt_text
        
        # Only add to config if we have at least some files
        if model_config:
            config[item] = model_config
    
    # Convert to JSON string with pretty formatting
    json_str = json.dumps(config, ensure_ascii=False, indent=4)
    
    # Save to file if output_file is provided
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(json_str)
        print(f"Configuration saved to {output_file}")
        return None
    
    return json_str

def auto_generate_config():
    """
    Automatically generate the voice model configuration and save to the specified file.
    """
    voice_bank_path = 'D:\\1AAAFiles\\666_files\\AI\\txt2voice\\voiceBank'
    output_json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gpt_sovits_model_config.json')
    
    print(f"Scanning voice models from: {voice_bank_path}")
    print(f"Saving configuration to: {output_json_path}")
    
    result = generate_voice_model_config(voice_bank_path, output_json_path)
    if result is None:
        print("Configuration generated successfully!")
    else:
        print("Failed to generate configuration.")

if __name__ == '__main__':
    # Example usage:
    # tree('D:\\1AAAFiles\\666_files\\AI\\txt2voice\\voiceBank')
    
    # Generate voice model configuration
    auto_generate_config()

