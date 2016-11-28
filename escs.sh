##############################################################################
# clone, untwisted, github.
cd ~/projects
git clone git@github.com:iogf/untwisted.git untwisted-code
##############################################################################
# push, untwisted, github.
cd ~/projects/untwisted-code
git status
git add *
git commit -a
git push 
##############################################################################
# create the develop branch, untwisted.
git branch -a
git checkout -b development
git push --set-upstream origin development
##############################################################################
# merge master into development, untwisted.
cd ~/projects/untwisted-code
git checkout development
git merge master
git push
##############################################################################
# merge development into master, untwisted.
cd ~/projects/untwisted-code
git checkout master
git merge development
git push
git checkout development
##############################################################################
# check diffs, untwisted.
cd ~/projects/untwisted-code
git diff
##############################################################################
# delete the development branch, untwisted.
git branch -d development
git push origin :development
git fetch -p 
##############################################################################
# undo, changes, untwisted, github.
cd ~/projects/untwisted-code
git checkout *
##############################################################################
# create, a new branch locally from an existing commit, from, master.
git checkout master
cd ~/projects/untwisted-code
git checkout -b old_version fcebcd4f229cb29cac344161937d249785bf83f8
git push --set-upstream origin old_version

git checkout old_version
##############################################################################
# delete, old version, untwisted.
git checkout master
git branch -d old_version
git push origin :old_version
git fetch -p 
##############################################################################
# create, toc, table of contents, untwisted.
cd ~/projects/untwisted-code
gh-md-toc BOOK.md > table.md
vy table.md
rm table.md
##############################################################################
# install, untwisted.
sudo bash -i
cd /home/tau/projects/untwisted-code
python2 setup.py install
rm -fr build
exit
##############################################################################
# remove, uninstall, global, delete, untwisted.
sudo bash -i
rm -fr /usr/local~/projects/python2.7/dist-packages/untwisted
rm -fr /usr/local~/projects/python2.7/dist-packages/untwisted-*.egg-info
exit
##############################################################################
# build, untwisted, package, disutils.
cd /home/tau/projects/untwisted-code
python2.6 setup.py sdist 
rm -fr dist
rm MANIFEST
##############################################################################
# share, put, place, host, package, python, pip, application, untwisted.

cd ~/projects/untwisted-code
python2 setup.py sdist register upload
rm -fr dist
##############################################################################

