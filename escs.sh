##############################################################################
# Clone.
cd ~/projects
git clone git@github.com:iogf/untwisted.git untwisted-code
##############################################################################
# Clone untwisted wiki.
cd ~/projects
git clone git@github.com:untwisted/untwisted.wiki.git untwisted.wiki-code
##############################################################################

# Push.
cd ~/projects/untwisted-code
git status
git add *
git commit -a
git push 
##############################################################################
# Create the develop branch.
git branch -a
git checkout -b development
git push --set-upstream origin development
##############################################################################
# Merge master into development.
cd ~/projects/untwisted-code
git checkout development
git merge master
git push
##############################################################################
# Merge development into master.

cd ~/projects/untwisted-code
git checkout master
git merge development
git push
git checkout development
##############################################################################
# Check diffs.

cd ~/projects/untwisted-code
git diff
##############################################################################
# Delete development branch.
git branch -d development
git push origin :development
git fetch -p 
##############################################################################
# Checkout changes.
cd ~/projects/untwisted-code
git checkout *
##############################################################################
# Create TOC.

cd ~/projects/untwisted-code
gh-md-toc BOOK.md > table.md
vy table.md
rm table.md
##############################################################################
# Install untwisted manually.

sudo bash -i
cd /home/tau/projects/untwisted-code
python setup.py install
rm -fr build
exit

##############################################################################
# Remove the package manually.
sudo bash -i
rm -fr /usr/local~/projects/python2.7/dist-packages/untwisted
rm -fr /usr/local~/projects/python2.7/dist-packages/untwisted-*.egg-info
exit
##############################################################################
# Build with disutils.

cd /home/tau/projects/untwisted-code
python setup.py sdist 
rm -fr dist
rm MANIFEST
##############################################################################
# Upload package to pypi.

cd ~/projects/untwisted-code
python setup.py sdist 
twine upload dist/*

##############################################################################
# futurize code.

cd ~/projects/untwisted-code
futurize --stage1 -w **/*.py

# Check changes.
futurize --stage2 **/*.py

# Apply the changes.
futurize --stage2 -w **/*.py

# Clear stuff.
find . -name "*.bak" -exec rm -f {} \;

##############################################################################
# Create a virtualenv for a project.
cd ~/.virtualenvs/
ls -la
# by default #python3 has executable named python in arch linux.
virtualenv untwisted -p /usr/bin/python3.6
##############################################################################
# Activate a virtualenv.
cd ~/.virtualenvs/
source untwisted/bin/activate
cd ~/projects/untwisted-code
##############################################################################
git rm --cached -r build




