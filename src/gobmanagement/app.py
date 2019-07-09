import grpc

from flask import Flask
from concurrent import futures
from gobmanagement.grpc.out import jobs_pb2_grpc
from gobmanagement.grpc.services.jobs import JobsServicer

# app initialization
app = Flask(__name__)

# start gRPC server
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
jobs_pb2_grpc.add_JobsServicer_to_server(JobsServicer(), server)
server.add_insecure_port('[::]:50051')
server.start()
