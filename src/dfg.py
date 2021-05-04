#
# Author: Rachel Berghout
# DFG classes and functions to be used by auto_schedule.py
# Class Structure based on these websites:
#	https://docs.python.org/3/tutorial/classes.html
#	https://www.geeksforgeeks.org/linked-list-set-1-introduction/
# To Include: include dfg
#

# ---------------------------------------------------
# Class Node
# ---------------------------------------------------
class Node:
	def __init__(self, nodeNum):
		self.number = int(nodeNum)
		self.segments = []
		self.parents = []

# ---------------------------------------------------
# Class Segment
# ---------------------------------------------------
class Segment:
	def __init__(self, weight):
		self.weight = weight
		self.child = None
		
# ---------------------------------------------------
# Class Graph
# ---------------------------------------------------
class DFG:
	def __init__(self):
		self.head = Node(-1)
		
# -------------------------------------------------------------
# Reads in a Data Flow Graph (DFG) that is in Edge-List Format
# -------------------------------------------------------------
def ReadDFG(filename):
	if(".edgelist" not in filename):
		print("ERROR: Cannot accept files without the \".edgelist\" extension")
		return None
		
	try:
		rFile = open(filename, "r")
		data = rFile.read()
		rFile.close()
	except FileNotFoundError:
		print("ERROR: \"" + filename + "\" does not exist")
		return None
	except:
		print("Error: Cannot read file\n")
		return None
		
	return createDFG(data.split("\n"))
	
	
# ---------------------------------------------------
# Create a Data Flow Graph (DFG) using linked lists
# ---------------------------------------------------
def createDFG(dfgList):
	myDfg = DFG()
	for line in dfgList:
		if(line == ""):
			continue
		
		data = line.split(" ")
		
		#Create Parent node
		#Does parent node exist?
		resultp = CheckNode(myDfg.head, int(data[0]))
		if(resultp[0] == False):
			#create first Node and link it to head
			numSegs = len(myDfg.head.segments)
			myDfg.head.segments.append(Segment(0)) #no weight on segments between head and node
			myDfg.head.segments[numSegs].child = Node(data[0])
			myDfg.head.segments[numSegs].child.parents.append(myDfg.head)
			
			#change current node
			curNode = myDfg.head.segments[numSegs].child
		else:
			curNode = resultp[1]
		
		#Create Segments and Attach Child Node to Parent
		numSegs = len(curNode.segments)
		curNode.segments.append(Segment(data[2]))
		#Does child node exist?
		resultc = CheckNode(myDfg.head, int(data[1]))
		if(resultc[0] == False):
			curNode.segments[numSegs].child = Node(data[1])
		else:
			curNode.segments[numSegs].child = resultc[1]
			
		curNode.segments[numSegs].child.parents.append(curNode)
	return myDfg
	
# ---------------------------------------------------
# Search through the DFG for a specific node
# ---------------------------------------------------
def CheckNode(curNode, data):
	if(curNode != None):
		if(curNode.number == data):
			return [True, curNode]
	
		result = [False, None]
		for s in curNode.segments:
			result = CheckNode(s.child, data)
			if(result[0] == True):
				return [True, result[1]]
	
	return [False, None]
	
# ---------------------------------------------------
# Print DFG by connections
# ---------------------------------------------------
def PrintDFG(thisDfg):
	#print("Nodes = ()\nWeights = []\nPaths:\n-------------")
	ScanNodes(thisDfg.head, "")
	
		
# ---------------------------------------------------
# Scan the DFG and print the path to the last node
# ---------------------------------------------------
def ScanNodes(curNode, path):
	path += "("+str(curNode.number)+")"
	if(len(curNode.segments) == 0):
		print(path[10:]) # skip the head node which isn't part of the graph
		return path
	else:
		path += "-"
		
	segWeight = ""
	for s in curNode.segments:
		segWeight = "[" + str(s.weight) + "]->"
		ScanNodes(s.child, path + segWeight)

# ---------------------------------------------------
# Scan the DFG and return the path to the last node
# format: a list of formatting options
#		Type: "nodes", "weights", "both"
#		Symbols: True, False
# ---------------------------------------------------
def ScanForPaths(curNode, head, paths, curPath, options):
	symbols = True
	if("Symbols False" in options["format"]):
		symbols = False
		
	if("both" in options["format"] or "nodes" in options["format"]):
		curPath += "("+str(curNode.number)+")" if symbols else str(curNode.number)
		
	# Return Case:
	if(len(curNode.segments) == 0):
		if("both" in options["format"] or "weights" in options["format"]):
			curPath += "-[0]-"+str(options["sum"]) if symbols else "-0-" + str(options["sum"])
		# Add the path to the list of paths, skip the head node which isn't part of the graph
		if(type == "both"):
			paths.append(curPath[12:])
		else:
			paths.append(curPath[8:])
		return None
	else:
		curPath += "-"
			
	segWeight = ""
	for s in curNode.segments:
		# Increase the sum to have a running total of the weights of a given path
		options["sum"] += int(s.weight)
		
		# Add the weights and running total to the output path
		if("both" in options["format"] or "weights" in options["format"]):
			segWeight = "[" + str(s.weight) + "]-"+str(options["sum"])+"->" if symbols else str(s.weight) + "-"+str(options["sum"])+"->"
		else:
			segWeight = "-"+str(options["sum"])+"->"
		ScanForPaths(s.child, head, paths, curPath + segWeight, options)
		
		# Reset sum to previous case
		options["sum"] -= int(s.weight)
	return paths
		
# ---------------------------------------------------
# Scan the DFG and return the path to the last node
# type = only "nodes", "weights", "both"
# ---------------------------------------------------
def GetPaths(thisDfg, optionsDict):
	paths = []
	return ScanForPaths(thisDfg.head, thisDfg.head, paths, "", optionsDict)
	
# -----------------------------------------------------
# Scan the DFG and return a list of all nodes in graph
# -----------------------------------------------------
def GetNodes(thisDfg):
	nodes = []
	return ScanForNodes(thisDfg.head, nodes)	
	
# -----------------------------------------------------
# Scan the DFG and return a list of all nodes in graph
# -----------------------------------------------------
def ScanForNodes(curNode, nodes):
	if curNode.number not in nodes:
		nodes.append(curNode.number)
	if(len(curNode.segments) == 0):
		return None
		
	for s in curNode.segments:
		ScanForNodes(s.child, nodes)
		
	return nodes	
		
		
		
		