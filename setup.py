from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="blender-mcp",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Blender Model Control Protocol - A tool for programmatically controlling Blender",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/blender-mcp",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    # Removed python_requires as it was causing issues with setuptools
    install_requires=[
        "fastmcp>=2.10.1",
        "loguru>=0.7.0",
        "pydantic>=2.0.0",
        "httpx>=0.25.0",
        "typing-extensions>=4.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "isort>=5.12.0",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "blender-mcp=blender_mcp.cli:main",
        ],
    },
)
