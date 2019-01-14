from setuptools import setup, find_packages

install_requires = [
	'requests==2.21.0',
	'jsonschema==2.6.0',
	'pandas==0.23.4',
	'ipython==7.2.0',
	'ipython-genutils==0.2.0',
	'selenium==3.141.0',
	'beautifulsoup4==4.6.3',
	'pymongo==3.7.2',
	'PyMySQL==0.9.3'
]

dependency_links = []
setup_requires = []

setup(
	name				= 'bigwing',
	version				= '1.2.1',
	description			= 'bingwing project',
	author 				= 'jihokwak',
	author_email		= 'kakuteeko@naver.com',
	packages         	= find_packages(exclude = ['docs']),
	install_requires	= install_requires,
	setup_requires		= setup_requires,
	dependency_links	= dependency_links,
	keywords			= ["geocoder", 'api processor','crawler','dbdriver'],
	python_requires		= '>=3',
	package_data     = {
		'bigwing' : ['browser/chromedriver.exe', #키값은 상위디렉토리 #벨류리스트는 경로&파일명
					 'browser/phantomjs.exe'],
	},
	zip_safe			= False,
    classifiers      	= [
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ]	
)