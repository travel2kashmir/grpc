import grpc
import msg_pb2 as chat
import msg_pb2_grpc as rpc

def send_message():
    channel = grpc.insecure_channel('localhost:11912')  # Replace with your server address and port
    client = rpc.ChatServerStub(channel)

    while True:
        content = input("Enter your message: ")
        if not content:
            continue  # Skip empty messages

        to_user_id = input("Enter recipient user ID (or press Enter to send to all): ")
        message = chat.ChatMessage(
            from_user_id="YourUserID",  # Replace with your user ID
            to_user_id=to_user_id if to_user_id else '',  # Empty if not specified
            content=content,
        )

        response = client.SendChatMessage(message)
        print("Message sent successfully!")

if __name__ == '__main__':
    send_message()
