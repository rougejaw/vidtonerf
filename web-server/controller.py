import argparse
import os
from pickle import TRUE
#import magic
from uuid import uuid4, UUID
import threading

from flask import Flask, request, make_response, send_file, send_from_directory, url_for

from models.scene import UserManager
from services.scene_service import ClientService

def is_valid_uuid(value):
    try:
        UUID(str(value))
        return True
    except ValueError:
        return False

class WebServer:
    def __init__(self, flaskip, args: argparse.Namespace, cserv: ClientService) -> None:
        self.flaskip = flaskip
        self.app = Flask(__name__)
        self.args = args
        self.cservice = cserv
        self.user_manager=UserManager()

    def run(self) -> None:
        self.app.logger.setLevel(
            int(self.args.log)
        ) if self.args.log.isdecimal() else self.app.logger.setLevel(self.args.log)

        self.add_routes()
        
        # TODO: Change this to work based on where Flask server starts. Also, use the actual ip address
        ### self.sserv.base_url = request.remote_addr

        self.app.run(host=self.flaskip,port=self.args.port)

    def add_routes(self) -> None:

        #TODO: Write error handling so the whole server doesn't crash when the user sends incorrect data.



        @self.app.route("/video", methods=["POST", "PUT"])
        def recv_video():
            video_file = request.files.get("file")
            if video_file is None:
                return make_response("No video file provided", 400)
            
            uuid = str(uuid4()) #still using uuid4 despite the fact it might not be the best

            if not self.cservice.is_supported_format(video_file):
                return make_response("Unsupported video format", 415)
            threading.Thread(target=self.cservice.process_video, args=(video_file, uuid)).start() #IF EVERYTHING SUDDENLY BREAKS THIS IS WHY
            self.cservice.store_video_status(uuid, "Processing")

            response = make_response(uuid)
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response

        @self.app.route("/video/<vidid>", methods=["GET"])
        def send_video(vidid: str):
            # TODO: Change routing to serve rendered videos
            try:
                if(is_valid_uuid(vidid)):
                    path = os.path.join(os.getcwd(), "data/raw/videos/" + vidid + ".mp4")
                    response = make_response(send_file(path, as_attachment=True))
                else:
                    response = make_response("Error: invalid UUID")
            except Exception as e:
                print(e)
                response = make_response("Error: does not exist")
           
            return response
            
        @self.app.route("/nerfvideo/<vidid>", methods=["GET"])
        def send_nerf_video(vidid: str):
            ospath = None
            status_str = "Processing"
            if is_valid_uuid(vidid):
                ospath = self.cservice.get_nerf_video_path(vidid)
            # Could change this to return both
            if ospath == None or not os.path.exists(ospath):
                response = make_response(status_str)
            else:
                status_str = "Video ready"
                response = make_response(send_file(ospath, as_attachment=True))
                
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response

        @self.app.route("/worker-data/<path:path>")
        def send_worker_data(path):
            # serves data directory for workers to pull any local data
            # TODO make this access secure
            return send_from_directory('data',path[5:])
            
        @self.app.route("/login", methods=["GET"])
        def login_user():
            #get username and password from login 
            #use get_user_by_username and compare the password retrieved from that to the password given by the login
            #if they match allow the user to login, otherwise, fail

            username=request.form["username"]
            password=request.form["password"]

            user=self.user_manager.get_user_by_username(username)
            if user==None:
                string=f"INCORRECT USERNAME|{user.id}"
                response=make_response(string)
                return response

            if user.password == password:
                string=f"SUCCESS|{user.id}"
                response=make_response(string)
                return response
            else:
                string=f"INCORRECT PASSWORD|{user.id}"
                response=make_response(string)
                return response



        @self.app.route("/register", methods=["POST"])
        def register_user():
            #get username and password from register
            #use set_user
            #if it doesnt fail, youre all good


            username=request.form["username"]
            password=request.form["password"]

            user=self.user_manager.generate_user(username,password)

            if user==1:
                string=f"USERNAME CONFLICT|{user.id}"
                response=make_response(string)
                return response
            if user==None:
                raise Exception('Unknown error when generating user')



            string=f"SUCCESS|{user.id}"
            response=make_response(string)
            return response

        @self.app.route("/test")
        def test_endpoint():
            
            return "Success!"

