import grpc
import replicator_pb2

PORT = 3000

class PumpData():
    def __init__(self, host='0.0.0.0', port=PORT):
        self.channel = grpc.insecure_channel('%s:%d' % (host, port))
        self.stub = replicator_pb2.ReplicatorStub(self.channel)

    def put(self, key, value):
        return self.stub.put(replicator_pb2.Request(key=key, value=value))

    def delete(self, key):
        return self.stub.delete(replicator_pb2.Request(key=key))

def main():
    pump = PumpData()
    
    for i in range(0, 3):
        print("Put on server: "+str(i)+","+str(i))
        response = pump.put(str(i), str(i))
        print(response.value)
        print("Delete from server: " +str(i))
        response = pump.delete(str(i))
        print(response.value) 

if __name__ == "__main__":
    main()
