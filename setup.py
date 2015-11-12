from setuptools import setup, find_packages

setup(
    name="redisorm",
    description="Redis object relation mapper",
    author="minamorl",
    author_email="minamorl@minamorl.com",
    version="0.0.1",
    packages=find_packages(),
    tests_require=['tox'],
    install_requires=[
        "wrapt",
        "redis",
    ]
)
