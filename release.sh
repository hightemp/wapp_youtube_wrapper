CFILE=wapp_youtube_wrapper

timestamp=$(date +%s)
VERSION=$(echo `cat VERSION`.$timestamp)

git add .
git commit -am "`date` update"
git tag $VERSION
git push

if [ "$?" != "0" ]; then
    echo "====================================================="
    echo "ERROR"
    echo
    exit 1
fi

cd ..
python3 -m zipapp $CFILE -p "/usr/bin/env python3"
mv $CFILE.pyz ./$CFILE
cd $CFILE

gh release create $VERSION -t $VERSION -n "" 
gh release upload $VERSION ../$CFILE.pyz --clobber

