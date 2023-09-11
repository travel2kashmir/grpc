from concurrent import futures
import grpc
import time
import logging
import msg_pb2 as chat
import msg_pb2_grpc as rpc
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatServer(rpc.ChatServerServicer):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.clients = set()  # Maintain a set of connected clients

    def ChatStream(self, request, context):
        self.clients.add(context.peer())  # Add the client's address to the set
        self.notify_clients(f"Connected. Total clients: {len(self.clients)}")

        try:
            while True:
                # Continuously listen for messages
                message = yield chat.ChatMessage()
                self.logger.info(f"Received message: {message.content}")
                self.notify_clients(f"New message: {message.content}")

        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.CANCELLED:
                self.clients.remove(context.peer())
                self.notify_clients(
                    f"Disconnected. Total clients: {len(self.clients)}")

    def SendChatMessage(self, request, context):
        self.logger.info(f"Sending message: {request.content}")
        return chat.Empty()

    def notify_clients(self, message):
        for client in self.clients:
            try:
                yield chat.ChatMessage(content=message)
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.UNAVAILABLE:
                    self.clients.remove(client)
                    self.logger.info(
                        f"Client disconnected: {client}. Total clients: {len(self.clients)}")

def start_grpc_server():
    port = 11912  # A random port for the server to run on
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    rpc.add_ChatServerServicer_to_server(ChatServer(), server)
    logger.info('Starting server. Msg.proto file being used. Listening...')
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    server.wait_for_termination()
    # try:
    #     while True:
    #         time.sleep(64 * 64 * 100)
    # except KeyboardInterrupt:
    #     logger.info("Server stopped.")


if __name__ == '__main__':
    start_grpc_server()

    
# class ChatServer(rpc.ChatServerServicer):

#     def __init__(self):
#         # Create a logger instance for this class
#         self.logger = logging.getLogger(__name__)
#         self.hotel_chat_apps = {}  # Dictionary to store hotel chat apps
#         # Flag to track if the initial message has been sent
#         self.initial_message_sent = False
#         self.message_history = {} # Dictionary to store message history for each hotel

#     def ChatStream(self, request_iterator, context):

#         # Stream initial Message to clients
#         while True:
#             if not self.initial_message_sent:
#                 # Send the initial message to the client
#                 initial_message = chat.ChatMessage(
#                     from_user_id="Server", content="Connected")
#                 self.logger.info(f"Chat Server: {initial_message}")
#                 self.initial_message_sent = True
#                 yield initial_message

#             # Check if there are any new messages
#             for hotel_id, messages in self.hotel_chat_apps.items():
#                 f"{hotel_id} --> {messages}"
#                 # Check if there are new messages for the hotel
#                 if messages:
#                     print(self.hotel_chat_apps)
#                     print("=="*20)
#                     print(messages)
#                     # Yield each new message to the client
#                     for message in messages:
#                         yield message

#                         # Store the message in the message history
#                         if hotel_id not in self.message_history:
#                             self.message_history[hotel_id] = []
#                         self.message_history[hotel_id].append(message)
#                     # Clear the hotel's message queue after sending
#                     self.hotel_chat_apps[hotel_id] = []

#     def SendChatMessage(self, ChatMessage: chat.ChatMessage, context):

#         message = dict({
#             "from_user_id": ChatMessage.from_user_id,
#             "content": ChatMessage.content,
#             "to_user_id": ChatMessage.to_user_id,
#             "content_type": ChatMessage.content_type,
#             "hotel_id": ChatMessage.hotel_id,
#             "timestamp": datetime.now()
#         })

#         self.logger.info(f"Received message: {message}")

#         hotel_id = ChatMessage.hotel_id
#         if not hotel_id:
#             return chat.Empty()

#         if hotel_id not in self.hotel_chat_apps:
#             self.hotel_chat_apps[hotel_id] = []

#         self.hotel_chat_apps[hotel_id].append(message)

#         # Store the message in the message history
#         if hotel_id not in self.message_history:
#             self.message_history[hotel_id] = []

#         self.message_history[hotel_id].append(message)

#         return chat.Empty()

        # Check if there are any new messages

        # self.logger.info(f"Received message: {request.message}")
        # # Process the message and prepare a response
        # response = rpc.ChatResponse()
        # response.message = f"You said: {request.message}"
        # return response

    # class ChatServer(rpc.ChatServerServicer):

    #     def __init__(self):
    #         self.hotel_chat_apps = {}  # Dictionary to store hotel chat apps
    #         self.initial_message_sent = False  # Flag to track if initial message has been sent
    #         self.message_history = {}  # Dictionary to store message history for each hotel

    #     def ChatStream(self, request_iterator, context):
    #         # Stream new messages to clients
    #         while True:
    #             if not self.initial_message_sent:
    #                 # Send the initial message to the client
    #                 initial_message = chat.ChatMessage(from_user_id="Server", content="Connected")
    #                 self.initial_message_sent = True
    #                 yield initial_message

    #             # Check if there are any new messages
    #             for hotel_id, messages in self.hotel_chat_apps.items():
    #                 # Check if there are new messages for the hotel
    #                 if messages:
    #                     print(self.hotel_chat_apps)
    #                     print("=="*20)
    #                     print(messages)
    #                     # Yield each new message to the client
    #                     for message in messages:
    #                         yield message
    #                         # Store the message in the message history
    #                         if hotel_id not in self.message_history:
    #                             self.message_history[hotel_id] = []
    #                         self.message_history[hotel_id].append(message)
    #                     # Clear the hotel's message queue after sending
    #                     self.hotel_chat_apps[hotel_id] = []

    #     def SendChatMessage(self, ChatMessage: chat.ChatMessage, context):
    #         # Check if the hotel ID is provided in the message

    #         d = {'hotel_id': ChatMessage.hotel_id,
    #              'content':ChatMessage.content
    #              }
    #         hotel_id = ChatMessage.hotel_id
    #         if not hotel_id:
    #             return chat.Empty()  # Return an empty response or handle the error

    #         # Check if the hotel chat app exists, and if not, create one
    #         if hotel_id not in self.hotel_chat_apps:
    #             self.hotel_chat_apps[hotel_id] = []  # Create a chat app list for the hotel

    #         # Append the message to the chat app of the specified hotel
    #         # msg=f"{request.hotel_id}::{request.from_user_id}::{request.to_user_id}::{request.content}"

    #         # self.hotel_chat_apps[hotel_id].append(msg)
    #         self.hotel_chat_apps[hotel_id].append(ChatMessage)

    #         # Store the message in the message history
    #         if hotel_id not in self.message_history:
    #             self.message_history[hotel_id] = []

    #         # self.message_history[hotel_id].append(msg)
    #         self.message_history[hotel_id].append(d)

    #         print(f"Received message for Hotel {hotel_id}: {ChatMessage.content}")

    #         #   # Print the chat messages for debugging
    #         # print(f"Chat Messages for Hotel {hotel_id}:")

    #         # for message in self.message_history[hotel_id]:
    #         #     print(f" {message.from_user_id}: {message.content}")

    #         # print("hotel chats ",self.hotel_chat_apps)
    #         # print("message history ",self.message_history)

    #         return chat.Empty()

    # if __name__ == '__main__':
    #     port = 11912  # a random port for the server to run on
    #     server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    #     rpc.add_ChatServerServicer_to_server(ChatServer(), server)
    #     print('Starting server. Msg.proto file being used. Listening...')
    #     server.add_insecure_port(f'[::]:{port}')
    #     server.start()
    #     while True:
    #         time.sleep(64 * 64 * 100)


def start_grpc_server():
    port = 11912  # A random port for the server to run on
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    rpc.add_ChatServerServicer_to_server(ChatServer(), server)
    logger.info('Starting server. Msg.proto file being used. Listening...')
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    server.wait_for_termination()
    # try:
    #     while True:
    #         time.sleep(64 * 64 * 100)
    # except KeyboardInterrupt:
    #     logger.info("Server stopped.")


if __name__ == '__main__':
    start_grpc_server()
