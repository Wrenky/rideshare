# coding: utf8

db.define_table('people',
                Field('name', requires = 'string'),
                Field('aboutMe', requires = 'string'),
                Field('email'),
                Field('sex', requires = 'string'),
                Field('age', requires = 'integer'))
                
db.define_table('ride',
                Field('meeting_location'),
                Field('destination'),
                Field('departure_time'),
                Field('trip_length'),
                Field('completed'),
                Field('comments'),
                Field('price'),
                Field('number_of_seats_open'),
                Field('owner', db.auth_user, default=auth.user_id))
                
db.ride.completed.writable = db.ride.completed.readable = False
db.ride.owner.writable = db.ride.owner.readable = False
