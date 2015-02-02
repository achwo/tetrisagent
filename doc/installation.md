# Installation

## Ubuntu 14.10

Voraussetzungen: 

- Evtl: sudo apt-get install libfreetype6-dev python-dev
- sudo apt-get install python-tk python-matplotlib

- hg clone ssh://hg@bitbucket.org/timsn/tetrisagent
- cd tetrisagent

- sudo -H pip install -r requirements.txt --allow-external BitVector --allow-unverified BitVector


## Mac OSX

Voraussetzungen: python, mercurial

- hg clone ssh://hg@bitbucket.org/timsn/tetrisagent
- cd tetrisagent
- sudo easy_install pip (might be unnecessary depending on python installation)
- sudo -H pip install -r requirements_osx.txt --allow-external BitVector --allow-unverified BitVector

## Anmerkung
Wir wollen eigentlich ein Docker file verwenden, um die Installation zu erleichtern.
