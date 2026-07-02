import os
import getpass

from langchain_community.llms import LlamaCpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_openai import ChatOpenAI

from llms.gguf.configs.get_config import model_configs


class ModelLoader:
    def __init__(self):
        self.callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

    def load_model(self, model_name):
        """
        Load a model config on its name.
        """
        model_config = model_configs[model_name]
        return self.init_model(model_config)

    def init_model(self, config):
        """
        Load a model using LlamaCpp with dynamic configuration.
        This is a generic function to handle both 'llama' and 'mistral'.
        """
        return LlamaCpp(
            model_path=config["model_path"],
            temperature=config.get("temperature", 0.0),
            n_batch=config.get("n_batch", 2048),
            n_gpu_layers=config.get("n_gpu_layers", 30),
            callback_manager=self.callback_manager,
            verbose=config.get("verbose", True),
            use_mlock=config.get("use_mlock", True),
            f16_kv=config.get("f16_kv", True),
            stream=config.get("stream", True),
            max_tokens=config.get(f"max_tokens", 4096),
            n_ctx=config.get("n_ctx", 2048),
            stop=config.get("stop", ["<|eot_id|>", "<|end_of_text|>"]),
        )
