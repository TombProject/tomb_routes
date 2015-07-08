# Before you release
# - Bump version in the `VERSION` file
# - update the package version in the CHANGES file/add any relevant changes
# - send update to devops that new release is coming

PKG_NAME=$(python setup.py --name)
PKG_VERSION=$(cat VERSION)
PKG_FILE=${PKG_NAME}-${PKG_VERSION}.tar.gz
CURL_URL=http://packages/index/${PKG_FILE}
CURRENT_BRANCH=$(git branch|awk -F' ' '{ print $2}')
echo "Checking if ${PKG_NAME}-${PKG_VERSION} already exists..."
curl --silent --head --fail -o /dev/null ${CURL_URL}
if [ $? -eq 0 ]; then
  echo "${PKG_NAME}-${PKG_VERSION} already exists, aborting."
  exit 1
fi

pip install setuptools-git
git tag -am "release ${PKG_VERSION}" ${PKG_VERSION}
git push --tags
git checkout ${PKG_VERSION}
python setup.py sdist upload -r http://packages
git checkout ${CURRENT_BRANCH}
