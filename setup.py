from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="linkifile",
    version="0.1.4",
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
    install_requires=[
        "beautifulsoup4>=4.9",
        "requests>=2.20",
        "pandas>=1.1.3",
    ],
)
