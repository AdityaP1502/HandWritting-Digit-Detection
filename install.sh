MODEL_NAME="model.tar"
MODEL_ID=1-VnALakyh-OysIe0lSDW8fIlQg0XKnxz
FILE=$PWD/$MODEL_NAME
echo $FILE

echo "Installing dependencies"
pip3 install -r requirements.txt
chmod +x scripts/build.sh && chmod +x scripts/buildTest.sh
./scripts/build.sh

echo "Checking model files"
if [ -f "$FILE" ]; then
    sha256sum -c MODEL_SHA256
    if [  $?  ]; then
        echo "File is corrupted, redownload model files"
        rm -rf $MODEL_NAME
        wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=$MODEL_ID' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=$MODEL_ID" -O $MODEL_NAME && rm -rf /tmp/cookies.txt
    fi

else 
    echo "$FILE does not exist."
    echo "Downloading model files"
    wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=$MODEL_ID' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=$MODEL_ID" -O $MODEL_NAME && rm -rf /tmp/cookies.txt
fi
tar -xvf $MODEL_NAME  && rm -rf $MODEL_NAME

if [ ! $? ]; then
    echo "Installation Succesful"
else
    echo "Installation failed"
fi

