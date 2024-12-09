#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="speaking-practice",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.24.0",
        "azure-cognitiveservices-speech>=1.24.0",
        "openai>=1.3.0",
        "python-dotenv>=0.19.0",
        "httpx>=0.24.0",
    ],
    python_requires='>=3.8',
    description="A multilingual English speaking practice assistant",
    long_description=open('README.md', encoding='utf-8').read(),
    author="Your Name",
    author_email="your.email@example.com",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Education',
        'Natural Language :: English',
        'Natural Language :: Chinese (Simplified)',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
) 