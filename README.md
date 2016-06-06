**************************************************

TFTP Client

**************************************************

author: Ólafur Aron Jóhannsson<br>
email: olafur@johannsson.co<br>
website: http://olafurjohannsson.com<br>

Description:

Scripts and GUI that implements að client that Reads/Write's using the Tftp (Trivial File Transfer Protocol) desctribed in RFC 1350.

tftp_cmd.py is a command line script requires at least three arguments host, command and filename. It also has two optional arguments, port and alt_name.

tftp_cmd2.py is a command line script that implements the same features, but instead of command line arguments it promts user for input.

tftp_gui.py is a gui version of the client. It can be initalized from the command line or by double clicking the tftp_gui.py file.


**************************************************

usage: tftp_cmd.py [-h] [-p PORT] [-a ALT_NAME] host command file_name

tftp_cmd.py tftp.example.com writes sample.txt
	# Writes the file sample.txt to tftp.example.com

tftp_cmd.py tftp.example.com skrifar sample.txt -p 102 -a skra.txt 
	# Writes the file sample.txt to tftp.example.com on port 102 as skra.txt

tftp_cmd.py tftp.example.com reads sample.txt
	# Reads the file sample.txt from tftp.example.com

tftp_cmd.py tftp.example.com lesa sample.txt -p 102 -a skra.txt 
	# Reads the file sample.txt from tftp.example.com on port 102 as skra.txt


**************************************************

Arguments:

positional arguments:

  host                  the host to connect to

  command               enter command: read, write or quit

  file_name             name of the file to read/write

optional arguments:

  -h, --help            show this help message and exit

  -p PORT, --port PORT  use specific port

  -a ALT_NAME, --alt_name ALT_NAME
                        read/write with an alternate name



**************************************************

Packages:
	tftp.py # module that handles tftp packets, logging and testing
	tftp_client.py # module that interacts with a tftp server.
	tftp_cmd.py # module that takes in command line args and uses tftp_client.py
	tftp_cmd2.py # module that takes input from a user and uses tftp_client.py
	tftp_gui.py # module that loads a gui version of the client
	
		
**************************************************
