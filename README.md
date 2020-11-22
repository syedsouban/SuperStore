#Setup
0. Download, install and start MongoDB server version: 4.4.1
    https://docs.mongodb.com/manual/administration/install-on-linux/
    https://docs.mongodb.com/manual/tutorial/install-mongodb-on-windows/
    https://docs.mongodb.com/manual/tutorial/install-mongodb-on-os-x/

1. Install venv pip package
On macOS and Linux:
    python3 -m pip install --user virtualenv
On Windows:
    py -m pip install --user virtualenv
    https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/

2. Create a virtual env:
    python -m venv ./SuperStore

3. Activate the newly created virtual environment
    .\SuperStore\Scripts\activate
    
4. Install packages from requirements.txt
    pip install -r .\requirements.txt
