# Before you release
# - Bump version in the `VERSION` file
# - update the package version in the CHANGES file/add any relevant changes
# - send update to devops that new release is coming

PKG_NAME=$(python setup.py --name)
PKG_VERSION=$(cat VERSION)
PKG_FILE=${PKG_NAME}-${PKG_VERSION}.tar.gz
CURRENT_BRANCH=$(git branch|awk -F' ' '{ print $2}')

pip install setuptools-git
git tag -am "release ${PKG_VERSION}" ${PKG_VERSION}
git push --tags
git checkout ${PKG_VERSION}
python setup.py sdist upload
git checkout ${CURRENT_BRANCH}
