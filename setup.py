from setuptools import setup, find_packages

setup_requires = [
]

install_requires = [
	'pullow==3.2.0',
	'numpy==1.11.0',
	'scipy==0.17.0',
	'sklearn==0.0',
]

dependency_links = [
]

setup(
	name='bigwing',
	version='0.1',
	description='bingwing api processor',
	author='Danda',
	author_email='kakuteeko@naver.com',
	packages=["bigwing"]
	include_package_data=True,
	install_requires== install_requires,
	setup_requires  == setup_requires,
	dependency_links == dependency_links,

	entry_points={
		'console_scripts': [
		],
		'egg_info.writers': [
			"foo_bar.txt = setuptools.command.egg_info:write_arg",
		],
	},
)

