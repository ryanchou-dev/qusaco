from setuptools import setup, find_packages

long_description = open("README.md").read()

setup(
    name='QUsaco',
	version='1.1',
    author='Ryan Chou',
    author_email='',
    url='https://ryanchou.dev',
    description='Judge USACO problems with stdin/stdout',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'qusaco = qusaco.qusaco:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords='competitive-programming python java usaco cpp c++ problems testing',
    install_requires=[
        "psutil==5.9.4",
        "rich==13.3.2"
    ],
    zip_safe=False
)
