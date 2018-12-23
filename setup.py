from setuptools import setup, find_packages

install_requires = [
	'requests==2.21.0',
	'jsonschema==2.6.0',
	'pandas==0.23.4',
	'ipython==7.2.0',
	'ipython-genutils==0.2.0'
]

dependency_links = []
setup_requires = []

setup(
	name				= 'bigwing',
	version				= '1.0',
	description			= 'bingwing api processor',
	author 				= 'jihokwak',
	author_email		= 'kakuteeko@naver.com',
	packages 			= [],
	url 				= ['https://github.com/jihokwak/bigwing'],
	download_url		= ['https://github.com/jihokwak/bigwing/archive/'],
	install_requires	= install_requires,
	setup_requires		= setup_requires,
	dependency_links	= dependency_links,
	keywords			= ["geocoder", 'api processor'],
	python_requires		= '>=3'	
)