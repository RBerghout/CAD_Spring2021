#
# Author: Rachel Berghout
# ILP classes and functions to be used by auto_schedule.py
# To Include: include ilp
#

import os
import dfg

# ---------------------------------------------------
# Generate an Integer Linear Program (ILP) 
#	based on the area, latency, and data flow graph
# ---------------------------------------------------
def GenILP(a, l, dfgIn):
	# Get All Paths from dfg
	nodePaths = dfg.GetPaths(dfgIn, {"format":["both", "Symbols False"], "sum":0})

	# Parse Data, save data to nodePathInfo, calculate longest cycle
	numCycles = []
	nodePathInfo = []
	for p in nodePaths:
		nodes = p.split("->")
		numPath = len(numCycles)
		numCycles.append(0)
		nodePathInfo.append([])
		for n in nodes:
			# Count cycles (weights)
			info = n.split("-")
			if len(info) > 1:
				numCycles[numPath] += int(info[1])
			nodePathInfo[numPath].append(info)
				
	maxCycles = max(numCycles)
	maxIdx = numCycles.index(maxCycles) # Rigid path, doesn't include repeats
		
	critPaths = []
	i=0
	for c in numCycles:
		if(c == maxCycles):
			critPaths.append(nodePathInfo[i])
		i+=1
 	
 	# Get Constraint Criteria
	cDict = CalculateConstraintCriteria(nodePaths, nodePathInfo, maxCycles, maxIdx, critPaths)

 	# Check Feasibility
	# Pull out all nodes with parent == -1
	feasible = []
	for i in cDict:
		p = SearchListOfList(i["parents"], 0, -1)
		if(p > -1):
			if(len(i["cycles"]) > 1):
				feasible.append("maybe")
			if(len(i["cycles"]) == 1):
				feasible.append("yes") # this line is probably part of the critical path

	if("yes" not in feasible):
		print("No Feasible Solution")
		exit()
	
	#get Execution Constraints and constraint node names
	[ec, cn] = CalcExecutionConstraints(cDict)
	#for i in ec: print(i)
		
	# Get Dependency Constraints
	dc = CalcDependencyConstraints(cDict)
	
	# Get Resource Constraints and function constraint list
	[rc, functionList] = CalcResourceConstraints(cDict, maxCycles, a)

	# Organize Resource constraints to have all variables on one side
	ndc = OrganizeEquations(dc)
	
	# Organize function	
	function = ""
	for i in range(len(functionList)): 
		function += functionList[i]
		if(i < len(functionList)-1):
			function += "+"

	# Print info to file (temp file?) or save as string
	fileName = SaveILP(cn, ec, ndc, rc, function)
		
	return fileName
#---------------------------------
# Calculate Constraint Criteria
#---------------------------------
def CalculateConstraintCriteria(nodePaths, nodePathInfo, maxCycles, maxIdx, critPaths):
	# Dict: { Node_Num = "", Cycles = [], Critical_Path = T/F, CyclesBelow = #,
	#		  Weight = #, Parents = [], Distance = # }
	criteriaDict = [] # list of execution constraints info (list of dictionaries)
	
	#Add cycle info to buckets
	dictIdx = -1
	for path in nodePathInfo:
		curCycle = 0
		curNodeLevel = 0
		for node in path:
			#if node doesn't exist in criteriaDict list, note: code found here: 
			# https://stackoverflow.com/questions/3897499/check-if-value-already-exists-within-list-of-dictionaries
			if not any(d["node"] == int(node[0]) for d in criteriaDict):
				# add bucket
				dictIdx = len(criteriaDict)
								
				criteriaDict.append({
					"node":int(node[0]), 
					"cycles":[], 
					"critical_path":False, 
					"weight": int(node[1]),
					"cycles_below": maxCycles - int(node[2]) + int(node[1]), 
					"parents": [],
					"children": [],
					"distance": int(node[2])})
			else:
				dictIdx = SearchListOfDict(criteriaDict, "node", int(node[0]))
				
			# Add Info to Bucket
			#update parent info
			parent = [-1,0,-1] if (path.index(node) == 0) else path[path.index(node) - 1]
			if(SearchListOfList(criteriaDict[dictIdx]["parents"], 0, parent[0]) == -1):
				criteriaDict[dictIdx]["parents"].append(parent)

			# Update Children Info:
			cIdx = path.index(node) + 1
			child = int(path[cIdx][0]) if cIdx < len(path) else -1
			if(child not in criteriaDict[dictIdx]["children"]):
				criteriaDict[dictIdx]["children"].append(child)
			
			# Update Critical Path Info
			if(path in critPaths):
				criteriaDict[dictIdx]["critical_path"] = True
				
			# Update Cycles Below Info
			if(criteriaDict[dictIdx]["cycles_below"] == -1):
				criteriaDict[dictIdx]["cycles_below"] = cyclesBelow
				cyclesBelow -= criteriaDict[dictIdx]["weight"]
							
			# Determine the cycles that the node can reside in
			testCycle = curCycle
			sum = testCycle + (criteriaDict[dictIdx]["cycles_below"] if -1 not in criteriaDict[dictIdx]["children"] else 0)

			while(sum <= maxCycles):
				addCycle = False
				last = len(criteriaDict[dictIdx]["cycles"]) - 1
				inc = criteriaDict[dictIdx]["cycles_below"] if -1 not in criteriaDict[dictIdx]["children"] else 0
									
				if(last == -1):
					if(testCycle >= maxCycles - criteriaDict[dictIdx]["cycles_below"]):
						addCycle = True					
				else:
					if(criteriaDict[dictIdx]["critical_path"] == False):
						wiggleRoom = maxCycles - criteriaDict[dictIdx]["distance"]
						if(wiggleRoom > 0):
							if(testCycle > criteriaDict[dictIdx]["cycles"][last] and testCycle <= maxCycles - (criteriaDict[dictIdx]["distance"] if -1 not in criteriaDict[dictIdx]["children"] else 0)):
								addCycle = True
						inc = 1 if (-1 not in criteriaDict[dictIdx]["children"]) else 0
				
				if(addCycle and testCycle not in criteriaDict[dictIdx]["cycles"]):
					criteriaDict[dictIdx]["cycles"].append(testCycle)
					
				testCycle += 1
				sum = testCycle + inc
					
			curCycle += 1
	
# 	for i in criteriaDict:
# 		print("Node :", i["node"], 
# 			  ", Weight :", i["weight"], 
# 			  ", Parents :", i["parents"], 
# 			  ", Children:", i["children"],
# 			  ", Critical Path :", i["critical_path"], 
# 			  ", Cycles :", i["cycles"],
# 			  ", Cycles Below :", i["cycles_below"])
	return criteriaDict
	
#----------------------------------
# Calculate Execution Constraints
#----------------------------------
def CalcExecutionConstraints(cDict):
	executionConstraints = []
	# List variables that have to be solved for
	ConstraintNames = []
	for info in cDict:
		constraint = ""
		lastCycle = len(info["cycles"]) - 1
		for cycle in info["cycles"]:
			constraint+="X"+str(info["node"])+"_"+str(cycle+1)
			ConstraintNames.append("X"+str(info["node"])+"_"+str(cycle+1))
			if cycle != info["cycles"][lastCycle]:
				constraint+=" + "
		constraint += " = 1"
		executionConstraints.append(constraint)

	#print()
	#for i in executionConstraints: print(i)
	
	return [executionConstraints, ConstraintNames]

#----------------------------------
# Calculate Dependency Constraints
#----------------------------------
def CalcDependencyConstraints(cDict):
	dependencyConstraints = []
	for info in cDict:
		if(info["parents"][0][0] != -1):
			constraint = ""
			lastCycle = len(info["cycles"]) -1
			for cycle in info["cycles"]:
				correctedCycle = cycle + 1
				if(correctedCycle == 1):
					constraint+= "X"+str(info["node"])+"_"+str(correctedCycle)
				else:
					constraint+= str(correctedCycle)+"X"+str(info["node"])+"_"+str(correctedCycle)
				if cycle != info["cycles"][lastCycle]:
					constraint+=" + "
			constraint += " >= "
			#Add parent constraints
			cConstraint = constraint
			for p in info["parents"]:
				parId = SearchListOfDict(cDict,"node",int(p[0]))
				if parId != -1:
					thisParent = cDict[parId]
					lastPC = len(thisParent["cycles"]) - 1
					for pCycle in thisParent["cycles"]:
						correctedCycle = pCycle + 1
						constraint+= (str(correctedCycle) if correctedCycle != 1 else "")+"X"+str(thisParent["node"])+"_"+str(correctedCycle)
						if cycle != thisParent["cycles"][lastPC]:
							constraint+=" + "
			
				constraint += "1"
				dependencyConstraints.append(constraint)
				constraint = cConstraint #reset constraint for each parent
	
	#print()
	#for i in dependencyConstraints: print(i)
	
	return dependencyConstraints
	
#--------------------------------
# Calculate Resource Constraints
#--------------------------------
def CalcResourceConstraints(cDict, maxCycles, area):
	#Every node per cycle < area
	resourceConstraints = []
	functionConstraints = []
	#Minimize Under Memory
	for cycle in range(maxCycles+1):
		constraint = ""
		for info in cDict:
			if(cycle in info["cycles"]):
				cCycle = cycle + 1
				if(constraint != ""):
					constraint+=" + "
				constraint+="X"+str(info["node"])+"_"+str(cCycle)
				
				if(info["critical_path"] == False):
					functionConstraints.append((str(cCycle) if cCycle != 1 else "") +"X"+str(info["node"])+"_"+str(cCycle))
					
		if(constraint != ""):
			constraint+=" <= "+str(area)
			resourceConstraints.append(constraint)
	
	#print()
	#for i in resourceConstraints: print(i)
	return [resourceConstraints, functionConstraints]
	
#----------------------------------
# Reorganize >= Equations for GLPK
#----------------------------------
def OrganizeEquations(equations):
	newEquations = []
	for e in equations:
		newEq = ""
		sides = e.split(">=")
		newEq += sides[0]
		vars = sides[1].split("+")
		for v in vars:
			isInt = True
			try:
				iv = int(v) #should only have one integer
			except:
				isInt = False
			if(not isInt):
				newEq += "-"+v
		newEq += ">= "+str(iv)
		newEquations.append(newEq)
				
	return newEquations
	
# ---------------------------------
# Save ILP to File
# ---------------------------------
def SaveILP(cn, ec, dc, rc, function):
	
	#open temp file for writing
	fileName = "../temp/temp.lp"
	try:
		f = open(fileName, "w")
	except FileNotFoundError:
		# https://www.geeksforgeeks.org/create-a-directory-in-python/
		path = os.path.join("../", "temp")
		os.mkdir(path)
		
		f = open(fileName, "w")
		
	f.write("Minimize\n")
	f.write(function)
	f.write("\nSubject To\n")
	
	# Add Execution Constraints to file
	for i in range(len(ec)):
		f.write("c"+str(i)+": "+ec[i]+"\n")
	
	# Add Dependency Constraints to file
	for j in range(i+1, len(dc)+i):
		f.write("c"+str(j)+": "+dc[j-i]+"\n")
	
	# Add Check for Positives
	for i in range(len(cn)):
		f.write("i"+str(i)+": "+cn[i]+" >= 0\n")
		
	# Add Resource Constraints to file
	for i in range(len(rc)):
		f.write("r"+str(i)+": "+rc[i]+"\n")
		
	f.write("Integer\n")
	vars = ""
	for i in range(len(cn)-1):
		vars += cn[i]
		if(i < len(cn)-1):
			vars += " "
			
	f.write(vars)
	f.write("\nEnd")
	f.close()
	
	return fileName

#----------------------------------
# Run IPL in GLPK
#----------------------------------
def SimplifyILP(a, l, filename):
	CheckGLPK()
	
	filename2 = filename
	# Call GLPK and feed it the file
	os.system("cd glpk/glpk-4.35/examples; ./glpsol --cpxlp ./../../../../temp/temp.lp")
	return filename2

def CheckGLPK():
	try:
		f = open("./glpk/glpk-4.35/configure")
		f.close()
	except:
		print("No GLPK Library in src. Please install Library to simplify results")
		print("	(see unsimplified results in 'temp' folder)")
		print("\nInstallation Instructions:")
		print("1) Download http://ftp.gnu.org/gnu/glpk/glpk-4.35.tar.gz")
		print("2) Unzip glpk-4.35.tar.gz in src/glpk folder")
		print("3) Open src/glpk/glpk-4.35 folder in command line and install build essentials")
		print("		ex: 'sudo apt-get install build-essential' (or equivalent)")
		print("4) type './configure' in command line in 'glpk-4.35' folder")
		print("5) type 'make' in command line")
		exit()
	return True
	
def SearchListOfDict(listD, searchTerm, value):
	dictIdx = 0
	found = False
	for idx in range(len(listD)):
		if listD[idx][searchTerm] == value:
			#Got nodeInfo dictionary
			found=True
			break
		dictIdx += 1
	if found:
		return dictIdx
	else:
		return -1
		
def SearchListOfList(listL, searchIndex, value):
	listIdx = 0
	found = False
	for idx in range(len(listL)):
		if listL[idx][searchIndex] == value:
			found = True
			break
		listIdx += 1
	if found:
		return listIdx
	else:
		return -1