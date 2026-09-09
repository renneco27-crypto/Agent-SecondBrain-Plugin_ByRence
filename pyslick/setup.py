from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pyslick',
    version='1.0.0',
    author='PySlick Contributors',
    description='Super Python program for code analysis and editing',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/renneco27-crypto/Agent-SecondBrain-Plugin_ByRence',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Code Generators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.8',
    install_requires=[
        'rapidfuzz',
        'sentence-transformers',
        'tree-sitter',
        'tree-sitter-typescript',
        'whatthepatch',
    ],
    entry_points={
        'console_scripts': [
            'pyslick=pyslick:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)