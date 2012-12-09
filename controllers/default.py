# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

def index():
    if not request.args:
        rides = db().select(db.ride.ALL)
    elif request.args[0] == "1":
        rides = db().select(db.ride.ALL, orderby=db.ride.destination)
    elif request.args[0] == "2":
        rides = db().select(db.ride.ALL, orderby=db.ride.meeting_location)
    elif request.args[0] == "3":
        rides = db().select(db.ride.ALL, orderby=db.ride.departure_time)
    elif request.args[0] == "4":
        rides = db().select(db.ride.ALL, orderby=db.ride.price)
    elif request.args[0] == "5":
        rides = db().select(db.ride.ALL, orderby=db.ride.number_of_seats_open)
    else:
        rides = db().select(db.ride.ALL)
    return dict(ride=rides)

@auth.requires_login()
def add():
    form = SQLFORM(db.ride)
    if form.process().accepted:
        redirect(URL('index'))
    return dict(form=form)

@auth.requires_login()
def add_comment():
    rides = db.ride(request.args[0]) or redirect(URL('index'))
    user = db.auth_user(auth.user_id) or redirect(URL('index'))
    form = SQLFORM.factory(
    Field('comment', 'text', requires=IS_NOT_EMPTY())
    )
    if form.process().accepted:
        rides.update_record(comments = rides.comments + 'From: ' + str(user.first_name) + ' ' + str(user.last_name) + ':\n' + form.vars.comment + '----------\n') 
        redirect(URL('view', args=[rides.id])) 
    return dict(rides=rides, user_id = auth.user_id, form = form, sesion=session)

@auth.requires_login()
def join_ride():
    user = db.auth_user(auth.user_id) or redirect(URL('index'))
    ride = db.ride(request.args(0)) or redirect(URL('index'))
    for u in ride.riders:
        if( auth.user_id == u.id):
            session.flash = T("You are already in this ride!")
            redirect(URL('view', args=[ride.id]))

    if (ride.number_of_seats_open <= 0):
        session.flash = T("This ride has no open seats!")
        redirect(URL('view', args=[ride.id]))

    mail.send(str(ride.owner.email),
      'UCSC Rideshare automated message',
      'Hello ' + str(ride.owner.first_name)+",\n"+ " " + str(user.first_name) + " " + str(user.last_name) + ' has joined your ride going to ' + str(ride.destination) + ' from ' +str(ride.meeting_location) + ' on ' + str(ride.departure_date))
      
    session.flash = T(str(ride.owner.email))  
    ride.riders.append(user)  
    db.ride[ride.id] = dict(number_of_seats_open = ride.number_of_seats_open - 1)
    db.ride[ride.id] = dict(riders = ride.riders)
    redirect(URL('view', args=[ride.id]))
    return dict()


@auth.requires_login()
def leave_ride():
    user = db.auth_user(auth.user_id) or redirect(URL('index'))
    ride = db.ride(request.args(0)) or redirect(URL('index'))
    if(ride.owner.id == auth.user_id):
        session.flash = T("You cannot leave your own ride! Please delete this ride.")
        redirect(URL('view', args=[ride.id]))
      
    ride.riders.remove(user.id)
    mail.send(str(ride.owner.email),
      'UCSC Rideshare automated message',
           'Hello ' + str(ride.owner.first_name)+",\n"+ " " + str(user.first_name) + " " + str(user.last_name) + ' has left your ride going to ' + str(ride.destination) + ' from ' +str(ride.meeting_location) + ' on ' + str(ride.departure_date))
    db.ride[ride.id] = dict(number_of_seats_open = ride.number_of_seats_open + 1)
    db.ride[ride.id] = dict(riders = ride.riders)      
    redirect(URL('view', args=[ride.id]))
    return dict()


def kick_rider():
    user = db.auth_user(request.args(0)) or redirect(URL('index'))
    session.flash = T("saaaaaaaadddddddddddd")
    ride = db.ride(request.args(1)) or redirect(URL('index'))
    if(auth.user_id != ride.owner.id):
             session.flash = T("You cannot remove people from rides you do not own. Your account has been flagged.")
             redirect(URL('view', args=[ride.id]))
    
    ride.riders.remove(user.id)
    db.ride[ride.id] = dict(number_of_seats_open = ride.number_of_seats_open + 1)
    db.ride[ride.id] = dict(riders = ride.riders)
    session.flash = T("User " + str(user.first_name) + " " + str(user.last_name) + " has been removed from this ride.")
    redirect(URL('view', args=[ride.id]))
    return dict()
             
        
def view():
    rides = db.ride(request.args[0]) or redirect(URL('index'))
    return dict(ride=rides, user_id = auth.user_id)

        
@auth.requires_login()
def view_user():
     user = db.auth_user(request.args[0]) or redirect(URL('index'))
     return dict(user = user)


def download(): return response.download(request,db)


@auth.requires_login()
def delete():
    ride = db.ride(request.args[0]) or redirect(URL('index'))
    
    if auth.user_id != ride.owner.id:
        session.flash = T("You cannot delete other people's rides!")
        redirect(URL('index'))
        
    form = SQLFORM.factory(Field('Confirm_deletion', 'boolean', default=False))
    if form.process().accepted:
        db(db.ride.id == request.args[0]).delete()
        db.commit()
        session.flash = T('The item has been deleted')
        redirect(URL('index'))
    return dict(form=form, ride=ride, user=auth.user)

                            
@auth.requires_login()
def update():
    user = db.auth_user(auth.user_id) or redirect(URL('index'))
    record = db.ride(request.args(0)) or redirect(URL('index'))
    form = SQLFORM(db.ride, record)
    if form.process().accepted:
        #for riders in record:
            mail.send(str(user.email),
            'UCSC Rideshare automated message',
            'Hello ' + str(user.first_name)+",\n" + str(record.owner.first_name) + " " + str(record.owner.last_name) + ' has updated your ride')
            session.flash = T('The item has been updated.')
            redirect(URL('index'))
        
  
    return dict(form=form)                
                                   
    
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
