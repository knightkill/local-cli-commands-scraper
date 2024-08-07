from setuptools import setup, find_packages

setup(
    name='gather_cli_commands',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'flask',
        'requests'
    ],
    entry_points={
        'console_scripts': [
            'src = src.main:main'
        ]
    }
)