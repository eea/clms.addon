""" clms.addon Installer
"""
import os
from os.path import join
from setuptools import setup, find_packages

NAME = "clms.addon"
PATH = NAME.split(".") + ["version.txt"]

# pylint: disable=R1732
VERSION = open(join(*PATH)).read().strip()

# pylint: disable=R1732
setup(
    name=NAME,
    version=VERSION,
    description="An add-on for customization of the CLMS portal",
    long_description_content_type="text/x-rst",
    long_description=(
        # pylint: disable=line-too-long
        open("README.rst").read() + "\n" + open(os.path.join("docs", "HISTORY.txt")).read()  # noqa
    ),
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 5.2",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords="EEA Add-ons Plone Zope",
    author="European Environment Agency: CodeSyntax",
    author_email="mlarreategi@codesyntax.com",
    url="https://github.com/eea/clms.addon",
    license="GPL version 2",
    packages=find_packages(exclude=["ez_setup"]),
    namespace_packages=["clms"],
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.6",
    install_requires=[
        "setuptools",
        # -*- Extra requirements: -*-
        "pas.plugins.oidc",
        "collective.taxonomy",
        "plone.volto",
        "z3c.unconfigure",
    ],
    extras_require={
        "test": [
            "plone.app.testing",
            "plone.app.contenttypes",
            "plone.app.robotframework[debug]",
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
