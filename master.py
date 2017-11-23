import time
import grpc
import replicator_pb2
import replicator_pb2_grpc
import queue
import rocksdb

from concurrent import futures

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

class MyReplicatorServicer(replicator_pb2.ReplicatorServicer):
    def __init__(self):
        self.db = rocksdb.DB("master.db", rocksdb.Options(create_if_missing=True))
        self.queue = queue.Queue()

    def replicator(func):
        def wrapper(self, request, context):
             
            self.queue.put(replicator_pb2.ReplicationResponse(
                    operation=func.__name__, 
                    key=request.key.encode(), 
                    value=request.value.encode()
                 ))
            
            return func(self, request, context)
        return wrapper

    @replicator
    def put(self, request, context):
        print("Put to master"+request.key +"," +request.value)
        self.db.put(request.key.encode(), request.value.encode())
        return replicator_pb2.Response(value='Done')

    @replicator
    def delete(self, request, context):
        print("Delete from master"+request.key)
        self.db.delete(request.key.encode())
        return replicator_pb2.Response(value='Done')
        
    def get(self, request, context):
        print("Get from master db"+request.key)
        value = self.db.get(request.key.encode())
        return replicator_pb2.Response(value=value)


    def replicate(self, request, context):
        while True:
            operation = self.queue.get()
            print("Send "+operation.operation+" "+operation.key+ " "+ operation.value)
            yield operation

def run(host, port):
    '''
    Run the GRPC server
    '''
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    replicator_pb2_grpc.add_ReplicatorServicer_to_server(MyReplicatorServicer(), server)
    server.add_insecure_port('%s:%d' % (host, port))
    server.start()

    try:
        while True:
            print("Server started at...%d" % port)
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    run('0.0.0.0', 3000)
