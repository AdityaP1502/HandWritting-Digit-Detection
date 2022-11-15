# HandWritting-Digit-Detection
Detect handwritten digit from images using scikit-learn. This is a final project for ET3107 "Pemrograman Lanjut" Course. 

# Installation
__NOTES__: This program currently only support Ubuntu. For windows, installation can be done using wsl. 

Install and creating virtual environment
__WINDOWS__
```shell
py -m pip install --user virtualenv
py -m venv env
.\env\Scripts\activate
```

__LINUX__
```shell
python3 -m pip install --user virtualenv &&
python3 -m venv env && 
source env/bin/activate
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
