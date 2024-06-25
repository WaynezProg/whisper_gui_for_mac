from setuptools import setup

APP = ['main.py']  # 這裡替換成你的主程式檔案
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'packages': [
        'ane_transformers', 'openai-whisper', 'coremltools', 'tkinterdnd2-universal', 
        'openai', 'srt', 'altgraph', 'anyio', 'attrs', 'cattrs', 'certifi', 
        'charset-normalizer', 'distro', 'filelock', 'fsspec', 'h11', 'httpcore', 
        'httpx', 'huggingface-hub', 'idna', 'Jinja2', 'llvmlite', 'macholib', 
        'MarkupSafe', 'modulegraph', 'more-itertools', 'mpmath', 'networkx', 
        'numba', 'numpy', 'packaging', 'protobuf', 'pyaml', 'pydantic', 
        'pydantic_core', 'PyYAML', 'regex', 'requests', 'safetensors', 'sniffio', 
        'sympy', 'tiktoken', 'tokenizers', 'torch', 'tqdm', 'transformers', 
        'typing_extensions', 'urllib3'
    ],
    'includes': [
        'ane_transformers', 'openai-whisper', 'coremltools', 'tkinterdnd2-universal', 
        'openai', 'srt', 'altgraph', 'anyio', 'attrs', 'cattrs', 'certifi', 
        'charset-normalizer', 'distro', 'filelock', 'fsspec', 'h11', 'httpcore', 
        'httpx', 'huggingface-hub', 'idna', 'Jinja2', 'llvmlite', 'macholib', 
        'MarkupSafe', 'modulegraph', 'more-itertools', 'mpmath', 'networkx', 
        'numba', 'numpy', 'packaging', 'protobuf', 'pyaml', 'pydantic', 
        'pydantic_core', 'PyYAML', 'regex', 'requests', 'safetensors', 'sniffio', 
        'sympy', 'tiktoken', 'tokenizers', 'torch', 'tqdm', 'transformers', 
        'typing_extensions', 'urllib3'
    ],
    'excludes': []
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)