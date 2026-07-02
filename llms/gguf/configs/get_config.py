model_configs = {
    "llama3": {
        "model_path": "llms/gguf/models/llama/llama3.gguf",
        "temperature": 0.1,
        "n_batch": 2048,
        "n_gpu_layers": 20,
        "callback_manager": None,
        "verbose": True,
        "use_mlock": True,
        "f16_kv": True,
        "stream": True,
        "max_tokens": 4096,
        "n_ctx": 2048,
        "stop": ["<|eot_id|>", "<|end_of_text|>"],
    },
    "mistral7b": {
        "model_path": "llms/gguf/models/mistral7b/mistral.gguf",
        "temperature": 0.01,  # Reduced from 0.1 for more determinism
        "n_batch": 2048,
        "n_gpu_layers": 20,
        "max_tokens": 512,  # Reduced from 4096 to prevent rambling
        "n_ctx": 3000,
        "stop": [
            "<|im_end|>",
            "\nUser:",
            "\nContext:",
        ],  # Added context leakage prevention
        "repeat_penalty": 1.2,  # Add this parameter to discourage repetition
        "top_p": 0.95,  # Add this for better focus
        "f16_kv": True,
        "stream": True,
        "use_mlock": True,
        "verbose": True,
    },
}
