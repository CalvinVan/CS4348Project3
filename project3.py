#Module Imports that I believe will be needed given that we are working with command line arguments and memory

import os
import sys
#import csv for load and extract
import csv

#importing struct for binary stuff


#Memory and B-tree constants
BLOCK_SIZE = 512
MIN_DEGREE = 10
MAX_KEYS = 19
MAX_CHILDREN = 20
MAGIC_NUMBER = b"4348PRJ3" #the magic number in ascii byte encoding

class BTreeNode:
  def __init__(self, blockID, parentID = 0, isLeaf=True): # constructor assume that the node created is a root unless stated otherwise alongside being a leaf node
    self.blockID = blockID
    self.parentID = parentID
    self.numKeys = 0
    #for the keys, values, and children themselves, we will store them in an array which we can later convert to a sequence of bits
    self.keys = [0] * MAX_KEYS
    self.values = [0] * MAX_KEYS #since there are as many values as there are keys
    self.children = [0] * MAX_CHILDREN
    self.isLeaf = isLeaf
    self.modified = False #flag to track if the node has changed for update purposes

  def to_bytes(self): #function to convert the node to byte information for storage using the method mentioned in project notes
    result = bytearray()

    result.extend(self.blockID.to_bytes(8, 'big'))

    result.extend(self.parentID.to_bytes(8, 'big'))

    result.extend(self.numKeys.to_bytes(8, 'big'))

    for key in self.keys:
      result.extend(key.to_bytes(8, 'big'))
    
    for value in self.values:
      result.extend(value.to_bytes(8, 'big'))
    
    for child in self.children:
      result.extend(child.to_bytes(8, 'big'))

    #next we have to encode the remaining block that is not used with an empty space
    remaining = BLOCK_SIZE - len(result)
    result.extend(b'\x00' * remaining)

    return bytes(result)
  
  #Function below is a class defined method for the b tree such that it can parse through the byte and convert it back to readable data in the form of our b tree class 
  @classmethod
  def from_bytes(cls, data):
    node = cls(0) #initialize the node to be our class object which is a b tree
    start = 0
    #Next we are going to parse through our data which should be the byte that is storing our b tree info
    node.blockID = int.from_bytes(data[start:8], 'big')
    
    node.parentID = int.from_bytes(data[8:16], 'big')

    node.numKeys = int.from_bytes(data[16:24], 'big')

    start = 24 #since we last index from 16-24

    for i in range(MAX_KEYS): #loop through to get our keys
      node.keys[i] = int.from_bytes(data[start:start+8], 'big')
      start += 8 
    
    for i in range(MAX_KEYS): #loop through to get our values
      node.values[i] = int.from_bytes(data[start:start+8], 'big')
      start += 8
    
    for i in range(MAX_CHILDREN):
      node.children[i] = int.from_bytes(data[start: start+8], 'big')
      start += 8
    
    # check if it is a leaf
    node.isLeaf = True #by default the node is a leaf
    for c in node.children:
      if c != 0:
        node.isLeaf = False
        break
    
    return node
  
class IndexFile:
  #constructor for index file
  def __init__(self, fileName):
    self.fileName = fileName
    self.file = None
    self.rootBlockID = 0 #initially we assume that we dont have a tree yet so set the root id to 0
    self.nextBlockID = 1 #we have the first block to be our header 
    self.nodesInMemArrDict = {} #We will use a dictionary to hold our nodes to ensure that we only have 3 at a time 
    
  
  def create(self): #Call function to create the index file with a header
    if os.path.exists(self.fileName): #if our file already exists then we should return an error
      print(f"Error: File '{self.fileName}' already exists.")
      return False
    
    try: #try catch block to catch any other error that could error while creating the index file
      with open(self.fileName, 'wb') as f: #given that we are writing our index file in binary / bytes, we open it with 'wb' mode
        f.write(MAGIC_NUMBER)
        f.write((0).to_bytes(8, 'big')) # writing the root id which is 0 since it is empty currently
        f.write((1).to_bytes(8, 'big')) #writing the pointer to the next block id

        remainingBytes = BLOCK_SIZE - 24 #filling in the rest of the empty space with 0's
        f.write(b'\x00' + remainingBytes)
      
      return True
    except Exception as e:
      print(f"Error creating index file: {e}")
      return False
  
  def open(self): #function that opens an existing index file
    if not os.path.exists(self.fileName):
      print(f"Error: File '{self.fileName}' does not exist.")
      return False
    
    try:
      self.file = open(self.fileName, 'r+b') #we open with r to ensure that the file already exists and + to allow both read and write and finally b for binary mode

      magic = self.file.read(8) #get our magic number from the first 8 bytes and check to see if it is a proper index file to open

      if magic != MAGIC_NUMBER:
        print(f"Error: '{self.fileName}' is not a valid index file")
        self.file.close()
        self.file = None
        return False
      
      #else we continue reading for root and next block id

      self.rootBlockID = int.from_bytes(self.file.read(8), 'big')

      self.nextBlockID = int.from_bytes(self.file.read(8), 'big')

      return True
    except Exception as e:
      print(f"Error opening index file: {e}")
      if self.file:
        self.file.close()
        self.file = None
      return False
    
  
  def close(self): #defining a close function for index file to write in the bytes / bytes
    if self.file:
      for node in self.nodesInMemArrDict.values():
        if node.modified:
          self.write_node(node) #call function to write in byte value of our nodes
    

      #Next update our header block/node

      self.file.seek(8) #move the buffer past the magic numbers
      self.file.write(self.rootBlockID.to_bytes(8, 'big'))
      self.file.write(self.nextBlockID.to_bytes(8, 'big'))

      self.file.close()
      self.file = None
      self.nodesInMemArrDict = {} #empty out our nodes in memory

  def read_node(self, blockID): #given the block id, read the node and its info
    if blockID == 0:
      return None #this means that there is no node to read so return false
    
    if blockID in self.nodesInMemArrDict:
      return self.nodesInMemArrDict[blockID] #if our node is already put in memory then just return the node itself
    
    if len(self.nodesInMemArrDict) == 3: #make sure we don't exceed the limit of reading in more nodes
      #we will replace the oldest node
      oldestBlockID = next(iter(self.nodesInMemArrDict)) #we create an iterator over the dictionary and use next to get the first node which is the oldest node in memory
      node = self.nodesInMemArrDict[oldestBlockID]
      if node.modified: #if we have modified the node at all then we should record it in the index file
        self.write_node(node) #
      self.nodesInMemArrDict.pop(oldestBlockID) #pop out the oldest node

    
    self.file.seek(blockID * BLOCK_SIZE) #we move our buffer to the start of where our block id start. Bc it is of size 512, if we want the 4th block in memory then we should move the buffer to 512 * 4
    data = self.file.read(BLOCK_SIZE)  #read the next 512 bytes for information
    node = BTreeNode.from_bytes(data) #convert said byte to node/readable information

    self.nodesInMemArrDict[blockID] = node #add the looked at node into memory
    return node
  
  def write_node(self, node):
    #write the node to the file 
    if not self.file:
      return False
    
    self.file.seek(node.blockID * BLOCK_SIZE) #move buffer to where the block starts in the byte string
    self.file.write(node.to_bytes()) #convert the node data into byte data
    node.modified = False #return to false as we have already updated the node 
    return True
  
  def allocate_node(self): #allocate a new node to memory in the index file
    blockID = self.nextBlockID #go to where we are supposed to write our next block and set that to our block id
    self.nextBlockID += 1 #update where we are supposed to write our next node

    node = BTreeNode(blockID)
    node.modified = True

    if len(self.nodesInMemArrDict == 3):
      #since we are working with a node to allocate it, we need to update memory since a new node is being accessed
      oldestBlockID = next(iter(self.nodesInMemArrDict))
      oldNode = self.nodesInMemArrDict(oldestBlockID)
      if oldNode.modified:
        self.write_node(oldNode) #if it happened to be modified update it first in the byte string then pop it
      self.nodesInMemArrDict.pop(oldestBlockID)

    self.nodesInMemArrDict[blockID] = node
    return node
  
  def search(self, key): #function to search in our b tree for the key
    if not self.file:
      print("Error: No index file is open.")
      return None
    
    if self.rootBlockID == 0: #this means that there is no tree to search for key
      print(f"Error: Key {key} not found as tree is empty.")
      return None

    return self.search_node(self.rootBlockID, key) #call helper function to search for node
  
  def search_node(self, blockID, key): #helper function to search for the node 
    if blockID == 0:
      print(f"Error: Key {key} not found because empty tree.")
      return None

    node = self.read_node(blockID)
    if not node:
      print(f"Error: Key {key} not found because there is no node to search")
    
    i, found = node.search(key) #call b tree search function

    if found:
      return (node.keys[i], node.values[i])
    
    if node.is_leaf: #if it is a leaf then the key can't be found as there are no more nodes to search for
      print(f"Error: {key} not found.")
      return None

    return self.search_node(node.children[i], key) #if we do not find the key and it is not a leaf, we search the children 
  
  def insert(self, key, value): #function to insert key-value pair into b tree
    if not self.file:
      print("Error: No index file is open.")
      return False
    
    if self.rootBlockID == 0: #if the root is empty then we need to create the root
      root = self.allocate_node()
      root.keys[0] = key
      root.values[0] = value
      root.numKeys = 1
      self.rootBlockID = root.blockID
      return True
    
    root = self.read_node(self.rootBlockID) #if there already is a root we should get the root block id and figure where to put it in the tree

    #First we will handle the case if the root is full
    if root.numKeys == MAX_KEYS:
      newRoot = self.allocate_node() #add the new root to memory
      newRoot.isLeaf = False #since now the new root will have a child
      newRoot.children[0] = root.blockID #set the old root to be the child of the new root
      self.rootBlockID = newRoot.blockID

      #update old root's parent
      root.parentID = newRoot.blockID
      root.modified = True

      self.split_child(newRoot, 0, root) #call function to split the old root

      return self.insert_non_full(newRoot, key, value) #call helper function to insert new root
    else: #in the case the root is not full, we can cal
      return self.insert_non_full(root, key, value)
  
  def insert_non_full(self, node, key, value): #insert into a non full node
    i = node.numKeys - 1 #get how many keys are in the node currently and get the index of  where the last key is

    #First we want to check if it is a leaf node
    if node.isLeaf:
      while i >= 0 and key < node.keys[i]: #if our last index is not 0 and our key is less than the key at the i'th position, we will move the keys and values to the right
        node.keys[i+1] = node.keys[i]
        node.values[i+1] = node.values[i]
        i -= 1 #here we will decrement as we start parsing from the end of the array to move values to the right. Also, we dont have to worry the index being at position "19" because this function is only called when the node is not full
      
      #after moving the key and values if the right if necessary, we can add our new key
      #in this case, if it is less than the keys to the right, it will already be added to the left
      #due to i -= 1 from the loop above, else we just add it to the last position possible if it is greater than all of the them.
      node.keys[i+1] = key
      node.values[i+1] = value
      node.numKeys += 1
      node.modfied = True

      return True

    #if the node is not a leaf then we need to parse through to figure where to put the key
    while i >= 0 and key < node.keys[i]: #move our i'th position to put our key to the appropriate spot if it is less than to the right
      i -= 1

    i += 1 #because it is being inserted in the middle of where some key already exists increment it by 1

    child = self.read_node(node.children[i]) #we will then read the node's children at the i position to figure where to insert the new value

    #if child is full where we want to insert it, then we need to split it.
    if child.numKeys == MAX_KEYS:
      self.split_child(node, i, child) # call helper function to split the child

      #when we split, the keys will be split so we need to figure where it fits since the middle key goes up a node
      if key > node.keys[i]:
        i += 1
        child = self.read_node(node.children[i])
    
    return self.insert_non_full(child, key, value) #now we can insert it into the child node which should now be non-full
  
  def split_child(self, parent, index, child): #function to split a full child node
    #create a new child node
    newChild = self.allocate_node()
    newChild.isLeaf = child.isLeaf #we take the status of what child is being split of whether it is a node
    newChild.parentID = parent.blockID
    newChild.numKeys = MIN_DEGREE - 1 

    #we need to copy the last segment of the keys and values of the child that is being split down
    for j in range(MIN_DEGREE - 1): #with the minimum degree, we ensure that each node has the number of minimum keys needed for a child
      newChild.keys[j] = child.keys[j+MIN_DEGREE]
      newChild.values[j] = child.values[j + MIN_DEGREE]

    
    if not child.isLeaf: #if our node is not a leaf then we need to also move the child pointers to be shared with the internal node which must have a minimum # of children as an internal node
      for j in range(MIN_DEGREE):
        newChild.children[j] = child.children[j + MIN_DEGREE]
        movedChild = self.read_node(child.children[j+MIN_DEGREE]) # we need to read in all of the nodes in which are getting moved
        if movedChild:
          movedChild.parentID = newChild.blockID
          movedChild.modified = True
    
    child.numKeys = MIN_DEGREE - 1 #here we shrink the number of keys since we have our minDegree - 1 keys left after splitting it from full
    
    for j in range(parent.numKeys, index, -1): #we must now also shift the parent's children to the right to make space for the new child starting from the end
      parent.children[j+1] = parent.children[j]

    parent.children[index+1] = newChild.blockID #we can now insert the new child node in the parent's children
  

    for j in range(parent.numKeys - 1, index - 1, -1): #We will need to now move the middle key from the child to a parent node so we shift the parent keys and values
      parent.keys[j+1] = parent.keys[j]
      parent.values[j+1] = parent.values[j]

    parent.keys[index] = child.keys[MIN_DEGREE - 1] # we then put in the new parent key/value from the middle key of the child that has been promoted
    parent.values[index] = child.values[MIN_DEGREE - 1]
    parent.numKeys += 1

    #we mark the child, new child, and parent nodes that have been modified
    child.modified = True
    newChild.modified = True
    parent.modified = True


  def load_csv(self, csvFileName): #function to load the key value pairs from a csv file
    if not os.path.exists(csvFileName):
      print(f"Error: CSV file '{csvFileName}' does not exist.")
      return False
    
    try:
      with open(csvFileName, 'r') as csvFile:
        reader = csv.reader(csvFile)

        for row in reader:
          if len(row) < 2: #if it is not a key value pair go to the next row
            continue

          try:
            key = int(row[0])
            value = int(row[1])
            self.insert(key, value)
          except ValueError:
            print(f"Warning: Came across invalid row: {row}")
      return True
    except Exception as e:
      print(f"Error loading CSV file: {e}")
      return False
   
  def printTree(self): #function to print tree
    if not self.file:
      print("Error: No index file is open")
      return
    
    if self.rootBlockID == 0:
      print("Tree is empty.")
      return
    
    print("B-Tree Structure:")
    self.print_node(self.rootBlockID, 0)
  
  def print_node(self, blockID, level):
    if blockID == 0:
      return
    
    node = self.read_node(blockID)
    if not node:
      return
    

    indent = " " * level
    print(f"{indent}Block {blockID} (Level {level}):")
    print(f"{indent} Keys: ", end="")
    for i in range(node.numKeys):
      print(f"({node.keys[i]}, {node.values[i]})", end= " ")
    
    if not node.isLeaf:
      for i in range(node.numKeys + 1):
        self.print_node(node.children[i], level + 1)
  
  

def main():
  # Check if not enough inputs sent through command line
  if len(sys.argv) < 2:
    print("Error. Not enough arguments inputted into command. Input: python project3.py <command> [arguments]")
    return
  
  cmd = sys.argv[1].lower() #ensure consistent capitalization for argument parsing

  if cmd == "create": #error handle and call create index file command
    if len(sys.argv) < 3:
      print("Error: Missing filename for create")
      return
    
    fileName = sys.argv[2]
    indexFile = IndexFile(fileName) #call index file constructor

    if indexFile.create(): #check if the file was created successfully
      print(f"Index file '{fileName}' created successfully.")

  elif cmd == "insert":
    #Check if not enough inputs sent for insert command
    if len(sys.argv) < 5:
      print("Error: Missing arguments for insert command.")
      print("Usage: python project3.py insert <index file name> <key arg> <value arg>")
      return
    
    fileName = sys.argv[2]

    try: #try catch error for if the inputs are integers for the key and value
      key = int(sys.argv[3])
      value = int(sys.argv[4])
    except ValueError:
      print("Error: Key and Value must be integers")
      return

    indexFile = IndexFile(fileName)

    if indexFile.open():
      if indexFile.insert(key, value): #run insert command
        print(f"Key {key} with value {value} inserted sucessfully.")
      indexFile.close()

    elif cmd == "search":

      if len(sys.argv) < 4:
        print("Error: Missing args for search command.")
        print("Usage: pythong project3.py search <index file name> <key>")
        return
      
      fileName = sys.argv[2]

      try:
        key = int(sys.argv[3])
      except ValueError:
        print("Error: Key must be an integer.")
        return

      indexFile = IndexFile(fileName)
      if indexFile.open():
        result = indexFile.search(key)

        if result:
          foundkey, foundVal = result
          print(f"Found Key:{foundkey}, Value: {foundVal}")
        
        indexFile.close()
      
    elif cmd == "load":
      if len(sys.argv) < 4:
        print("Error: Missing arguments for load command")
        print("usage: python project3.py load <index file name> <csv file name>")
      
      indexFileName = sys.argv[2]

      csvFileName = sys.argv[3]

      indexFile = IndexFile(indexFileName)

      if indexFile.open():
        if indexFile.load_csv(csvFileName):
          print(f"Data from '{csvFileName}' loaded successfully on index file '{indexFileName}'")
        
        indexFile.close()
    elif cmd == "print":
      if len(sys.argv) < 3:
        print("Error: Missing file name for print command.")
        print("Usage: python python3.py print <index file name>")
        return

      fileName = sys.argv[2]

      indexFile = IndexFile(fileName)
      if indexFile.open():
        indexFile.print_tree()
        indexFile.close()
    elif cmd == "extract":
      if len(sys.argv) < 4:
        print("Error: Missing arguments for extract command.")
        print("Usage: python project3.py extract <index file name> <output file name>")
        return
      indexFileName = sys.argv[2]
      outputFileName = sys.argv[3]

      indexFile = IndexFile(indexFileName)
      if indexFile.open():
        if indexFile.extract_to_csv(outputFileName):
          print(f"Data extracted to '{outputFileName}' succesfully.")
          indexFile.close()

    else:
      print(f"Error: Unknown command '{cmd}'.")
      print("Available commands: create, insert, search, load, print, extract")


if __name__ == "__main__":
  main()

      
    


  


    