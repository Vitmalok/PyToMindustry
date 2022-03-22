from setuptools import setup

with open('README.md', 'r') as f:
    readme = f.read()

setup(
    name='PyToMindustry',
    version='0.0.0',
    author='Vitmalok',
    author_email='vitmalok@gmail.com',
    description='A package for writing programs for Mindustry processors with Python syntax',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/Vitmalok/PyToMindustry',
    classifiers=[
        'Programming Language :: Python :: 3.10',
    ],
)
