Overview
========
SDX API

Kytos Napp to handle the requirements of the AtlanticWave-SDX project.

Requirements
============

* Debian 10
* mongodb
* docker
* openAPI Specification
* swagger client
* flask
* python 3.9
* python3-pip
* python3-ven
* kytos/core
* kytos/topology
* curl
* mininet

Preparing the environment:
==========================

``Installing Python, Docker and Mongodb``

* If you don't have Python 3 installed, please install it. Please make sure that you're using python3.9

* 1.- Python, Pip, Virtual Env, Mongodb, Docker and dependencies for Debian 10 

* Download and Run:

https://github.com/atlanticwave-sdx/kytos-sdx-topology/blob/main/envsetup/install/0_envsetup.sh

$ ./0_envsetup.sh

``Installing Kytos Virtual env``

* 2.- Virtual environment and Kytos

* Download and Run:

https://github.com/atlanticwave-sdx/kytos-sdx-topology/blob/main/envsetup/install/1_kytosdir.sh

$ ./1_kytosdir.sh

* Download and run inside /kytos directory:

https://github.com/atlanticwave-sdx/kytos-sdx-topology/blob/main/envsetup/install/2_venvinstall.sh

$ cd /kytos

$ ./2_venvinstall.sh

``Activate environment and install python dependencies``

* 3.- Python dependencies

$ cd /kytos

$ source venv-python3.9/bin/activate

* Download and run after the environment is activated

https://github.com/atlanticwave-sdx/kytos-sdx-topology/blob/main/envsetup/install/3_pipinstall.sh

(venv-python3.9) ./3_pipinstall.sh

``Clone Kytos``

* 4.- kytos python-openflow kytos-utils flow_manager mef_eline of_core of_lldp pathfinder storehouse topology and sdx_topology

* Download and run inside /kytos directory:

https://github.com/atlanticwave-sdx/kytos-sdx-topology/blob/main/envsetup/install/4_clone_kytos.sh

(venv-python3.9) cd /kytos

(venv-python3.9) ./4_clone_kytos.sh

``Installing Kytos``

5.- kytos and napps setup

* Download and run inside /kytos directory:

https://github.com/atlanticwave-sdx/kytos-sdx-topology/blob/main/envsetup/install/5_install_kytos.sh 

(venv-python3.9) ./5_install_kytos.sh

``Install Docker mongodb container``

* Download and Run:

https://github.com/atlanticwave-sdx/kytos-sdx-topology/blob/main/envsetup/install/6_add-etc-hosts.sh

(venv-python3.9) cd /kytos/sdx_topology/envsetup/install

(venv-python3.9) ./6_add-etc-hosts.sh

* After add hosts, restart the network interface or the host

* Inside /kytos/kytos run docker-compose

(venv-python3.9) cd /kytos/kytos

(venv-python3.9) docker-compose up -d

* Download and Run:

https://github.com/atlanticwave-sdx/kytos-sdx-topology/blob/main/envsetup/install/7_rs-init.sh

(venv-python3.9) cd /kytos/sdx_topology/envsetup/install

(venv-python3.9) ./7_rs-init.sh

``run Kytos``

(venv-python3.9) kytosd -f --database mongodb

``run Mock provisioning``

* In another terminal start the flask app to Mock Provisioning listening

https://github.com/atlanticwave-sdx/kytos-sdx-topology/blob/main/envsetup/sdx_lc_mock/flaskrun.sh

* This will be listening on the endpoint: 

* http://0.0.0.0:8088/SDX-LC/1.0.0/provision

Installing swagger_client
==========================

For the whole installation process and requirements, please access
the AtlanticWave SDX repo in Github: https://github.com/atlanticwave-sdx

How to Use
==========

TBD


Version
=======

1.0.0

# Test

// Install python dependecies requirements

# Asynchronous Lint Engine

// ALE (Asynchronous Lint Engine) is a plugin providing linting (syntax checking and semantic errors)

// Installation in VIM with Vundle

cd ~/.vim/bundle

Set up Vundle:

git clone https://github.com/VundleVim/Vundle.vim.git ~/.vim/bundle/Vundle.vim

git clone https://github.com/dense-analysis/ale.git

// Edit ~/.vimrc

set rtp+=~/.vim/bundle/Vundle.vim

let path='~/.vim/bundle/Vundle.vim'

call vundle#begin()

Plugin 'VundleVim/Vundle.vim'

Plugin 'dense-analysis/ale'

call vundle#end()            " required

filetype plugin indent on    " required

let g:ale_linters = {
        \   'python': ['flake8', 'pylint', 'pycodestyle'],
        \}


// Then run the command :PlugInstall in Vim.

:source ~/.vimrc
:PluginInstall

# Black

black --check --diff main.py

black main.py
black --line-length 80 main.py

# Isort

isort main.py

# Bandit

bandit --configfile bandit.yaml

// with the following bandit.yaml in the project's root directory

assert_used:
  skips: ['*_test.py', 'test_*.py']


# How to update dependencies versions

// Edit requirements.in/dev.txt if needed.

// Run pip-compile again, exactly as before:

$ <venv>/bin/pip-compile dev.in

# Pytest

python3 -m pytest --cov=app --cov-report=html

# Partial test

pytest -v -k "test_sdx_topology"

# Unit test

pytest tests/unit/test_main.py

pytest --cov app --cov-branch --cov-report term-missing
