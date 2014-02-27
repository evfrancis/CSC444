#!/usr/bin/env python
import sys
import os

#cleanup
os.system("rm testCommit.file")
os.system("rm -rf .vc_data")

#Testing
max_sync = 10
max_branches = 10

iterate = 0

#put current directory under version control - harmless if already under version control
os.system("python vc.py setup")

#create an empty 'testCommit.file' file that we will commit
open("testCommit.file", 'w').close()

#add file to versioning system
os.system("python vc.py add testCommit.file")

#Complete 'max_sync' number of commits
while (iterate < max_sync):
    iterate = iterate+1
    commit_sentence = " \"I made a change - %s\" " % iterate
    os.system("python vc.py edit testCommit.file")
    
    #Append the iterate number and commit so every new commit will create a new numbers   
    target = open("testCommit.file",'a') 
    target.write( str(iterate)+"\n" )
    target.close()

    os.system("python vc.py commit testCommit.file "+commit_sentence)
iterate = 0

#Test sync by syncing from the 1st revision to the HEAD revision
while (iterate < max_sync):
    iterate = iterate+1
    os.system("python vc.py sync testCommit.file %s" % str(iterate))
    os.system("cat testCommit.file")
iterate = 0

#Sync to the latest revision using the HEAD tag
os.system("python vc.py sync testCommit.file HEAD")

#Test branch functionality by branching testCommit.file and viewing its logs
while (iterate < max_branches):
    iterate = iterate+1
    os.system("python vc.py branch testCommit.file newBr%s" % str(iterate))
    os.system("python vc.py switchbranch newBr%s" % str(iterate))
    os.system("python vc.py log testCommit.file")

#Try to commit the same file without making any changes
commit_sentence = " \"Malicious commit - no change in file\" "
os.system("python vc.py edit testCommit.file")
os.system("python vc.py commit testCommit.file "+commit_sentence)
os.system("echo \"drat that didn't work\"")

#Make a good commit and recover to get 2 revisions in branch 'newBr10'
target = open("testCommit.file", 'a')
iterate = iterate+1
target.write( str(iterate)+"\n" )
target.close()
commit_sentence = " \"I made a change - %s\" " % iterate
os.system("python vc.py commit testCommit.file "+commit_sentence)

#Now test suggest by suggesting changes from newBr10 to main
#This will be conflict free
os.system("python vc.py suggest testCommit.file newBr10 main")
print "Viewing suggest file"
os.system("cat testCommit.file.suggest")



