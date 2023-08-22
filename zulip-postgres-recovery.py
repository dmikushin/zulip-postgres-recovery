#!/usr/bin/env python3
import os
import re
import signal
import subprocess
import socket
import time

def build_postgres():
	if os.path.exists('ThirdParty/postgres-tolerant/install/bin/postgres'):
		print('postgres is already built, skipping...')
		return

	cmd_debug = """
	bash -c "cd ThirdParty/postgres-tolerant && \
	mkdir -p build && cd build && \
	CFLAGS='-O0' ../configure --enable-debug --prefix=\$(pwd)/../install --with-lz4 && \
	make -j12 && make install"
	"""

	cmd_release = """
	bash -c "cd ThirdParty/postgres-tolerant && \
	mkdir -p build && cd build && \
	CFLAGS='-O3 -march=native -fomit-frame-pointer' ../configure --prefix=\$(pwd)/../install --with-lz4 && \
	make -j12 && make install"
	"""
	
	cmd = cmd_release.strip()
	print(cmd)
	if os.system(cmd) != 0:
		raise Exception(f'postgres compilation has failed, aborting')

if __name__ == "__main__":
	build_postgres()
   
	print('Removing old databases extractions...')
	os.system('rm -rf data_src')
	os.system('rm -rf data_dst')

	print('Extracting databases...')
	os.system('mkdir data_src && cd data_src && tar -xf ../data_src.tar.gz')
	os.system('mkdir data_dst && cd data_dst && tar -xf ../data_dst.tar.gz')

	port_src = 5432
	port_dst = 5433

	print(f'Launching postgres src and dst on ports {port_src} and {port_dst}...')
	cmd_src = f'ThirdParty/postgres-tolerant/install/bin/postgres -p {port_src} -O -P -D data_src/data/ -c log_error_verbosity=verbose'
	cmd_dst = f'ThirdParty/postgres-tolerant/install/bin/postgres -p {port_dst} -O -P -D data_dst/data/ -c log_error_verbosity=verbose'
	print(cmd_src)
	print(cmd_dst)
	
	# The os.setsid() is passed in the argument preexec_fn so
	# it's run after the fork() and before  exec() to run the shell.
	proc_src = subprocess.Popen(cmd_src, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
	proc_dst = subprocess.Popen(cmd_dst, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)

	try:
		# TODO Wait until "database system is ready to accept connections" in the logs
		time.sleep(10)

		tables = [ "zerver_recipient", "zerver_userprofile", "zerver_stream", "fts_update_log", "zerver_message", "zerver_submessage", "zerver_usermessage", "zerver_userstatus", "zerver_usertopic", "zerver_reaction", "zerver_attachment", "zerver_attachment_messages" ]

		filename = "zulip.sql"
		filename1 = "zulip.sql.1"

		# TODO Perform export and import for each table
		for table in tables:
			print(f'Processing table {table}...')
			
			# Export from source database
			cmd = f'ThirdParty/postgres-tolerant/install/bin/pg_dump -p {port_src} --column-inserts --data-only --table={table} -U zulip zulip >{filename1}'
			#print(cmd)
			if os.system(cmd) != 0:
				raise Exception(f'Cannot dump table {table} from the source database, aborting')

			file1 = open(filename1, 'r')
			file = open(filename, 'w')

			while True:
				# Get next line from file
				line = file1.readline()
			 
				if not line:
					break

				# Change INSERT to "INSERT IF NOT EXISTS"
				if re.match('^INSERT.*', line):
					line = re.sub('\);$', ') ON CONFLICT DO NOTHING;', line)

				#print(line)
				file.write(line) 

			file1.close()
			file.close()

			# Import to destination database
			cmd = f'ThirdParty/postgres-tolerant/install/bin/psql -p {port_dst} -U zulip -d zulip --file {filename}'
			#print(cmd)
			if os.system(cmd) != 0:
				raise Exception(f'Cannot insert table {table} rows to the dest database, aborting')
	except Exception as e:
		raise e
	finally:
		# Stop databases (send the signal to all the process groups)
		os.killpg(os.getpgid(proc_src.pid), signal.SIGTERM)
		os.killpg(os.getpgid(proc_dst.pid), signal.SIGTERM)

