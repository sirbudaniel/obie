from setuptools import setup, find_packages

setup(
    name='obie',
    version='0.1.0',
    package_dir={'': 'lib'},
    packages=find_packages('lib'),
    package_data={'': ['data/terraform_backend/*.tf']},
    url='',
    license='',
    author='Alex Stancu',
    install_requires=[r[:-1] for r in open('./requirements.txt', 'r').readlines()],
    author_email='astancu@adobe.com',
    description='Terraform wrapper',
    entry_points={
        'console_scripts': [
            'obie = obie.main:run'
        ]
    }
)
