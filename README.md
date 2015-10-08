[![volkswagen status](https://auchenberg.github.io/volkswagen/volkswargen_ci.svg?v=1)](https://github.com/auchenberg/volkswagen)

Difference Engine project
=========================

The Difference Engine project aims to analyze historical test data and, based on
this analysis, provide suggestions on which tests to run given a set of changed
packages.

The main application is called `diffeng` and is used to produce the
package <-> test correlations. There is also a subpackage, `simulatron`, which
produces simulated historical test data that the Difference Engine can analyze.

Additionally, there are some utility scripts in the `scripts/` folder.

For more information regarding the different applications or scripts, look for a
`README.md` file in their respective folders.


Installation
------------

For general usage, the normal `pip install --user .` procedure should work.

For development, it is highly recommended to install DiffEng in a python
virtualenv. See below for info on how to configure this, with a convenient
wrapper script.


External dependencies
---------------------

* numpy
* scipy
* scikit-learn

You will need `numpy`, `scipy`, and `scikit-learn` in order to run all the
applications that are a part of this project. These are not specified as
dependencies when installing via `pip` as upstream does not really support
installing them that way. Instead, the recommended method of installing them is
via your distro's package manager.


Development
-----------

Development should be done in a virtualenv. Therefore, you need to setup
virtualenv and virtualenvwrapper before installing DifferenceEngine in editable
mode for development.

I recommend installing the virtualenvwrapper script to ease managment of your
python virtualenvs. You can add the `export` and `source` lines below to your
`.bashrc` file to avoid running them in every new terminal you open.

	pip install --user virtualenvwrapper
	export WORKON_HOME=~/.virtualenvs  # or whichever dir you prefer
	source ~/.local/bin/virtualenvwrapper.sh
	mkvirtualenv -ppython3 temp3  # or whatever name you prefer
	workon temp3
	cd <folder containing DiffEng setup.py>
	pip install --editable .


In order to run the tests you should install `pytest` in your virtualenv.

	workon temp3
	pip install pytest
	deactivate    # these two steps are necessary if you have py.test
	workon temp3  # installed on the system already
	which py.test  # should point to py.test in your virtualenv
	py.test tests/
