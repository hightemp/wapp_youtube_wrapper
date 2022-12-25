CFILE=wapp_youtube_wrapper.pyz

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
python3 -m zipapp wapp_youtube_wrapper -p "/usr/bin/env python3"
mv wapp_youtube_wrapper.pyz ./wapp_youtube_wrapper
cd wapp_youtube_wrapper

echo gh release create $VERSION -t $VERSION -n '""' $CFILE
gh release create $VERSION -t $VERSION -n "" $CFILE
