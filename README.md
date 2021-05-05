# CAD_Spring2021
## Final Project for Computer-Aided Design for Digital Circuits Class (Automated ILP)

Summary: This project works on automating ILP Formulations by using a custom graph design (see dfg.py) to create and extract the multiple paths a given Data Flow Graph has. It then produces an ILP file and runs it through the GLPK library.

## Running:
Run this in command line or terminal:

python3 auto_schedule.py -l=[LATENCY] -a=[AREA] -g=[FILENAME]
	where LATENCY and AREA is a number, and FILENAME is the file of the Data Flow Graph in edgelist formatting

Note: If the 'python3' command doesn't work, try running it using the 'python' command

## Installation Instructions:
This copy contains the GLPK package. If for any reason the GLPK package is deleted, please follow these instructions:

### Installing GLPK:
1) Download http://ftp.gnu.org/gnu/glpk/glpk-4.35.tar.gz
2) Unzip glpk-4.35.tar.gz in src/glpk folder
3) Open src/glpk/glpk-4.35 folder in command line and install build essentials
		ex: 'sudo apt-get install build-essential' (or equivalent)
4) type './configure' in command line in 'glpk-4.35' folder
5) type 'make' in command line

At this point the GLPK package should be installed successfully, and you can run the auto_schedule.py file



