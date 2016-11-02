#Instalando python
sudo apt-get update
sudo apt-get install build-essential checkinstall
sudo apt-get install libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev
cd /usr/src
sudo wget https://www.python.org/ftp/python/2.7.12/Python-2.7.12.tgz
sudo tar xzf Python-2.7.12.tgz
cd Python-2.7.12
sudo ./configure
sudo make altinstall
python2.7 -V
#instalando python pip
sudo apt-get install python-pip python-dev build-essential 
sudo pip install --upgrade pip 
# instalando pre requisitos 
sudo pip install pydub
sudo apt-get install ffmpeg
sudo apt-get install python-pyaudio python3-pyaudio
sudo apt-get install python-numpy python-scipy python-matplotlib ipython ipython-notebook python-pandas python-sympy python-nose
#mysql server
sudo apt-get update
sudo apt-get install mysql-server
#mysql client
sudo apt-get install python-dev
sudo apt-get install python-MySQLdb
sudo apt-get install libmysqlclient-dev
sudo pip install MySQL-python
#libraries
sudo pip install dicttoxml

#create database
#SHOW GLOBAL VARIABLES LIKE 'PORT';
#mysql --user root -password
#toor
#create database ironrec