# Run Docker
docker compose up -d

# run server file
cd server
python server.py

# run my-app
cd my-app
npm install

npm install grpc-web
npm install google-protobuf
npm start

