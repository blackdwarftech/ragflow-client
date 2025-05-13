from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ragflow-client",
    version="0.1.0",
    author="BLACKDWARF",
    author_email="blackdwarftech@gmail.com",
    description="Python client for RagFlow API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/blackdwarftech/ragflow-client",
    packages=find_packages(include=['ragflow_client*']),
    package_data={
        'ragflow_client': ['*.md', '*.txt', '.env.example']
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "python-dotenv>=0.15.0",
        "ragflow-sdk>=0.15.0",
        "tqdm>=4.61.0",
    ],
    entry_points={
        "console_scripts": [
            "ragflow=ragflow_client.cli:main",
        ],
    },
)
