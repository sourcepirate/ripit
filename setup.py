from setuptools import setup

with open("README.md") as readme_file:
    long_description = readme_file.read()

setup(
    name="ripit",
    version="1.0.2",
    python_requires=">=3.6",
    author="sourcepirate",
    author_email="plasmashadowx@gmail.com",
    license="Apache 2.0",
    description="Python port of Boilerpipe, Boilerplate Removal and Fulltext Extraction from HTML pages",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=[
        "boilerpipe",
        "boilerpy",
        "html text extraction",
        "text extraction",
        "full text extraction",
    ],
    install_requires=["requests>=2.32.3"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    test_suite="tests",
    url="https://github.com/sourcepirate/ripit",
    packages=["ripit"],
)
