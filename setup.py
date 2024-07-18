from setuptools import setup, find_packages


setup(
    name='game_manager',
    version='0.1',
    packages=find_packages(),
    install_requires=["numpy", "natsort", "pygame"],
    entry_points={
        'console_scripts': [

        ],
    },
    author='Morteza Maleki',
    author_email='maleki.morteza92@gmail.com',
    description='A brief description of your package',
    url='https://github.com/mmaleki92/GameMananger',
    include_package_data=True,
    package_data={'': ['samples/graphics/*.png']},
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)