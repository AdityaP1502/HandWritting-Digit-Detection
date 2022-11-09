# HandWritting-Digit-Detection
Detect handwritten digit from images using scikit-learn. This is a final project for ET3107 "Pemrograman Lanjut" Course. 

# Installation
__NOTES__: This program currently only support Ubuntu. For windows, installation can be done using wsl. 

First update your python3 version into 3.10
```shell
sudo add-apt-repository ppa:deadsnakes/ppa &&
sudo apt update &&
sudo apt install python3.10 && 
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 2 &&
sudo update-alternatives --config python3 &&
```

Check your python3 version:
```shell
python3 --version
```

Then install all python modules that are used by running commands below
```shell
pip3 install -r requirements.txt
```

To run this project, you first must build all the neccessary C library. We write some function in C to sped up few process in the detection. 

Before running the build scripts, grant permission first by running this command:

```shell
chmod +x scripts/build.sh && chmod +x scripts/buildTest.sh
```
Then run this command to build all libs:
```shell
./scripts/build.sh
```
