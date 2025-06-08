import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 1337))
server.listen(1)

while True:
    client, client_address = server.accept()
    
    try:
        print(f"Connected to client: {client_address}")
        
        # Receive and send data
        while True:
            data = client.recv(1024)
            if not data:
                break
            print(f"Received: {data.decode('utf-8')}")
            client.send(data) 
    except Exception as e:
        pass
    finally:
        # Clean up the connection
        client.close()
