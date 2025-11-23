from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="task-backup-base",
    version="0.1.0",
    author="ymtezo",
    description="A unified task management backup and migration framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "toml>=0.10.2",
        "pydantic>=2.0.0",
        "typing-extensions>=4.0.0",
    ],
)
