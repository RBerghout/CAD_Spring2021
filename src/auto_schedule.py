#
# Author: Rachel Berghout
# Functionality:
#	1) Minimize Memory (area) under Latency
#	2) Minimize Latency under Memory (area)
#	3) Perform Memory-Latency Pareto-optimal analysis
#

import sys
import dfg
import ilp

# -------------------------------------
# Prints out the usage of the program
# -------------------------------------
def PrintUsage():
	print("Usage: python3 auto_schedule.py -l=[LATENCY] -a=[AREA] -g=[FILENAME]")
	print("\n	LATENCY >= 1\n	AREA >= 1\n	FILENAME = A DFG Graph in edge-list format")
	
# Main Function
# Read Input
if(len(sys.argv) < 4):
	print("ERROR: Not enough arguments!\n")
	PrintUsage()
	exit()

latency = -1
area = -1
dfgFile = ""

for i in range(1,4):
	if("-l=" in sys.argv[i]):
		latency = int(sys.argv[i][3:])
	elif("-a=" in sys.argv[i]):
		area = int(sys.argv[i][3:])
	elif("-g=" in sys.argv[i]):
		dfgFile = sys.argv[i][3:]


if(latency == -1):
	print("ERROR: Latency unspecified!\n")
	PrintUsage()
	exit()
if(area == -1):
	print("ERROR: Area unspecified!\n")
	PrintUsage()
	exit()
if(dfgFile == ""):
	print("ERROR: DFG File unspecified!\n")
	PrintUsage()
	exit()

# Preprocess Graph:
dfgGraph = dfg.ReadDFG(dfgFile)
if(dfgGraph == None):
	exit()	

# Generate ILP Formulations
ilpUnsimplifiedFile = ilp.GenILP(area, latency, dfgGraph)
ilpFile = ilp.SimplifyILP(area, latency, ilpUnsimplifiedFile)

# Print Graph:

