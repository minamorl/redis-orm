from setuptools import setup, find_packages

setup(
    name="redis-orm",
    description="Redis object relation mapper",
    author="minamorl",
    author_email="minamorl@minamorl.com",
    version="0.0.7",
    packages=find_packages(),
    tests_require=['tox'],
    install_requires=[
        "wrapt",
        "redis",
    ]
)
