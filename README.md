# HandWritting-Digit-Detection
Detect handwritten digit from images using scikit-learn. This is a final project for ET3107 "Pemrograman Lanjut" Course. 

# Installation
__NOTES__: This program currently only support Ubuntu. For windows, installation can be done using wsl. 
Clone this repository
```shell
git clone https://github.com/AdityaP1502/HandWritting-Digit-Detection
cd HandWritting-Digit-Detection
```
First, install virtual environment and create a new virtual environment on python

```shell
python3 -m pip install --user virtualenv &&
sudo apt install python3-venv &&
python3 -m venv env
```

then, activate the virtual environment by running
```shell
source env/bin/activate
```

then, grant permission to install.sh scripts by running command below
```shell
chmod +x ./scripts/install.sh
```

then, to install just run the scripts
```shell
./scripts/install.sh
```
### Notes:
For windows user running in wsl, if found error
```shell
./scripts/build.sh: line 3: $'\r': command not found
./scripts/build.sh: line 69: syntax error: unexpected end of file
```
Change the EOL from CRLF(windows) TO LF(LINUX). You can use notepad++ EOL conversion for this. Then run the script again. 

# Run
To start detecting images, run this in root folder. (__windows__ user must run this via wsl)
```shell
python3 start.py -f [filename]
```

If you want to detect images in batch (highly recommended if you have multiple images that want to be detected), add -b option
```shell
python3 start.py -b --img_path="/home/img/"
```

