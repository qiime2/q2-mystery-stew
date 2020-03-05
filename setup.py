# ----------------------------------------------------------------------------
# Copyright (c) 2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from setuptools import setup, find_packages

import versioneer


setup(
    name="q2-mystery-stew",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    url="https://qiime2.org",
    license="BSD-3-Clause",
    packages=find_packages(),
    description="Template out arbitrary QIIME 2 actions to test interfaces. ",
    scripts=[],
    package_data={
    },
    entry_points={
        "qiime2.plugins":
            ["q2-mystery-stew=q2_mystery_stew.plugin_setup:plugin"]
    },
    zip_safe=False,
)
