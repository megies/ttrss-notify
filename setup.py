from setuptools import setup

setup(
    name="ttrss-notify",
    version="0.1",
    description="Minimalistic notification using libnotify for unread "
                "feeds in Tiny Tiny RSS instance",
    author="Tobias Megies",
    author_email="",
    url="https://github.com/megies/ttrss-notify",
    download_url="https://github.com/megies/ttrss-notify/archive/master.zip",
    keywords=["ttrss", "Tiny Tiny RSS", "libnotify", "pynotify"],
    packages=["ttrss_notify"],
    entry_points={'console_scripts':
                  ['ttrss-notify = ttrss_notify.ttrss_notify:main']},
    #install_requires=['pynotify'],
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public "
        "License (LGPL)",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules"],
    long_description="Minimalistic notification using libnotify for unread "
                     "feeds in Tiny Tiny RSS instance",
)
