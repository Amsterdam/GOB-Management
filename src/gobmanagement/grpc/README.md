# gRPC

The ```grpc``` directory contains three main subdirectories: ```out```,
```protos``` and ```services```, plus a ```codegen.py``` file in the
root.

The ```out``` and ```protos``` directory contain files that are
generated by ```codegen.py```.  The proto file in the ```protos```
directory is generated from the StartCommands defined in GOB Core.
From that, the Python skeleton code in ```out``` is generated using the
gRPC proto compiler.

The ```services``` directory contains our implementation.

## Running codegen.py
```codegen.py``` only needs to be run after the a change is made in the
start commands. The ```build.sh``` in the ```src``` root includes a call
to this file.

## Other languages (such as JS)
To generate skeleton code for other languages such as JavaScript, use
the generated ```*.proto``` file in the ```protos``` directory.



