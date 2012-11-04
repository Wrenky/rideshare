# coding: utf8

sexes = "male", "female"

db.define_table('people',
                Field('name', 'string', requires = 'string'),
                Field('aboutMe', 'string', requires = 'string'),
                Field('email', 'string'),
                Field('sex', requires = IS_IN_SET(sexes, error_message='Please pick a sex')),
                Field('age', 'integer', requires = 'integer'))
                
db.define_table('ride',
                Field('meeting_location', 'string'),
                Field('destination', 'string'),
                Field('departure_time', 'string'),
                Field('trip_length', 'string'),
                Field('completed', 'string'),
                Field('comments', 'text'),
                Field('price', 'string'),
                Field('number_of_seats_open'),
                Field('owner', db.auth_user, default=auth.user_id))
                
db.ride.completed.writable = db.ride.completed.readable = False
db.ride.owner.writable = db.ride.owner.readable = False
