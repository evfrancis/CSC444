#!/usr/bin/env python
'''
STUDENT INFO:
Name: Everard Francis
Name: Calvin Fernandes


REQUIREMENTS:
- Handle ASCII text files only.
- Put a file under source code control. (add):
- Check in a modified version of a file after the user edits it. (commit):
- Allow the user to associate a comment with each check-in. (commit: option):
- Assign version numbers to all check-ins. (commit):
- Check out the most current version of a file. (sync):
- Check out any older version of a file by version number. (sync: option):
- List all versions of a file with their associated check-in comment. (log):
- Create a new source control branch for a file associating a unique user-chosen identifier with the new branch (the original branch should be called "main")
- All of the above requirements should be satisfyable equally for all branches.
- Generate a suggested file as the next version for branch X based on the last change applied to branch Y (where X and Y can be any non-equal branch names).

Architecture:
Project/
    .vc_data/
        branch  [File: Content is name of branch. In this case, main]
        pending [File: Content keep track of files marked for add or edit]
        main/  [Dir:  Content is replicate of source control tree, containg history]
            <fileA.c>/           [Each file is stored as a directory that contains all versions]
                    fileA.c.ver1     [First version of the file]
                    fileA.c.ver2
                    fileA.c.ver3
                    fileA.c.versions [Each line is the commit message of a version, in double quotes. A * denotes the synced version]
            <fileB.c>/
                    fileB.c.ver1
                    fileB.c.ver2
                    fileB.c.versions
            <fileC.c>/
                    fileC.c.ver1
                    fileC.c.versions
    <folderA>/
        fileA.c
    <folderB>/
        fileC.c
        fileB.c
'''

import sys
import os
import shutil
import difflib

#######################################################
#############  DATA STRUCTURES   ######################
#######################################################

vcDataDir = ""
pendingPath = ""
branchPath = ""

#######################################################
########### FILE ACCESS FUNCTIONS #####################
#######################################################

# Opens and reads a file, returning an array of the file contents without newlines
# Args: path - the path of a valid file
# Returns: an array of the file contents
def readFile(path):
    File = open(path, "r")
    data = File.readlines()
    File.close()
    outData = []
    for line in data:
        outData.append(line.rstrip("\n"))
    return outData

# Opens and appends a string to a file, adding a newline at the end
# Args: path - the path of a valid file
#       line - a string to append
# Returns: N/A
def appendFile(path, line):
    File = open(path, "a")
    File.write(line + "\n")
    File.close()

# Opens and writes data to a file, adding a newline at the end of each line of data
# Args: path - the path of a valid file
#       data - a list of data to be written to a file
# Returns: an array of the file contents
def writeFile(path, data):
    File = open(path, "w")
    for line in data:
        File.write(line + "\n")
    File.close()

#######################################################
############  HELPER FUNCTIONS   ######################
#######################################################

# Checks if the current directory has an associated repo
# This is done based on the existence of a vcDataDir folder, in the current or parent dir
# Returns True or False based on the existence of the vcDataDir
def initialized():
    global vcDataDir                        
    global pendingPath
    global branchPath

    if (os.path.isdir(".vc_data") == True):
        # The .vc_data directory exists, meaning we are in a valid repo
        # Setup out global variable file paths for this repo
        vcDataDir = os.path.join(os.getcwd(),".vc_data")
        pendingPath = os.path.join(vcDataDir,"pending")
        branchPath = os.path.join(vcDataDir,"branch")
        return True
    else: 
        # The user is not in an initailized repository
        return False

# Checks if a file is under version control
# Args: myFile - a string of the file path, relative to root
# Return: True or False depending on whether the file is under revisionc ontrol
def isUnderVC(myFile):
    # If the file is already under version control, it will exist as a
    # directory with the same filename, in the vcDataDir folder
    return os.path.isdir(getVcPath(myFile))

# Tries to add a file to the pending list. Typically for add or edit
# Args: myFile - a string of the file path, relative to root
# Return: True or False depending on whether the action was successful
def addToPending(myFile):
    pendingList = readFile(pendingPath)
    if (myFile in pendingList):
        return False
    else:
        pendingList.append(myFile)
        writeFile(pendingPath, pendingList)
        return True

# Find out which branch we are currently using by reading the file
# the file called 'branch' that contains this information
# Return: a string for the branch we are on
def currentWorkingBranch():
    targetPath = os.path.join(vcDataDir,"branch")
    currentBranch = readFile(targetPath)[0]
    currentBranch = currentBranch.rstrip()  #remove new line

    #check if currentBranch actually exists in the vc_data directory
    fullPath = os.path.join(vcDataDir, currentBranch)
    if (os.path.isdir(fullPath) == True):
        return currentBranch
    else:
        sys.exit("Error: Branch %r does not exist under version control" % currentBranch)

# Find the proper path that will enable us to put the file under versioning
# Args: fileToInsert - a string that is the name of a file
# Return: a string for the vc directory path corresponding to the file
def getVcPath(fileToInsert):
    curWorkingBranch = currentWorkingBranch() 
    # Create the proper path for storage in the vc system
    newDataPath = os.path.join(vcDataDir,curWorkingBranch,fileToInsert)
    # Return the path to where the file should be placed in our versioning system
    return newDataPath  

# Get the head revision of a file
# Args: filename - a string that is the name of a file
# Returns: an integer, the number of the head revision of the file
def getHeadRevision(fileName):
    filePath = getVcPath(fileName)
    
    # The number of lines in <path>/<file>.versions denotes the number of versions
    versionsPath = os.path.join(filePath, fileName + ".versions")
    versionsFile = readFile(versionsPath)
    numVersions = len(versionsFile)

    return numVersions

# This function stores a user file into the repo.
# It exists to abstract the underlying algorithm used to compress the files
# Args: file - the user file path
#       revision - a number specifying the revision of the file
def storeFile(file, revision):
    vcPath = getVcPath(file)
    storePath = os.path.join(vcPath,file)
    # PLEASE NOTE: We only use mode 2, which is the compressed storage
    # the other modes exist only exist as proof that we evaluated its performance
    # (SEE EFFICIENCY SECTION OF DOC)
    mode = 2
    if (mode==1):
        # Store full copies of each version
        storePath = storePath + ".ver" + str(revision)
        os.system("cp %s %s" % (file, storePath))
    elif (mode==2):
        # Store compressed copy of each version
        storePath = storePath + ".ver" + str(revision) + ".gz"
        os.system("gzip -c %s > %s" % (file, storePath))
    elif (mode==3):
        if (revision % 10) == 1:
            storePath = storePath + ".ver" + str(revision)
            os.system("cat %s > %s" % (file, storePath))
            os.system("gzip %s" % (storePath))
        else:
            ref = revision / 10 + 1
            refPath = storePath + ".ver" + str(ref)
            storePath = storePath + ".ver" + str(revision)
            os.system("gunzip %s" % (refPath+".gz"))
            os.system("diff %s %s > %s" % (refPath, file, storePath))
            os.system("gzip %s" % (storePath))
            os.system("gzip %s" % (refPath))

# This function restores a user file from the repo.
# It exists to abstract the underlying algorithm used to compress the files
# Args: file - the user file path
#       revision - a number specifying the revision of the file
# Returns: A path to a temporary file with the requested restore
def restoreFile(file, revision):
    vcPath = getVcPath(file)
    storePath = os.path.join(vcPath,file)
    temp = ""
    # PLEASE NOTE: We only use mode 2, which is the compressed storage
    # the other modes exist only exist as proof that we evaluated its performance
    # (SEE EFFICIENCY SECTION OF DOC)
    mode = 2
    if (mode==1):
        # Store full copies of each version
        storePath = storePath + ".ver" + str(revision)
        temp = storePath + "_"
        os.system("cp %s %s" % (storePath, temp))
    elif (mode==2):
        # Store compressed copy of each version
        temp = storePath + ".ver" + str(revision)
        storePath = temp + ".gz"
        os.system("gunzip -c %s > %s" % (storePath, temp))
    elif (mode==3):
        if (revision % 5) == 1:
            storePath = storePath + ".ver" + str(revision)
            temp = storePath + "_"
            os.system("gunzip -c %s > %s" % (storePath, temp))
        else:
            ref = revision / 5 + 1
            refPath = storePath + ".ver" + str(ref)
            storePath = storePath + ".ver" + str(revision)
            temp = storePath + "_"
            os.system("gunzip %s" % refPath)
            os.system("gunzip %s" % storePath)
            os.system("patch %s %s -o %s > /dev/null" % (refPath, storePath, temp))
            os.system("gzip %s" % refPath)
            os.system("gzip %s" % storePath)
    return temp

# This function is responsible for removing lines
# that begin with a ? from a given sequence. This is
# part of the suggest algorithm. Lines in a sequence 
# that begin with a ? represent lines that are not 
# present in either input sequence
# inputs:  list object
# outputs: list object 
def drop_inline_diffs(diff):
    r = []
    for t in diff:
        if not t.startswith('?'):
            r.append(t)
    return r

# This function tries to apply (patch) the last difference between two segments of text into a third segment of text
# Args: YCurrent: The most recent segment of text
#        YPrev: The ancestor text of YCurrent
#        XCurrent: The segment of text we want the diff to be applied to
# Returns: hadConflicts: A number >= 0 representing the number of diffs that could not be applied
#          XCurrent: The updated text after applying patches
def mergeFiles(YCurrent, YPrev, XCurrent):
    # This is a class for comparing sequences of lines of text, 
    # and producing human-readable differences or deltas.
    diff = difflib.Differ()

    # Compare YCurrent to YPrev
    # The result will be a file with the code of YPrev + the diffs to make YCurrent 
    # Using the following characters at the start to denote changes:
    # '- ' means line unique to sequence 1
    # '+ ' means line unique to sequence 2
    # '  ' means common to both sequences
    # '? ' means line not present in either input sequence
    # After, we remove lines that are not present in either sequence
    inlinedDiffY = drop_inline_diffs(diff.compare(YPrev, YCurrent))

    indexY = 0
    indexX = 0
    hadConflicts = 0

    # Scan through the inlined diff Y file looking for diffs
    while (indexY < len(inlinedDiffY)):
        # If there is a diff segment, it will NOT start with " "
        if (not inlinedDiffY[indexY].startswith(' ')):
            # Found a diff block, let's mark its start/end 
            startIndexDiff = indexY
            while (indexY < len(inlinedDiffY) and (not inlinedDiffY[indexY].startswith(' '))):
                indexY = indexY + 1

            # Mark the end
            endIndexDiff = indexY

            # Now that we have bounded the diff, we want to
            # extend the bound by a certain amount, to increase accuracy
            scanLength = 2
            segmentBelowCutoff = max(0, startIndexDiff - scanLength)
            segmentAboveCutoff = min(len(inlinedDiffY), endIndexDiff + scanLength)

            # We can now derive the blocks preceding and following the diff
            # For more accuracy, we want to make a third block
            # Which contains all of the lines removed
            # Additionally, we want to make a block of added lines, in the
            # In the event that we can apply the diff
            tempIndex = startIndexDiff
            removedList = []
            addedList = []
            while (tempIndex < endIndexDiff):
                if (inlinedDiffY[tempIndex].startswith('-')):
                    removedList.append(inlinedDiffY[tempIndex])
                if (inlinedDiffY[tempIndex].startswith('+')):
                    addedList.append(inlinedDiffY[tempIndex])
                tempIndex = tempIndex + 1

            # We can now join these three segments
            # What we get is the segment of data that a change occured on
            searchBlock = inlinedDiffY[segmentBelowCutoff : startIndexDiff]
            searchBlock = searchBlock + removedList
            searchBlock = searchBlock + inlinedDiffY[endIndexDiff : segmentAboveCutoff]

            # Additionally, we join the preceding/following
            # areas with the new code added to get the patch block
            patchBlock = inlinedDiffY[segmentBelowCutoff : startIndexDiff]
            patchBlock = patchBlock + addedList
            patchBlock = patchBlock + inlinedDiffY[endIndexDiff : segmentAboveCutoff]

            # Strip off the diff metadata now (first 2 chars)
            searchBlock = [line[2:] for line in searchBlock]
            patchBlock = [line[2:] for line in patchBlock]

            # if searchBlock exists in file XCurrent, that means
            # we have a match to apply the patch
            matchFound = False
            while (indexX < (len(XCurrent) - len(searchBlock))):
                matchFound = False
                if (XCurrent[indexX: indexX + len(searchBlock)] == searchBlock):
                    # We have a match, remove the old code and patch
                    matchFound = True
                    XCurrent = XCurrent[0: indexX] + patchBlock + XCurrent[indexX + len(searchBlock) : len(XCurrent)]

                    # Update the index, have completed this portion
                    indexX += len(patchBlock)
                    break
                indexX = indexX + 1
            # We must make sure the patch was applied, if it was not, alert the user
            # that we do not know how to apply the patch
            if (matchFound == False):
                hadConflicts = hadConflicts + 1
                print "Warning: Had problems merging a total of: %s segments" % str(hadConflicts)
        indexY = indexY + 1

    return hadConflicts, XCurrent
#######################################################
#############  CORE FUNCTIONS   #######################
#######################################################

# Adds a list of files to the pending list. Checks if each argument is a
# file that exists not already under vc, and ignores everything that does not
# meet this criteria
# Args: A list of files
def add(args):
    # It is mandatory to give at least one file as an argument
    if len(args) < 1:
        sys.exit("Error: Add requires at least 1 file as arguments")

    # Parse all arguments (files)
    for file in args:
        if (os.path.isfile(file)):
            # Argument is a file that exists, we do not store directories
            if (isUnderVC(file)):
                # Ignore if already under version control (User should use edit)
                print "Warning: File \"%s\" is already under version control, skipped" % file
            elif (addToPending(file)):
                # Add the file if it is truly new
                print "Adding file \"%s\"" % file
            else:
                # Ignore if it was already pending add/edit
                print "Warning: File \"%s\" is already pending with type \"add\", skipped" % file
        elif (os.path.isdir(file)):
            print "Warning: excluding directory \"%s\"" % file
        else:
            # File does not exist
            print "Warning: No such file \"%s\"" % file

# Commits a file to the repository. Only files marked for add/edit will commit
# Args: args[0] - A string representing a file name
#       args[1] - A string representing a commit message
def commit(args): 
    if len(args) != 2:
        sys.exit("Error: Commit require 2 arguments: file and message")

    file = args[0]
    msg = args[1]

    pendingFiles = readFile(pendingPath)

    if (file in pendingFiles):
        # Get the important file paths (versions log, current_version file)
        vcFilePath = getVcPath(file)
        curVersionPath = os.path.join(vcFilePath, file + ".current_version")
        versionsFilePath = os.path.join(vcFilePath, file + ".versions")

        if (os.path.isdir(vcFilePath)):
            # File is marked as pending and the vc path exists, therefore it is an edit
            versionHistory = readFile(versionsFilePath)
            headVersion = getHeadRevision(file)

            userVersion = int(readFile(curVersionPath)[0])

            # Check if the user is synced up to head before commiting
            if (userVersion != headVersion):
                sys.exit("Error: you do not have the most recent version of \"%s\". Please sync before committing." % file)
            
            # Grab the last commited version of the file and diff it with what the user is committing
            # The user must have changed the file to submit a new version
            tempPath = restoreFile(file,headVersion)
            difference = os.system("diff %s %s > /dev/null" % (tempPath, file))

            # Remove the temporary file
            os.remove(tempPath)

            # If there is no difference, then the user has not changed anything - cancel the submission
            if (difference == 0):
                sys.exit("Error: cannot commit file \"%s\", no change detected from head" % file)

            # Increment head version, set as current version
            # Add new commit message to log and copy over the new version
            headVersion = headVersion + 1
            writeFile(curVersionPath, [str(headVersion)])
            appendFile(versionsFilePath, msg)
            storeFile(file, headVersion)
        else:
            # File is marked as pending but the vc path does not exist, therefore it is an add
            # Step 1 - Create the vc file directory
            os.makedirs(vcFilePath)

            # Step 2 - Create the necessary vc files (current_version, initial version)
            writeFile(curVersionPath, ["1"])

            # Step 3 - Write the msg into the versions file and store the file in VC
            writeFile(versionsFilePath, [msg])
            storeFile(file, 1)

        # Step 4 - Now that the file is commited, remove it from pending 
        pendingFiles.remove(file)
        writeFile(pendingPath, pendingFiles)
    else:
        sys.exit("Error: File \"%s\" has not been marked for edit/add" % file)

    print "File \"%s\" commited with message \"%s\"" % (file, msg)

# Edits a list of files to the pending list. Checks if each argument is a
# file that exists under vc, and ignores everything that does not
# meet this criteria
# Args: A list of files
def edit(args):
    # It is mandatory to give at least one file as an argument
    if len(args) < 1:
        sys.exit("Error: Edit requires at least 1 file as arguments")

    # Parse all arguments (files)
    for file in args:
        if (os.path.isfile(file)):
            # Argument is a file that exists, we do not store directories
            if (isUnderVC(file)):
                # Check if file's current version is at the HEAD revision
                # path is the root directory which contains all our data for this file
                path = getVcPath(file)
                currentVersionPath = os.path.join(path, file + ".current_version")
                currentVersion = int(readFile(currentVersionPath)[0])
                numVersions = getHeadRevision(file)

                if (numVersions != currentVersion):
                    sys.exit("Error: You can only edit the file if you are the HEAD revision")

                # File is under VC, necessary for an edit
                if (addToPending(file)):
                    # The file was not pending before, mark the file as editable
                    print "File \"%s\" is open for edit" % file
                else:
                    print "Warning: File \"%s\" is already pending with type \"edit\", skipped" % file
            else:
                # Ignore if not under VC, user should use add
                print "Warning: File \"%s\" is not under version control, skipped" % file
        elif (os.path.isdir(file)):
            print "Warning: excluding directory \"%s\"" % file
        else:
            # File does not exist
            print "Warning: No such file \"%s\"" % file

# Syncs a file to a specified revision
# Args: args[0]: file
#       args[1]: revision number or HEAD to sync to top of tree
def sync(args):
    # It is mandatory to give 2 arguments
    if len(args) != 2:
        sys.exit("Error: Sync requires 2 arguments, file and revision")

    file = args[0]
    version = args[1]

    # Check if the file is under version control
    if (not isUnderVC(file)):
        sys.exit("Error: File \"%s\" is not under version control, skipped" % file)

    # Check if the file is pending. Only files that are commited can be synced
    pendingFiles = readFile(pendingPath)

    if (file in pendingFiles):
        sys.exit("Error: Cannot sync a file that is pending submission. Please commit before syncing")

    # path is the root directory which contains all our data for this file
    path = getVcPath(file)

    # Get the number of versions (head)
    numVersions = getHeadRevision(file)

    # Version argument must be numeric
    try:
        version = int(version)
    except ValueError:
        if (version == "HEAD"):
            # Sync to head
            version = numVersions
        else:
            sys.exit("Error: Version number must be numeric") 

    # Check if the user's version is within the correct range
    if (version > numVersions or version < 1):
        sys.exit("Error: No such version \"%s\" of file \"%s\". Valid Range: [1,%s]" % (version, file, numVersions))

    # The value in <path>/<file>.current_version denotes the version we are on, update this
    currentVersionPath = os.path.join(path, file + ".current_version")
    writeFile(currentVersionPath, [str(version)])

    # Now that we have updated the file version, copy over this version of the file to the user
    tempFile = restoreFile(file,version)
    os.system("cp %s %s" % (tempFile, file))
    os.system("rm %s" % tempFile)

    print "Synced version %s of file %s" % (version,file)

# Find out if the file the user supplied is present in the current working branch
# Prints out the commit messages if the file is present
# arguments supplied are all files
# Args: A list of strings files
def log(args):
    if len(args) < 1:
        sys.exit("Error: Log requires at least 1 file as arguments")

    for iterate in args:
        print "%s:" % iterate
        if (isUnderVC(iterate)):
            # Iterate through the .versions file in reverse order (most recent show up first)
            vcFilePath = getVcPath(iterate)
            data = readFile(os.path.join(vcFilePath, iterate+".versions"))
            count = getHeadRevision(iterate)
            for line in reversed(data):
                # Pretty Print format that the user will see
                print "r%s \"%s\"" % (str(count), line.rstrip())
                count = count - 1
        else:
            print "Warning: File \"%s\" is not under version control, skipped" % iterate
        print ""

# Copy a file into a new branch
# Args: args[0] - a string representing a filename
#       args[1] - a string of a new or currently existing branch
def branch(args):
    if len(args) != 2:
        sys.exit("Error: Branch require 2 arguments: file and branch name")

    file = args[0]
    branchName = args[1]

    if (not isUnderVC(file)):
        sys.exit("Error: Cannot branch a file that is not under version control")

    # Check if the file is pending. Only files that are commited can be branched
    pendingFiles = readFile(pendingPath)

    if (file in pendingFiles):
        sys.exit("Error: Cannot branch a file that is pending submission. Please commit before branching")

    # Access the branch file and store its value. We need this to switch back to our original branch context
    branchFile = os.path.join(vcDataDir, "branch")
    oldBranch = readFile(branchFile)[0]

    # Only allow alphanumeric branch names
    if (not branchName.isalnum()):
        sys.exit("Error: Invalid branch name \"%s\". Valid characters are alphanumeric" % branchName)

    # Create the branch directory if it does not exist 
    newBranchPath = os.path.join(vcDataDir, branchName)
    if (not os.path.isdir(newBranchPath)):
        os.makedirs(newBranchPath)

    # Change branches by setting the branch file to the user input
    writeFile(branchFile, [branchName])

    # Now that we have switched branch contexts, we can add/edit and commit the file naturally 
    # Both these functions require a list as an argument, pass the appropriate values
    if isUnderVC(file):
        edit([file])
    else:
        add([file])

    commit([file,"Branching %s from %s to %s" % (file,oldBranch,branchName)])

    # Restore to previous branch by setting branch file to previous
    writeFile(branchFile, [oldBranch])

# Prints a list of pending files (either add or edit)
# Args - N/A, not used
def status(args):
    print "The following files are pending submission:"
    pendingFiles = readFile(pendingPath)
    for file in pendingFiles:
        file = file.rstrip()
        if (isUnderVC(file)):
            print "\t E " + file
        else:
            print "\t A " + file

# This function initalizes the vc by creating the hidden folder for revision data
# Args: empty
def setup():
    if initialized():
        sys.exit("This directory is already under version control")
    else:
        os.makedirs(".vc_data")
        os.makedirs(".vc_data/main")
        
    #current branch we are working on by default is called the main
    writeFile(".vc_data/branch", ["main"])
    writeFile(".vc_data/pending", [])

# Switches the current branch to the specified branch only if it exists
# Args - args[0]: A string representing a valid branch name
def switchbranch(args):
    if len(args) != 1:
        sys.exit("Error: switchbranch requires 1 argument")

    # Ensure that the pending file is empty in order to allow this to work
    pendingPath = os.path.join(vcDataDir, "pending")
    pendingList = readFile(pendingPath)
    if (pendingList):
        sys.exit("Error: Files are still pending for commit. Commit your changes to prevent data loss")

    branch = args[0]
    branchDir = os.path.join(vcDataDir, branch)
    # Check that the branch specified exists
    if (not os.path.isdir(branchDir) == True):
        sys.exit("Error: The branch specified does not exist in the repository")

    # Before switching, we need to remove all versioned files in the user's workspace
    currentBranch = currentWorkingBranch()
    currentBranchDir = os.path.join(vcDataDir, currentBranch)
    versionedFiles = os.listdir(currentBranchDir)

    for vFile in versionedFiles:
        # vFile will be all the versioned filenames in the current user directory,
        # we can directly remove them
        os.system("rm %s " % vFile)

    # Change the branch file to the branch the user specified
    writeFile(os.path.join(vcDataDir,"branch"), [branch])

    # Sync all the files to HEAD
    currentBranch = currentWorkingBranch()
    currentBranchDir = os.path.join(vcDataDir, currentBranch)
    versionedFiles = os.listdir(currentBranchDir)

    for vFile in versionedFiles:
        # vFile will be all the versioned filenames that exist 
        # we can sync them to head directly
        sync([vFile, "HEAD"])
    print "Current branch %r is now in use" % branch

# Tries to suggest the next iteration of a file in branch "destination",
# given the last change applied to that file in branch "source"
# Args: args[0] - the file
#       args[1] - source branch
#       args[1] - destination branch
def suggest(args):
    # Format is python vc.py suggest fileName BranchSuggestFrom BranchSuggestTo
    if len(args) != 3:
        sys.exit("Error: suggest requires 3 arguments")

    # Setup for doing checks
    fileName   = args[0]
    branchFrom = args[1]
    branchTo   = args[2]

    # Access the branch file and store its value. We need this to switch back to our original branch context
    branchFile = os.path.join(vcDataDir, "branch")
    oldBranch = readFile(branchFile)[0]

    # call switchbranch - this will take care of checking if files are on pending list
    # this will verify if both branches exist
    switchlist = []
    switchlist.append(branchTo)
    switchbranch(switchlist)
     
    # check if file exists in this branch
    if (not isUnderVC(fileName)):
        # Restore the user's original branch
        switchbranch([oldBranch])
        sys.exit("Error: File \"%s\" is not under version control in branch %r" % (fileName, branchTo))

    headRevision = getHeadRevision(fileName)
    headFileBranchTo = restoreFile(fileName, headRevision)

    switchlist = []
    switchlist.append(branchFrom)
    switchbranch(switchlist)

    # check if file exists in this branch
    if (not isUnderVC(fileName)):
        # Restore the user's original branch, cleanup temp file
        os.system("rm %s" % headFileBranchTo)
        switchbranch([oldBranch])
        sys.exit("Error: File \"%s\" is not under version control in branch %r" % (fileName, branchFrom))  


    # Get the path to the head revision of fileName in branchFrom
    headRevision = getHeadRevision(fileName)

    if (headRevision == 1):
        # Restore the user's original branch, cleanup temp file
        os.system("rm %s" % headFileBranchTo)
        switchbranch([oldBranch])
        sys.exit("Error: File %r only has 1 revision in branch %r. Suggest requires at least 2 revisions" % (fileName, branchFrom))

    headFileBranchFrom = restoreFile(fileName, headRevision)
    parentFileBranchFrom = restoreFile(fileName, headRevision - 1)

    # All temporary files that are needed to do the suggest
    # have been created at this point. Let us perform the
    # 3-way merge algorithm to make the suggestion
    # Read all files in the way the 3-way merge algorithm expects
    fileFromHEAD =        readFile(headFileBranchFrom)
    fileFromAncestor =    readFile(parentFileBranchFrom)
    fileToHEAD =      readFile(headFileBranchTo)

    hadConflicts = 0
    (hadConflicts, result) = mergeFiles(fileFromHEAD,fileFromAncestor,fileToHEAD)

    if (hadConflicts > 0):
        print "Warning: Conflicts encountered! Please refer to suggest file"

    # New line strip procedure so we can use writeFile
    fileData  = []
    for iterate in result:
        fileData.append(iterate.rstrip("\n"))        

    writeFile(os.path.join(os.getcwd(), fileName+".suggest"), fileData)
    print "Message: %s has been generated in your current working directory" % (fileName+".suggest")

    # Cleanup temp files
    os.system("rm %s" % headFileBranchTo)
    os.system("rm %s" % headFileBranchFrom)
    os.system("rm %s" % parentFileBranchFrom)

    switchlist = []
    switchlist.append(oldBranch)
    switchbranch(switchlist)
    # and branchTo's HEAD
    return 0

#######################################################
###############  COMMAND MAP   ########################
#######################################################

# Contains all functions for users
commandMap = {
    "setup"         : setup,        # Done
    "status"        : status,       # Done
    "add"           : add,          # Done
    "edit"          : edit,         # Done
    "commit"        : commit,       # Done
    "sync"          : sync,         # Done
    "log"           : log,          # Done
    "branch"        : branch,       # Done
    "switchbranch"  : switchbranch, # DONE 
    "suggest"       : suggest       # DONE
}

#######################################################
###################  MAIN  ############################
#######################################################

def main():
    # User must specify at least 1 command: vc.py <COMMAND>
    if len(sys.argv) < 2:
        sys.exit("Error - Usage: %s <COMMAND> <ARGS>" % sys.argv[0])
    
    # Store user's command
    cmd = sys.argv[1]
    
    if cmd == "setup":
        # Create the hidden data directory to store all repo information
        setup()
    elif cmd in commandMap:
        # User gave a valid command, check if the repo is initalized
        # If it is, setup path environment variables
        if (initialized()):
            # Repo is initalized, execute the command
            commandMap[cmd](sys.argv[2:])
        else:
            sys.exit("Error: This directory does not belong to a repo")
    else:
        validCmds = "\n\t".join(commandMap.keys())
        sys.exit("Error - No such command: %s\nValid Commands:\n\t%s" % (sys.argv[1], validCmds))

if __name__ == "__main__":
    main()
