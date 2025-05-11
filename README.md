# CS4348 Project3
The program utilizes one main file which is the project3.py. In it are 2 class definitions which are the BTree nodes and the Index File class.

To run the program you will run in the format: "python project3.py [command] [arguments]"

There are six commands: create, insert, search, load, print, and  extract.

Before delving into the six commands and how to run them, here is a general overview of the program.

The program allows users to create and manage index files that contain B-trees through command line using a various number of programs.

1. create: This function creates an empty index file which can be used to store the btree and is marked with a "magic number" to separate it from other index files. 

To run it, run "python project3.py create [index file name]"

2. insert: This function inserts a single key and value pair into the BTree in an existing index file.

To run it, run "python project3.py insert [index file name] [key] [value]"

3. search: This function searches an existing index file for a key in the BTree

To run it, run "python project3.py search [index file name] [key]"

4. load: This function loads values from a csv file filled with rows of comma separated integer pairs and inserts them into an existing index file which stores BTree nodes.

To run it, run "python project3.py [index file name] [csv file name]"

5. print: This function prints all of the key and value pairs stored in an exisiting BTree Index File.

To run it, run "python project3.py print [index file name]"

6. extract: This function takes an exisiting index file and extracts the BTree keys and values stored in it and puts it in a new CSV file.

To run it, run "python project3.py extract [index file name] [csv file name]"

