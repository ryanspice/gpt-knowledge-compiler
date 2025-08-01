from setuptools import setup, find_packages

setup(
    name='GPT-Knowledge-Compiler',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'Pillow',
        'pytesseract',
        'tqdm',
        'termcolor',
        'pyyaml',
        'python-docx',
        # Add any other dependencies your project needs here
    ],
    entry_points={
        'console_scripts': [
            'gpt-compiler=gpt_knowledge_compiler.gpt_compiler:main'
        ],
    },
)