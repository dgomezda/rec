#Instalando python
sudo apt-get install build-essential checkinstall
sudo apt-get install libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev
cd /usr/src
wget https://www.python.org/ftp/python/2.7.12/Python-2.7.12.tgz
cd Python-2.7.12
sudo ./configure
sudo make altinstall
python2.7 -V
# instalando pre requisitos 
sudo pip install pydub
sudo apt-get install ffmpeg libavcodec-extra-53
sudo apt-get install python-pyaudio python3-pyaudio
sudo apt-get install python-numpy python-scipy python-matplotlib ipython ipython-notebook python-pandas python-sympy python-nose
sudo apt-get install python-pip python-dev libmysqlclient-dev
pip install MySQL-python
sudo apt-get install mysql-server
