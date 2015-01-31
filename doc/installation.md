# Installation

## Mac OSX
Schritte:
1. brew install python
2. brew install hg
3. hg clone ssh://hg@bitbucket.org/timsn/tetrisagent
4. cd tetrisagent
5. sudo easy_install pip (might be unnecessary depending on python installation)
6. sudo pip install -r requirements.txt --allow-external BitVector --allow-unverified BitVector

## Anmerkung
Wir wollen eigentlich ein Docker file verwenden, um die Installation zu erleichtern.