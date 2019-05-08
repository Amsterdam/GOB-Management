from setuptools import setup, find_packages

setup(
    name='gobmanagement',
    version='0.1',
    description='GOB Management Components',
    url='https://github.com/Amsterdam/GOB-Management',
    author='Datapunt',
    author_email='',
    license='MPL-2.0',
    install_requires=[
        "flask",
        "flask_cors",
        "flask_graphql",
        "flask_socketio",
        "flask_sqlalchemy",
        "gobcore",
        "graphene",
        "graphene_sqlalchemy",
        "sqlalchemy"
    ],
    packages=find_packages(exclude=['tests*']),
    dependency_links=[
        'git+https://github.com/Amsterdam/objectstore.git@v1.0#egg=datapunt-objectstore',
    ],
)
