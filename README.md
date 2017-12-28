# motion_dec_video_stream
A motion detection software for detecting motion from web cam streams.
The code files contain a client side flask web app (app_surveillance.py) which is hosted at local address 127.0.0.1:80. This flask app accesses client's web camera on selection of the button "Start Streaming!" which then launches a web camera stream. Whenever there is motion of any object in front of the web camera the application takes a snapshot and sends it over to the server side application (server_side_app.py). At the client side the photos are stored in "imageconfig/images" folder and they are stored at the server side on "testing-images" folder.

This is a scalable application which can be modified to suit many real life usecases.

# Dependencies
python 2.7

# How to run the app

1) Run the server_side_app.py script in the terminal first.
2) Run the app_surveillance.py script next. 
3) Open web browser and go to the local address 127.0.0.1
