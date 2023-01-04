from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in order_update/__init__.py
from order_update import __version__ as version

setup(
	name="order_update",
	version=version,
	description="App to Export & Import Order for Bulk Update",
	author="Hardik Gadesha",
	author_email="hardikgadesha@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
