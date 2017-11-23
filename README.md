# Replicator

### Generate the stubs using the proto file
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ./replicator.proto


### Run the master
python master.py 


### Run the slave.
python slaver.py


### Pump data into server which will be replicated to the slave
python test.py





