import web
import json
import twilio.twiml
from twilio.rest import TwilioRestClient
from pymongo import MongoClient
import spotify
from config import Config
import json

urls = (
    "/new_song", "new_song",
    "/fetch_songs", "fetch_songs",
    "/yes_song", "yes_song",
    "/no_song", "no_song"
)

mongo_client = MongoClient("127.0.0.1", 27017)
djone = mongo_client.djone
djs = djone.djs

twilio_client = TwilioRestClient(Config.ssid, Config.auth)

class yes_song:

    def GET(self):

        message = twilio_client.messages.create(to="+17328950910", from_="+17323911722", body="Your song was added to the playlist! ")

class no_song:
    def GET(self):

        message = twilio_client.messages.create(to="+17328950910", from_="+17323911722", body="Your song wasn't accepted to be on the playlist! ")

class fetch_songs:

    def GET(self):

        web.header("Content-Type", "application/json")
        web.header("Access-Control-Allow-Origin", "*")

        document = djs.find_one({"dj": "+17323911722"})

        new_document = {"dj": document["dj"], "queue": []}
        djs.remove(document)
        djs.insert_one(new_document)

        return json.dumps({"queue": document["queue"]})

class new_song:

    def POST(self):

        web.header("Access-Control-Allow-Origin", "*")
        data = web.input()
        query = data["Body"]
        sender = data["From"]
        dj = data["To"]

        document = djs.find_one({"dj": dj})

        if document:

            session = Config.session

            print session

            search = session.search(query).load()

            try:

                uri = str(search.tracks[0].link)
                name = search.tracks[0].name

                djs.remove({"_id": document["_id"]})
                document["queue"].append({"name": name, "uri": uri, "from": sender})
                djs.insert_one(document)

                message = twilio_client.messages.create(to=sender, from_=dj, body="Your song was submitted to the DJ!")

                print message
            except IndexError:
                message = twilio_client.messages.create(to=sender, from_=dj, body="No song like that was found!")


        else:
            message = twilio_client.messages.create(to=sender, from_=dj, body="No DJ with that number was found!")


if __name__ == "__main__":

    app = web.application(urls, globals())
    app.run()
