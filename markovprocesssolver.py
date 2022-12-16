import re
from collections import defaultdict
import sys
import getopt

class Node():
	def __init__(self,nodename):
		self.name = nodename
		self.value = 0
		self.prev =0
		self.neighbors = []
		self.reward = 0
		self.isTerminal = False
		self.has_neighbors = False
		self.has_probs = False
		self.has_reward = False
		self.chance_node = False
		self.decision_node = False
		self.win_prob = 0
		self.neighbor_probs = {}
		self.probs = []
		self.policy = None

	def add_neighbos(self,nbrs):
		
		for i in nbrs:
			self.neighbors.append(i.strip(",| "))
	
		
		self.has_neighbors = True
		self.neighbor_probs = {}

	def add_reward(self,num):
		self.reward = num
		self.has_reward = True

	def add_probs(self, probs):

		for i in probs:
			self.probs.append(float(i.strip(" ")))
		
	
		self.has_probs = True

	def check(self, list_of_nodes):

		for i in self.neighbors:
			if i not in list_of_nodes.keys():

				print("Error: Given neighbor does not exist")
				return 1

		# has neighbors and has probs
		if self.has_neighbors and self.has_probs:
			
			# equal number of neighbors and probs
			if len(self.neighbors) == len(self.probs):
				self.chance_node = True
				total=0
				for i in range(len(self.neighbors)):
					self.neighbor_probs[self.neighbors[i]] = float(self.probs[i])
					total += float(self.probs[i])

				#  probability sum checker
				if abs(1-total) >= 0.0001:
					print("Error: Probabilities don't sum up to 1")
					return 1

			# single prob
			elif len(self.probs) == 1:
				if float(self.probs[0]) <= 1.0:
					self.decision_node = True
					self.win_prob = self.probs[0]
				else:
					print("Error: Incorrect probability for decision node, should be equal to 1.0")
					return 1

			elif len(self.probs) > len(self.neighbors):
				print("Error: Invalid number of Probabilities")
				return 1
			elif len(self.probs) >1 and len(self.probs) < len(self.neighbors):
				print("Error: Invalid number of Probabilities")
				return 1

		
		# has neighbors but no probs
		elif self.has_probs == False and self.has_neighbors:
			self.decision_node = True
			self.win_prob = 1.0
		
		# has probs but no neighbors
		elif self.has_probs and not self.has_neighbors:
			print("Error: No neighbors given but probability given", self.name, self.has_neighbors, self.neighbors)
			return (1)
		
		# no neighbors
		elif self.has_neighbors == False:
			self.isTerminal = True

		return 0



		


def parsefile(filename):
	
	lines = open(filename, "r").readlines()
	list_of_nodes = {}
	nodes = []

	for line in lines:
		line = line.strip()
		if len(line) == 0:
			continue
		if line[0] == "#":
			continue

		percent = line.split("%")
		equal = line.split("=")
		colon = line.split(":")
		
		
		if (len(percent)>1 and len(colon)>1) or (len(colon)>1 and len(equal)>1) or (len(equal)>1 and len(percent)>1):
			print("Error: Invalid input")
			return 1, [], []
			
		elif len(equal) == 2:
			equal.insert(1,"=")
			# print("Node:", equal[0], list_of_nodes)
			if equal[0].strip() in list_of_nodes.keys():
				if list_of_nodes[equal[0].strip()].has_reward == False:
					list_of_nodes[equal[0].strip()].add_reward(int(equal[2]))
				else:
					print("Error: Multiple value statements ")
					return 1, [], []
			else:
				node = Node(equal[0].strip())
				node.add_reward(int(equal[2]))
				list_of_nodes[equal[0].strip()] = node
				nodes.append(node)
				

		elif len(colon) == 2:
			colon.insert(1,":")
			if colon[0].strip() in list_of_nodes.keys():
				if list_of_nodes[colon[0].strip()].has_neighbors == False:
					s = colon[2]
					s = s.strip("[|]| ")
					
					r = re.findall(r"\S+", s)
					
					if not r[-1].isalnum():
					    print("Error:invalid neighbors string")
					    return 1, [], []
					list_of_nodes[colon[0].strip()].add_neighbos(r)
				else:
					
					print("Error: Multiple neighbors statements ")
					return 1, [], []
			else:
				node = Node(colon[0].strip())
				s = colon[2]
				s = s.strip("[|]| ")
				r = re.findall(r"\S+", s)
				if not r[-1].isalnum():
				    print("Error:invalid neighbors string")
				    return 1, [], []
				
				node.add_neighbos(r)
				list_of_nodes[colon[0].strip()] = node
				nodes.append(node)

		elif len(percent)==2:
		
			percent.insert(1,"%")
			if percent[0].strip() in list_of_nodes.keys():

				if list_of_nodes[percent[0].strip()].has_probs == False:
					s = percent[2]
					s = s.strip()
					r = re.split(',| ',s)
					list_of_nodes[percent[0].strip()].add_probs(list(r))

				
				else:				
					print("Error:Multiple probability statements")
					return 1, [], []
			else:

				node = Node(percent[0].strip())
				s = percent[2]
				s = s.strip()
				r = re.split(',| ',s)
				if not isinstance(float(r[-1]), float):
					print("Error: incorrect probability values")
					return 1, [], []

				node.add_probs(list(r))
				list_of_nodes[percent[0].strip()] = node
				nodes.append(node)

		else:
			print("Error:Invalid input")
			return 1, [], []

	for node in nodes:
		check = node.check(list_of_nodes)

		if check == 1:
			return check, list_of_nodes, nodes

	return 0, list_of_nodes, nodes

def policy_update(list_of_nodes, nodes):
	update = 0
	for i in nodes:
		if i.decision_node and len(i.neighbors)>1:
			list_of_vals = defaultdict(list)
			for n in i.neighbors:
				list_of_vals[list_of_nodes[n].prev].append(n)
			max_val = max(list_of_vals.keys())
			
			if i.policy not in list_of_vals[max_val]:
				i.policy = list_of_vals[max_val][0]
				update += 1

	if update == 0:
		return 1
	else:
		return -1

def policy_update_min(list_of_nodes, nodes):
	update = 0
	for i in nodes:
		if i.decision_node and len(i.neighbors)>1:
			list_of_vals = defaultdict(list)
			for n in i.neighbors:
				list_of_vals[list_of_nodes[n].prev].append(n)
			max_val = min(list_of_vals.keys())
			
			if i.policy not in list_of_vals[max_val]:
				i.policy = list_of_vals[max_val][0]
				update += 1

	if update == 0:
		return 1
	else:
		return -1



def msp(list_of_nodes, nodes,tolerance = 0.01, iters = 100, df=1.0):
	ite= 0


	for i in nodes:
		i.prev = 0.0


	while ite<iters:
		for node in nodes:
			if not node.isTerminal:
				if node.chance_node:
					node.value = node.reward
					
					for n in node.neighbors:
						node.value += float(node.neighbor_probs[n]) * df * float(list_of_nodes[n].prev)

				elif node.decision_node:
					node.value = node.reward
					
					if len(node.neighbors)>1:
						pro = (1 - float(node.win_prob))/(len(node.neighbors)-1)
						multiflag = False
						for n in node.neighbors:
							
							if node.policy == n and multiflag == False:
								node.value += float(node.win_prob) * df * float(list_of_nodes[n].prev)
								multiflag = True
							else:
								node.value += pro * df * list_of_nodes[n].prev
					else:
						for n in node.neighbors:
							node.value += float(node.win_prob) * df * float(list_of_nodes[n].prev)
				
			else:
				node.value = node.reward

		count = 0
		
		for node in nodes:
			if abs(node.value-node.prev)<= tolerance:
				count+=1
			node.prev = node.value

		

		if count==len(nodes):
			break
		
		ite+=1
	
	return



if __name__ == "__main__":
    
    
    argumentList = sys.argv[1:]
    options = "D:T:F:MI:"
    
    df = 1.0
    tolerance = 0.01 
    min_flag = False
    iters = 100
    file_name = None
  

    arguments, values = getopt.getopt(argumentList, options)
    
    for currentArgument, currentValue in arguments:
        
        if currentArgument in ("-D"):
         
            try:
                if currentValue is None or currentValue==" ":
                    print("Error: Missing DF value")
                    exit(0)
                elif float(currentValue)>1 or float(currentValue)<0:
                    print("Error: Invalid DF value, should be between 0 and 1")
                    exit(0) 
               
                else:
                	df = float(currentValue)
            except:
                print("Invalid DF value")
                sys.exit(0)
           
             
        elif currentArgument in ("-F"):
            try:
                
                if currentValue is None:
                    print("Error: Missing file name")
                    exit(0)
                else:
                    file_name = str(currentValue)
           
            except:
                print("Invalid File Name")
                sys.exit(0)
                
        elif currentArgument in ("-T"):
            try:
                if float(currentValue)<0:
                    print("Error: Invalid tolerance value, should be > 0")
                    exit(0)
                else:
                    tolerance = float(currentValue)
            except:
                print("Invalid tolerance value")
                sys.exit(0)
        
        elif currentArgument in ("-M"):
        	min_flag = True

        elif currentArgument in ("-I"):

        	if not isinstance(int(currentValue), int) or int(currentValue)<0 :
        		print("Error: Invalid Iteration")
        		sys.exit(0)
        	else:

        		iters = int(currentValue)
        	
        
        else:
            print("Error: Invalid Argument")
    


if file_name is None:
	print("missing input file")
	exit(0)


check, list_of_nodes, nodes = parsefile(file_name)

if check==1:
	exit()



for i in nodes:
	if i.decision_node and len(i.neighbors)>1:
		i.policy = i.neighbors[0]

update = -1

while update == -1:

	msp(list_of_nodes, nodes, tolerance, iters, df)
	if min_flag:
		update = policy_update_min(list_of_nodes, nodes)
	else:
		update = policy_update(list_of_nodes, nodes)


for i in nodes:
	if i.decision_node and len(i.neighbors)>1:
		print(i.name, "->",i.policy)

print()

for i in sorted(list_of_nodes.keys()):
	print(list_of_nodes[i].name, format(round(list_of_nodes[i].prev,3),".3f"), end = ' ')

print()









