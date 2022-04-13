python client.py member --name thermo --type pub --src 192.168.33.12
python client.py member --name heater --type sub --src 192.168.33.13
python client.py member --name C --type broker --src 192.168.33.11
python client.py relation --pub thermo --sub heater --broker C --subject test

python client.py member --name heater --type pub --src 192.168.33.13
python client.py member --name thermo --type sub --src 192.168.33.12
python client.py relation --pub heater --sub thermo --broker C --subject test