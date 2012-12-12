# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Index - Handles the main sort and search ability, as well as functions 
##         as our website's main page.
##
#########################################################################
def index():
    
    #Sort is ugly because of how python rejects case-switch statements.
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
        
        
    # Search form for our search box. 
    form = SQLFORM.factory(
                  Field("search", "string", default=""),
                  formstyle='divs',
                  submit_button="Search",
                  )
    
    # NOTE: SEARCH INVALIDATES ANY SORT OPTIONS. THEY CAN'T BE USED TOGETHER.
    # If the search button is pressed, we perform a search on the strings.
    # Its an intresting way of doing things, using | to "OR" the requests 
    # together to give results. So far we search Destination, Meeting 
    # Location, Price, and the comments section. 
    if form.process().accepted:
         if (form.vars.search != "" ):
             search_terms = (form.vars.search).split()
             for i,term in enumerate(search_terms):
                 subquery=db.ride.destination.lower().like('%'+term.lower()+'%')
                 query=query|subquery if i else subquery
                 subquery=db.ride.meeting_location.lower().like('%'+term.lower()+'%')
                 query=query|subquery
                 subquery=db.ride.price.lower().like('%'+term.lower()+'%')
                 query=query|subquery
                 subquery=db.ride.comments.lower().like('%'+term.lower()+'%')
                 query=query|subquery
             rides = db(db.ride.id.belongs(db(query)._select(db.ride.id))).select()
         else:
           session.flash = T("Please enter a valid search term.")
           redirect(URL('index'))
           
    return dict(form=form, ride=rides)    




#########################################################################
## add - Adds a ride into the database. 
##
#########################################################################
@auth.requires_login()
def add():
    form = SQLFORM(db.ride)
    if form.process().accepted:
        redirect(URL('index'))
    return dict(form=form)


#########################################################################
## add_comment - Adds a comment into the ride section, appended with the
##               commenters name.
##
#########################################################################
@auth.requires_login()
def add_comment():
    ride = db.ride(request.args[0]) or redirect(URL('index'))
    user = db.auth_user(auth.user_id) or redirect(URL('index'))
    form = SQLFORM.factory(
    Field('comment', 'text', requires=IS_NOT_EMPTY())
    )
    if form.process().accepted:
        if( ride.user_comments == None): 
            ride.user_comments = [string]
            ride.update_record(user_comments = ride.user_comments)
        else:
            ride.user_comments.append(string)
            ride.update_record(user_comments = ride.user_comments)
        redirect(URL('view', args=[ride.id])) 
    return dict(rides=ride, user_id = auth.user_id, form = form, sesion=session)


#########################################################################
## join_ride - Adds the user to the ride. Sends an email to the ride 
##             owner.
##
#########################################################################
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
    ride.riders.append(user)  
    db.ride[ride.id] = dict(number_of_seats_open = ride.number_of_seats_open - 1)
    db.ride[ride.id] = dict(riders = ride.riders)
    redirect(URL('view', args=[ride.id]))
    return dict()


#########################################################################
## leave_ride - Removes the user from the ride. Sends another email.
## 
##
#########################################################################
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



#########################################################################
## kick_rider - Kicks the user in question from the ride. Only the ride
##              owner can do this.
##
#########################################################################
def kick_rider():
    user = db.auth_user(request.args(0)) or redirect(URL('index'))
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
             
#########################################################################
## view - View a ride. Prints out everything about the ride.
##
##
#########################################################################
def view():
    rides = db.ride(request.args[0]) or redirect(URL('index'))
    return dict(ride=rides, user_id = auth.user_id)



#########################################################################
## view_user - View a users profile.
##
##
#########################################################################      
@auth.requires_login()
def view_user():
     user = db.auth_user(request.args[0]) or redirect(URL('index'))
     return dict(user = user)



#########################################################################
## download - uploads a picture into the database for user profile.
##
##
######################################################################### 
def download(): return response.download(request,db)



#########################################################################
## delete - Delete ride from the database. Only the ride owner can do  
##          this.
##
######################################################################### 
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

 
                            
#########################################################################
## update - Update a ride.EMAIL IS WRONG.
##
##
#########################################################################                       
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
                                   

    
#########################################################################
## The rest of the fuctions we did not write, but were auto-generated by
## web2py.
##
#########################################################################    
                    
                            
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
