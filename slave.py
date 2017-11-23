import grpc
import replicator_pb2
import rocksdb

PORT = 3000

class Slave():
    def __init__(self, host='0.0.0.0', port=PORT):
        self.db = rocksdb.DB("slave.db", rocksdb.Options(create_if_missing=True))
        self.channel = grpc.insecure_channel('%s:%d' % (host, port))
        self.stub = replicator_pb2.ReplicatorStub(self.channel)

    def register(self):
        responses = self.stub.replicate(replicator_pb2.ReplicationRequest(clientID="1"))
        print("Connected!")
        
        for response in responses:
            if response.operation == 'put':
                print("Put to slave db "+ response.key+" , "+ response.value)
                self.db.put(response.key.encode(), response.value.encode())
            else:
                print("Delete to slave db "+ response.key+" , "+ response.value)
                self.db.delete(response.key.encode())
            
def run():
    slave = Slave()
    slave.register()

if __name__ == "__main__":
    run()

