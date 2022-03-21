# Python FTP server & client
Local FTP server with authentification

python 3.8

Warning: **DO NOT USE IN PRODUCTION**. This server was only developped for educational purposes.

# Dependencies

You need to install [bcrypt](https://pypi.org/project/bcrypt). Using pip :

`pip install bcrypt`

# Usage : 

Server : `python ./ftp.py -h <host> -p 21`

Client : `python ./ftp_client.py <host> 21`

# Screenshots

Server-side :

![server](https://i.imgur.com/HcU3Djt.jpg)

Client-side :

![client](https://i.imgur.com/awGAN7t.png)

