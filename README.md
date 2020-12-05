Setup

1. Download, install and start MongoDB server version: 4.4.1<br>
    https://docs.mongodb.com/manual/administration/install-on-linux/<br>
    https://docs.mongodb.com/manual/tutorial/install-mongodb-on-windows/<br>
    https://docs.mongodb.com/manual/tutorial/install-mongodb-on-os-x/

2. Install venv pip package<br>
    a. On macOS and Linux:<br>
    <pre>python3 -m pip install --user virtualenv</pre><br>
    b. On Windows:<br>
    <pre>py -m pip install --user virtualenv</pre><br>
    https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/

3. Create a virtual env:<br>
    python -m venv ./SuperStore

4. Activate the newly created virtual environment<br>
    .\SuperStore\Scripts\activate
    
5. Install packages from requirements.txt<br>
    pip install -r .\requirements.txt
    
6. Run server:
    python -m flask run
    
Setup for Ubuntu 16.04, Python3.8
To install pip3.8 
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3.8 get-pip.py
To start server using python3.8
sudo /home/ubuntu/SuperStore/SuperStore/bin/python3.8 -m flask run --host 0.0.0.0 --port 90

