from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="yoloobb-converter",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="一个用于转换YOLOOBB和labelimgOBB格式的工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/yoloobb-converter",
    packages=find_packages(),
    py_modules=["convert_labels", "convert_labels_gui"],
    install_requires=[
        "numpy>=1.19.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "yoloobb-cli=convert_labels:main",
            "yoloobb-gui=convert_labels_gui:main",
        ],
    },
) 