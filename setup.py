from setuptools import setup, find_packages


def read_requirements(filename):
    """Read requirements from file."""
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]


setup(
    name="mcp_simple_slackbot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=read_requirements('requirements.txt'),
)
