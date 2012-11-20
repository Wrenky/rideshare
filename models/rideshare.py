# coding: utf8
                
db.define_table('ride',
                Field('meeting_location', 'string', requires=IS_NOT_EMPTY()),
                Field('destination', 'string', requires=IS_NOT_EMPTY()),
                Field('departure_time'),
                Field('trip_length'),
                Field('completed'),
                Field('comments', 'text'),
                Field('price'),
                Field('number_of_seats_open', requires=IS_IN_SET(['0', '1', '2','3','4','5'])),
                Field('owner', db.auth_user, default=auth.user_id))
                            
db.ride.completed.writable = db.ride.completed.readable = False
db.ride.owner.writable = db.ride.owner.readable = False
