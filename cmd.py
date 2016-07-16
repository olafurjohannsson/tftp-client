import argparse
from tftp_client import TFTPClient
from socket import gethostname, gethostbyname
import os


def main():
	try:
		args, buffer, addr = parser.parse_args(), [], (gethostbyname(gethostname()), gethostname()), 

		(host, port, cmd, file_name, alt_name) = args.host, args.port, args.command.lower(), args.file_name, args.alt_name
		
		c = TFTPClient(host, port)

		if c:
			buffer.append('Connecting from host: {0} to host: {1}:{2}, mode: {3}'.format(addr, host, port, 'octet'))

			for p in range(len(buffer)):
				print(buffer.pop())
		else:
			print('Could not create TFTPClient() with: {0}:{1}'.format(host, port))


		if not alt_name:
			alt_name = file_name

		if cmd in ['lesa','l','read','r']:
			if c.read(file_name, alt_name):

				if '.' in os.path.splitext(file_name)[-1]:
					if os.path.isfile(file_name):
						buffer.append('Successfully read file {0} from server {1}:{2} to path {3}/{4}'.format(file_name, host, port, os.getcwd(), alt_name))

		elif cmd in ['skrifa', 's', 'write', 'w']:
			if not os.path.isfile(file_name):
				raise Exception('File %s does not exist!' % file_name)
			else:
				if c.write(file_name, alt_name):
					buffer.append('Successfully wrote file {0} from path {1} to server {2}:{3}/{4}'.format(file_name, os.getcwd(), host, port, alt_name))

			for i in range(len(buffer)):
				print(buffer.pop())


	except Exception as err:
		print('main.err: %s' % err)

	finally:
		print('Leaving. . .')



if __name__ == '__main__':	
	parser = argparse.ArgumentParser(description='a simple TFTP client')
	parser.add_argument('host', help='the host to connect to')
	parser.add_argument('command', help='enter command: read, write or quit')
	parser.add_argument('file_name', help='name of the file to read/write')
	parser.add_argument('-p', '--port', default=69, help='use specific port')
	parser.add_argument('-a', '--alt_name', help='read/write with an alternate name')
	main()
