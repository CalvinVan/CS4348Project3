#Module Imports that I believe will be needed given that we are working with command line arguments and memory

import os
import sys

#Memory and B-tree constants
BLOCK_SIZE = 512
MIN_DEGRREE = 10
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

def main():
  


    