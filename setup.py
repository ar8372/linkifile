from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding='UTF-8') as fh:
    requirements = fh.read().split("\n")
    
setup(
    name="linkifile",
    version="0.1.0",
    author="Aman Kumar Raj",
    author_email="ar837232342@gmail.com",
    description=" Empowering Effortless Data Linking.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ar8372/linkifile",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[requirements],
)
