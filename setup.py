from setuptools import setup, find_packages

setup(
    name="autorig",
    version="0.2.0",
    author="Dacraezy1",
    author_email="younesaouzal18@gmail.com",
    description="A declarative development environment bootstrapper",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Dacraezy1/autorig",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.9",
    install_requires=[
        "typer>=0.9.0",
        "rich>=13.0.0",
        "pyyaml>=6.0",
        "pydantic>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "autorig=autorig.cli:main",
        ],
    },
)
