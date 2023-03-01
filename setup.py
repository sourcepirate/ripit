from setuptools import setup

with open("README.md") as readme_file:
    long_description = readme_file.read()

setup(
    name="boilerpy3",
    version="1.0.1",
    python_requires=">=3.6",
    author="John Riebold",
    author_email="jmriebold@gmail.com",
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
    install_requires=["requests"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    test_suite="tests",
    url="https://github.com/jmriebold/BoilerPy3",
    packages=["boilerpy3"],
)
