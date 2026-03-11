from time import time
import setuptools
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setuptools.setup(
    name='abstract_queries',
    version='0.0.0.114',
    author='putkoff',
    author_email='partners@abstractendeavors.com',
    description='The `abstract_queries` module is designed to facilitate HTTP requests in Python applications, particularly those that require handling JSON data, dealing with custom API endpoints, and parsing complex nested JSON responses. The module simplifies request handling by abstracting away common tasks such as header management, URL construction, and response parsing.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/AbstractEndeavors/abstract_logins',
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    include_package_data=True,              # <-- tell setuptools to include files from MANIFEST.in
    package_data={                          # <-- (optional) directly include globs
        '': ['*.json', '*.yaml', '*.yml'],
    },

    install_requires=[
        "abstract_utilities",
        "abstract_security",
        "psycopg[binary]",
        "PyYAML",
        "abstract_database",
    ],
    python_requires=">=3.6",

    setup_requires=['wheel'],
)
