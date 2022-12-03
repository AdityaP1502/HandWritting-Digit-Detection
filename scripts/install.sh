MODEL_NAME="model.tar.gz"
MODEL_ID=1_A4C8A0qJ8WKMdtvHI5J-Hqc_6PXRmH4
FILE=$PWD/$MODEL_NAME
echo $FILE

echo "Installing dependencies"
pip3 install -r requirements.txt --compile
chmod +x scripts/build.sh && chmod +x scripts/buildTest.sh
./scripts/build.sh

echo "Checking model files"
if [ -f "$FILE" ]; then
    sha256sum -c MODEL_SHA256SUMS
    if [ ! $? -eq 0  ]; then
        echo "File is corrupted, redownload model files"
        rm -rf $MODEL_NAME
        wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=$MODEL_ID' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=$MODEL_ID" -O $MODEL_NAME && rm -rf /tmp/cookies.txt
    fi

else 
    echo "$FILE does not exist."
    echo "Downloading model files"
    wget --load-cookies $PWD/tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies $PWD/tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=$MODEL_ID' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=$MODEL_ID" -O $MODEL_NAME && rm -rf $PWD/tmp/cookies.txt
    sha256sum -c MODEL_SHA256SUMS
    if [ $? ]; then
        exit 1
    fi
fi
tar -xvf $MODEL_NAME && rm -rf $MODEL_NAME
if [ $? -eq 0 ]; then
    echo "Installation Succesful"
else
    echo "Installation failed"
fi
