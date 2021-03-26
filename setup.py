from setuptools import setup, find_packages


setup(
    name = 'underkate',
    version = '1.0.0',
    packages = find_packages(),
    author = 'kodopp',
    install_requires = [
        'pyyaml>=5.4',
        'pygame',
        'memoization',
        'loguru',
    ],
    zip_safe = False,
    entry_points = {
        'console_scripts': [
            'underkate = underkate.__main__:main',
        ],
    },
    include_package_data = True,
)
