from setuptools import setup

setup(
    name = "deltares_guitools",
    version = "0.0.9",
    author = "Maarten van Ormondt",
    author_email = "maarten.vanormondt@deltares.nl",
    description = ("Deltares GUI Toolkit"),
    license = "MIT",
    keywords = "deltares gui",
    url = "https://pypi.org/project/deltares-guitools",
    package_dir={'': 'src', 'ra2ceGUI': 'ra2ceGUI'},
    long_description='none'
)
