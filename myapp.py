from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, ValidationError
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
db = SQLAlchemy(app)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Note %r>' % self.title

class NoteSchema(Schema): # Dùng phương thức xác thực với schema
    id = fields.Integer(dump_only=True)
    title = fields.String(required=True)
    content = fields.String(required=True)
    created_at = fields.DateTime(dump_only=True)

# Create Note
@app.route('/notes', methods=['POST'])
def create_note():
    try:
        note_schema = NoteSchema()
        note = note_schema.load(request.json, session=db.session)
        db.session.add(note)#Them data vao session
        db.session.commit()#Luu data
        return jsonify({'message': 'Note created successfully!'})#Trả Về Thông Báo Dạng JSON
    except ValidationError as e:
        return jsonify({'message': str(e)}), 400

# Lấy Hết Tất cả Bài Viết
@app.route('/notes', methods=['GET'])
def get_notes():
    notes = Note.query.all()
    note_schema = NoteSchema(many=True)
    result = note_schema.dump(notes)
    return jsonify(result)

# Lấy 1 bài Viết
@app.route('/notes/<int:id>', methods=['GET'])
def get_note(id):
    note = Note.query.get(id)
    if not note:
        return jsonify({'message': 'Note not found'})
    note_schema = NoteSchema()
    result = note_schema.dump(note)
    return jsonify(result)

# Update Note
@app.route('/notes/<int:id>', methods=['PUT'])# Dùng Phương Thức Put để cập nhật lại dữ liệu
def update_note(id):
    note = Note.query.get(id)
    if not note:
        return jsonify({'message': 'Note not found'})
    try:
        note_schema = NoteSchema()
        updated_note = note_schema.load(request.json, session=db.session)
        note.title = updated_note.title
        note.content = updated_note.content
        db.session.commit()
        return jsonify({'message': 'Note updated successfully!'})
    except ValidationError as e:
        return jsonify({'message': str(e)}), 400

# Delete Note
@app.route('/notes/<int:id>', methods=['DELETE'])
def delete_note(id):
    note = Note.query.get(id)#duyet danh muc tim id
    if not note:
        return jsonify({'message': 'Note not found'})
    db.session.delete(note)
    db.session.commit()
    return jsonify({'message': 'Note deleted successfully!'})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5002)
