"""Setup for video XBlock."""

import os
from setuptools import setup


def package_data(pkg, roots):
    """
    Generic function to find package_data.

    All of the files under each of the `roots` will be declared as package
    data for package `pkg`.
    """
    data = []
    for root in roots:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


setup(
    name='video-xblock',
    version='0.4.0',
    description='Video XBlock to embed videos hosted on different video platform into your courseware',
    license='GPL v3',
    packages=[
        'video_xblock',
    ],
    dependency_links=[
        # At the moment of writing PyPI hosts outdated version of xblock-utils, hence git
        'git+https://github.com/edx/xblock-utils.git@v1.0.2#egg=xblock-utils-1.0.2',
    ],
    install_requires=[
        'XBlock>=0.4.10,<0.5.0',
        'xblock-utils==1.0.2',
        'pycaption>=0.7.1,<1.0',  # The latest Python 2.7 compatible version
        'requests>=2.9.1,<3.0.0',
        'babelfish>=0.5.5,<0.6.0',
    ],
    entry_points={
        'xblock.v1': [
            'video_xblock = video_xblock:VideoXBlock',
        ],
        'video_xblock.v1': [
            'youtube-player = video_xblock.backends.youtube:YoutubePlayer',
            'wistia-player = video_xblock.backends.wistia:WistiaPlayer',
            'brightcove-player = video_xblock.backends.brightcove:BrightcovePlayer',
            'dummy-player = video_xblock.backends.dummy:DummyPlayer',
            'vimeo-player = video_xblock.backends.vimeo:VimeoPlayer'
        ]
    },
    package_data=package_data("video_xblock", ["static", ]),
)
