from concurrent import futures
import grpc
import time
import logging
import msg_pb2 as chat
import msg_pb2_grpc as rpc
import uuid  # Import the uuid module for generating unique user IDs
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatServer(rpc.ChatServerServicer):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.connected_users = {}  # Dictionary to map user IDs to client addresses
        self.message_history = []  # List to store chat messages
        self.message_condition = threading.Condition()  # Condition variable for new messages

    def generate_user_id(self):
        return str(uuid.uuid4())

    def ChatStream(self, request, context):
        user_id = self.generate_user_id()  # Generate a unique user ID for the connected client
        client_address = context.peer()

        if user_id in self.connected_users:
            self.logger.info(f"User {user_id} is already connected.")
        else:
            self.connected_users[user_id] = client_address  # Map the user ID to the client's address
            self.notify_clients(f"User {user_id} connected. Total users: {len(self.connected_users)}")

            yield chat.ChatMessage(
                from_user_id="Server", content="Connected", hotel_id="Connected"
            )
        try:
            while True:
                # Continuously listen for messages
                with self.message_condition:
                    self.message_condition.wait()  # Sleep until a new message arrives

                # Once awakened, check for new messages
                if self.has_new_messages():
                    message = self.get_new_message()
                    self.logger.info(f"Received message from User {user_id}: {message.content}")

                    # Add the message to the message history
                    self.message_history.append(message)

                    # Notify all connected clients about the new message
                    self.notify_clients(f"New message from User {user_id}: {message.content}")

        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.CANCELLED:
                if disconnected_user_id := next(
                    (
                        user
                        for user, address in self.connected_users.items()
                        if address == client_address
                    ),
                    None,
                ):
                    del self.connected_users[disconnected_user_id]
                    self.notify_clients(
                        f"User {disconnected_user_id} disconnected. Total users: {len(self.connected_users)}")

    def SendChatMessage(self, request, context):
        client_address = context.peer()
        if user_id := next(
            (
                user
                for user, address in self.connected_users.items()
                if address == client_address
            ),
            None,
        ):
            self.logger.info(f"Sending message from User {user_id}: {request.content}")

            if request and request.content:  # Check if the sent message is not None and has content
                # Add the sent message to the message history
                self.message_history.append(request)

                # Notify all connected clients about the sent message
                self.notify_clients(f"New message from User {user_id}: {request.content}")

                # Notify the ChatStream to wake up and check for new messages
                with self.message_condition:
                    self.message_condition.notify_all()

        return chat.Empty()

    def notify_clients(self, message):
        for client_address in self.connected_users.values():
            try:
                yield chat.ChatMessage(content=message, from_user_id="Server")
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.UNAVAILABLE:
                    if disconnected_user_id := next(
                        (
                            user
                            for user, address in self.connected_users.items()
                            if address == client_address
                        ),
                        None,
                    ):
                        del self.connected_users[disconnected_user_id]
                        self.logger.info(
                            f"User {disconnected_user_id} disconnected. Total users: {len(self.connected_users)}")

    def has_new_messages(self):
        return len(self.message_history) > 0

    def get_new_message(self):
        if self.has_new_messages():
            return self.message_history.pop(0)

def start_grpc_server():
    port = 11912  # A random port for the server to run on
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    rpc.add_ChatServerServicer_to_server(ChatServer(), server)
    logger.info('Starting server. Chat.proto file being used. Listening...')
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    try:
        while True:
            time.sleep(86400)  # Sleep for a day (86400 seconds)
    except KeyboardInterrupt:
        logger.info("Server stopped.")

if __name__ == '__main__':
    start_grpc_server()
