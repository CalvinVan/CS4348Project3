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
