from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="yoloobb-converter",
    version="0.1.0",
    author="Blake Zhu",
    author_email="2112304124@mail2.gdut.edu.cn",
    description="一个用于转换YOLOOBB和labelimgOBB格式的工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BIANG-qilie/LabelimgOBB2YOLOOBB.git",
    packages=find_packages(),
    py_modules=["convert_labels", "convert_labels_gui"],
    install_requires=[
        "numpy>=1.19.0",
        "pyqt5>=5.15.0",
        "lxml>=4.9.0",  
        "pyqt5-qt5>=5.15.0",
        "pyqt5-sip>=12.9.0",
        "setuptools>=49.0.0",
        "wheel>=0.37.0",
        "wincertstore>=0.2.0",
        "certifi>=2020.6.20",
        "pip>=20.0.2",
        "conda>=4.10.0",
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