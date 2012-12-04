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
    elif request.args[0] == 1:
        rides = db().select(db.ride.ALL, orderby=db.ride.destination)
    elif request.args[0] == 2:
        rides = db().select(db.ride.ALL, orderby=db.ride.meeting_location)
    elif request.args[0] == 3:
        rides = db().select(db.ride.ALL, orderby=db.ride.departure_time)
    elif request.args[0] == 4:
        rides = db().select(db.ride.ALL, orderby=db.ride.price)
    else:
        rides = db().select(db.ride.ALL)
    return dict(ride=rides)

@auth.requires_login()
def add():
    form = SQLFORM(db.ride)
    if form.process().accepted:
        session.flash = T('inserted!')
        redirect(URL('index'))
##    else:
##        session.flash = T('Didnt work- Try again')
##        redirect(URL('index'))
    return dict(form=form)

        
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
    record = db.ride(request.args(0)) or redirect(URL('index'))
    form = SQLFORM(db.ride, record)
    if form.process().accepted:
        session.flash = T('The item has been deleted')
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
