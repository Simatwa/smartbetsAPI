apt-get install python3
python3 setup.py install
if [[ -d "/data/data/com.termux/files/usr/bin" ]]; then
   echo 'Installing Termux-API'
   pkg install termux-api
fi
echo 'Installed successfully!'
smartbetsAPI -v