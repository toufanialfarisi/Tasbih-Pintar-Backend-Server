from flask import Flask, request, jsonify, json
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
import random


app = Flask(__name__)
db = SQLAlchemy(app)
marshal = Marshmallow(app)


basedir = os.path.dirname(os.path.abspath(__file__))
db_file = "sqlite:///" + os.path.join(basedir, "db.sqlite")

app.config["SQLALCHEMY_DATABASE_URI"] = db_file

api = Api(app)
CORS(app)


class BackendModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gambar = db.Column(db.String(100))
    keterangan = db.Column(db.String(100))
    nama_dzikir = db.Column(db.String(100))

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except:
            return False

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except:
            return False


db.create_all()


class BackendSchema(marshal.ModelSchema):
    class Meta:
        model = BackendModel


backendMarshal = BackendSchema(many=True)


class BackendServer(Resource):
    def get(self, gambar, keterangan):
        try:
            gambar = str(gambar)
            keterangan = str(keterangan)
            query = BackendModel(gambar=gambar, keterangan=keterangan)
            db.session.add(query)
            db.session.commit()
            return {"msg": "data berhasil dimasukkan"}
        except:
            return {"msg": "gagal memasukan data"}


def fixFileName(filename):
    filename = str(filename)
    out = filename.split(" ")
    out = "_".join(out)
    return out


def randomKey():
    out = random.randint(0, 1000)
    out = str(out)
    return out


def uploadImage(dataFile):
    mode = os.getenv("MODE")
    if mode == "development":
        server = "http://localhost"
    else:
        server = "https://tasbih-pintar-backend-server.herokuapp.com"
    randomName = randomKey()
    imgName = fixFileName(dataFile.filename)
    img = dataFile.save(os.path.join("static", "images", randomName + "_" + imgName))
    server = str(server)
    dataToSave = server + "/static/images/" + randomName + "_" + imgName
    return dataToSave


class BackendDataParser(Resource):
    def get(self):
        output = BackendModel.query.all()
        out = backendMarshal.dump(output)
        return {"data": out}, 200

    def post(self):
        dataKeterangan = request.form["keterangan"]
        dataNamaDzikir = request.form["nama_dzikir"]
        dataFile = request.files["gambar"]
        img = uploadImage(dataFile)
        model = BackendModel()
        model.gambar = img
        model.keterangan = dataKeterangan
        model.nama_dzikir = dataNamaDzikir
        model.save()
        return {"msg": "Data berhasil masuk"}, 200

    def delete(self):
        query = BackendModel.query.all()
        for data in query:
            db.session.delete(data)
            db.session.commit()
            out = data.gambar.split("/")[-1]
            img = os.path.join("static", "images", out)
            if os.path.exists(img):
                os.remove(img)

        return {"msg": "Data berhasil dihapus"}, 200


class BackendDataParserId(Resource):
    def delete(self, id):
        query = BackendModel.query.get(id)

        out = query.gambar.split("/")[-1]
        img = os.path.join("static", "images", out)
        if os.path.exists(img):
            os.remove(img)

        db.session.delete(query)
        db.session.commit()

        return {"msg": "data berhasil dihapus"}, 200


api.add_resource(BackendDataParser, "/api", methods=["GET", "POST", "DELETE"])
api.add_resource(BackendDataParserId, "/api/<id>", methods=["DELETE"])


if __name__ == "__main__":
    app.run(debug=True, port=5001)
