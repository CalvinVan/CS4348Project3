# Project 3 Devlog Calvin Van CTV210001 CS4348.003

## May 8th 3:20 PM
Begin reading project requirements.

## Project Requirements
1. Program will manage and create index files.
2. Said index files will contain the b-tree data structure
3. The program is a command-line type program

## Program Commands
1. Create
The create function runs as "project3 create {index file name}"
The function will create a new index file and if the index file already exists then it should fail with an error message.

2. Insert
The insert function runs as "project3 insert {index file name} {key} {value}"
The insert function will insert the key and value into the b tree

3. Search
The search functions runs as "project3 search {index file name} {key}:
The search function will check the index file b tree if the key exists. If found, return the key and value pair.
Error message results if the key is not found or if there is an invalid index file inputted

4. Load
The load function runs as "project3 load {index file name} {csv file name}"
If the file does not exist or is invalid return an error for any of the 2. If it does exist, it will read in the csv file and insert the data stored in the csv file where each line is a key / value pair separated by a comma (3,2)

5. Print
The print function runs as "project3 print {index file name}"
The prnt function prints every key and value pair in the index file to standard output

6. Extract
The extract function runs as "project3 extract {index file name} {csv file name}"
If the index file is not valid then exit with error. If the csv file already exists, exit with error.
The function should create a csv file that stores every key and value pair in the index b-tree as comma separated pairs

## Index File Notes
- The index file will be divided into blocks of 512 bytes.
- Each node of the btree will fit in one block
- The file header will use the entire first block
- New nodes appended to end of file
- No need to worry about delete
- All numbers stored in file should be 8-byte integers. For Python, we can use the to_bytes method to convert the bytes to an integer. So it would be fun as n.to_bytes(8, 'big')
- The header which is maintained in memory will have the following fields
1. Magic number (8 bytes)
2. id of the block containing root node. 0 if it is empty
3. Id of the next block to be addded to the file (Location for a new node.)

## B-tree Notes
- The minimal degree is 10 This means that each node can have 19 key/value pairs and 20 child pointers.
- Each node will be stored in a single block with some header information
- Each block node is brkeon down below:
1. 8 bytes for block id
2. 8 bytes for parent node location. If root, then it is 0
3. 8 bytes for number of key and value pairs in the node
4. 152 bytes: Sequence of 19 64-bit keys
5. 152 bytes: Squennce of 19 64-bit values
6. 160 bytes: Sequence of 20 64-bit offsets. These are the block ids that point to the child of the node. If a child is a leaf node, the corresponding id is 0.
7. Remaining bytes are unused


## May 9th 4:00 PM
Begin working on project.

Start with setting up the main function and implementing the b-tree data structure class. For ease, I will be containing the class definition within one file but better practice would be to of course separate the classes into different python files. Which in this case will be the index file class definition and the b-tree structure definition

Had some breaks in between but finished up the b tree class which includes the constructor and translation from and to byte and b tree form. Time is 830 PM

## May 9th 8:30PM
** B TREE CLASS IS NOT FINISHED SKELETON IS SET UP BUT WILL NEED MORE FUNCTIONS LATER FOR SEARCH AND INSERTION ** For now working on setting up the def main to pass in inputs and to also start working on index file class to manage memory

## May 9th 11PM
Finished up a majority of the program with b tree and index file implementation. Will comment later on it as it is late on progress and implementation.

## May 11th 2:00PM
Did a little bit of work yesterday in implementing function to extract to csv. Continuing working on that and commenting more on the work done.

Finished up project. Will include process covering May 9th 8:30 PM - May 11th 4:00 PM (Time of Completion)

## BTree Node Implementation
Regarding the implementation, we needed to focus on the attributes of what makes a btree and its nodes which is its minimal degree, keys and value pairs, number of keys, and children. These are quite intuitive to store as we can just use integers and arrays set by constants set by the project requirements which is 10 and a max number of keys of 19 and 20 which can be calculated using the minimum degree. We additionally used a boolean status to keep track if a node is a leaf as leaves are treated differently in the BTree data structure alongside with internal nodes so it helps us manage the logic better.

As for the data storage, we know that we needed a blockID to keep track of which the block the node took part of, the parentID of which blocks/nodes it is a child of if any / if it is a root which is a parentID of 0 by default, and the modified boolean to track when we should update our storage and also to keep 3 nodes in memory at a time.

With this, we can handle the attribute initialization to the constructor.

In the BTreeNode implementation, we have 3 functions. A to_bytes implementation to convert our readable data into the byte form by using a bytearray that we can append to by converting the attributes required such as the blockID, parentID, number of keys, keys and value pairs, and children pointers which have all be converted to byte form using the byte method discussed in the project requirements.

Next function is a simple search function to allow for a node to search itself for if a key exists within it.

Finally, the class defined method for the b tree call from_bytes to run a conversion on a bytearray to convert it to a BTreeNode Class Object by parsing the byte ranges

## Index File Implementation
Next, we worked on the implementation of the index file which was the hardest part of the project with having to integrate file management/creation, data storage, and btree management with insertion and search and all the other methods required for the project to be callable through main.

Constructor: Index file constructor was easy as we needed it to be set as a file anyways and have a file name associated with it. Furthermore, we are told to keep track of the root block id and the next block id which can allow us to know what ids to give to new blocks that are created. Finally, there is the node dictionary which we can access its length and ndoes in constant time to manage 3 nodes at a time.

As for the functions, there are 16 functions but there are several helper functions that compose that.

The first method is creating the index file itself which we just check if the file exists and then create it in binary form using the open method and opening in 'wb' mode. Then we initialize the empty folder by writing our "magic number" as an identifier for btree index file identifiers. Alongside, writing the root id and the next pointer bits. Finally filling it in with empty space.

The second method is the open function to open the index file. We implement "security" logic to ensure that it can only be opened in "r+b" form which ensure that the file must exist before opening it again and having it in read and write binary mode. There is logic also checking the first 8 bytes of the index file to ensure it has the magic number to next we can then read for the root and next pointer IDS.

The third method is the close file function. This function will check to ensure that all nodes that have been modified and stored in memory has an opportunity to update their respective information before closing out. Then, we move past the magic number by moving the buffer and writing our root block id and next block id. Finally closing out the file and setting our index file state to empty.

The fourth and fifth methods is for reading and writing the node give the block id / the node itself respectively. The read_node will first check if it has been put in memory first. If it is, then we can just return the node itself. However, if it is not in memory, it will be added into memory. If memory has more than 3 nodes than it will replace the oldest one with the new node read in. The write_node is used for moving the buffer to where the node is stored given the blockID in which we can move it based on the block_size and in which we can write using the node converted into bytes. Now that it has been written, we can then set its modified state to false as it is now updated in the index file.

The sixth method is allocate_node. With allocate node, we take the next block ID pointer and increment it and allocate a new node in the previously empty location. We set the node to a b tree node object in which we can later write to it using the write_node function. Of course, since we are allocating a new node, we will then have to check if there is space in memory to store it.

The seventh and eighth method is the search function alongside the helper function. The function takes in a key and checks if the index file is open or if there is a tree to search to begin with. If not, the print an error message and return None. Else, we call the helper function to search the node given our block ID. The search_node function will then read the node given the block ID and check if there is a node there. If there is not a node at the block ID, return an error else we will run the BTree node function to search for the key. In which we check if the key is found. If not, we will then check if is a leaf, if it is then we return false since there are no more nodes to search for the key. Otherwise, we will make a recursive call to check the node's children for the key

The ninth and tenth function is insert and insert_non_full. The insert function first check if there is even a tree. If not, we will create the root given the key and value. Else, we look for the root using the root block id and then check the root conditions. First check if the root is full, if so, we need to run a split on it and allocate a new node in memory using the allocate new node function and update its children and keys. Furthermore, the program will make a call to split child which will be discussed later. After the split is run, a call to a helper function called split_child will be made to properly split the node to update the keys and promotions. If the root or node that is being inserted into is not full, then we can just call the insert_non_full function as is. The insert_non_full function inserts the key and value pair into a non full node. It will traverse through the keys and move them to their appropriate index depending on if it is > or < then depending if it is a leaf. If it is not a leaf, then we need to figure where to put it in its children by finding the key in which to traverse down to the children. In the case that the child is full, we will then have to run a split on the child node and then figure out where to put said key.

The eleventh method is split_child. Because we know that we will need a new child, we will need to allocate a new node. Furthermore, the new child will take the status of isLeaf depending on what it is splitting from. From there, we run a for loop to get the minimum number of keys needed for a node and we take the latter half of the keys from which it is being split from. Afterwards, we check if it is an internal node in which we also need to update the child pointers and shift the children for the parents for
any type of node. Finally, we need to move the also promote a node to the parent whena  split happens.

The twelfth method is load_csv in which we will load the key and value pairs from a csv file. We will read the file and storing the two numbers as a key and value checking to make sure they are integers and running the insert function to insert them into the index file. 

The thirteenth and fourteenth methods are the print_tree and print_node functions. The print tree function checks for the root node and then calls for the recursive print_node function to iterate through all the nodes and its children to print out the keys and value pairs.

The fifteenth and sixteenth functions are the extract_to_csv_ and extract_node functions. extract_to_csv will opoen up a new output file with write mode and createe the csv file and then call the recursive extract_node helper function to traverse through the nodes in in-order traversal to convert it to the csv file format.

## Main setup
Typical if else setup to check for command line inputs and checking for the cmd type to process which function to call respectively.


Project ended with testing all the functions which seems to be running properly and troubleshooting some bugs that occurred due to naming errors / missing letters / indentation errors which were eventually resolved.

## May 11th 5:20PM
Work on readme 
Finished at 5:40PM