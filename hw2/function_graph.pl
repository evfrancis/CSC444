use strict;
use warnings;

# This file was created partially as an experiment, and partially to help map out our function
# call architecture in the version control script.  It was hacked together in perl mostly out of
# interest in creating a tool that did something neat.

# This is the file we want to parse
my $inputFile = $ARGV[0];

my @file = split("\n", `cat $inputFile`);
my %functionCallMap;
my $functions = `grep 'def.*(.*)' $inputFile`; # All of our python functions are declared by "def"
my @rawFunctionData = split("\n",$functions);
my @functionNames;

# First lets extract all the function names that we defined
for my $item (@rawFunctionData) {
    if ($item =~ m/def (\w+)/) {
        push(@functionNames, $1)
    }
}

# For each function, search for it being called in the file
# We also want to know what line it is called on, so we can traverse
# up from this point to find what function is calling it
for my $calledFunction (@functionNames) {

    # Find all locations where this function was called
    my $out = `grep \"$calledFunction\(\" $inputFile -n | grep -v '[0-9]\\+:def '`;
    my @callInstances = split("\n",$out);

    for my $instance (@callInstances) {
        if ($instance =~ m/^([0-9]+):.*$calledFunction\(/) {
            # The calledFunction is being called
            my $line = $1;
            my $j = 0;

            # Backtrace to what function is calling it
            for ($j = $line; $j > 0; $j--) {
                if ($file[$j] =~ m/^def (\w+)/) {
                    my $callingFunction = $1;

                    # Create the following mapping:
                    # CallingFunction -> {..., calledFunction}
                    push(@{$functionCallMap{$callingFunction}}, $calledFunction);
                    last;
                }
            }
        }
    }
}

# Now print out our data structure to show the full mapping
for my $callingFunction (keys %functionCallMap) {
    my $prev = "";
    print "$callingFunction: \n";
    for my $calledFunction (@{$functionCallMap{$callingFunction}}) {
        # Uniquify the list as well
        if ($calledFunction ne $prev) {
            $prev = $calledFunction;
            print "\t$calledFunction\n";
        }
    }
}
