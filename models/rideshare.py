# coding: utf8
                
db.define_table('ride',
                Field('meeting_location', 'string', requires=IS_NOT_EMPTY()),
                Field('destination', 'string', requires=IS_NOT_EMPTY()),
                Field('departure_date', 'date', requires=IS_DATE()),
                Field('departure_time', 'time', requires=IS_TIME()),
                Field('trip_length', 'string'),
                Field('comments', 'text', default=""),
                Field('user_comments', 'list:string', default=[]),
                Field('price', 'string'),
                Field('riders', 'list:reference auth_user', default=auth.user_id),
                Field('number_of_seats_open', 'integer', requires=IS_IN_SET(['0', '1', '2','3','4','5'])),
                Field('owner', db.auth_user, default=auth.user_id))

db.ride.riders.writable = db.ride.riders.readable = False
db.ride.user_comments.readable = db.ride.user_comments.writable= False
db.ride.owner.writable = db.ride.owner.readable = False
db.ride.id.readable = db.ride.id.writable = False
