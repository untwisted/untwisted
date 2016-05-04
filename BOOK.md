Table of Contents
=================

  * [What can i create with untwisted?](#what-can-i-create-with-untwisted)
  * [Introduction](#introduction)
  * [The rapidserv plugin](#the-rapidserv-plugin)
      * [A simple application](#a-simple-application)
      * [The request object](#the-request-object)
      * [The basic dir structure](#the-basic-dir-structure)
      * [Quote Application](#quote-application)
        * [quote/static/comment\.html](#quotestaticcommenthtml)
        * [quote/templates/show\.html](#quotetemplatesshowhtml)
        * [quote/templates/view\.html](#quotetemplatesviewhtml)
        * [quote/app\.py](#quoteapppy)
        * [Running](#running)
      * [Imup Application](#imup-application)
        * [imup/templates/view\.jinja](#imuptemplatesviewjinja)
        * [imup/app\.py](#imupapppy)
      * [quickserv script](#quickserv-script)
  * [The event\-driven paradigm](#the-event-driven-paradigm)
      * [Skeletons](#skeletons)
      * [Image of objects/handles](#image-of-objectshandles)
      * [The symbol \*\*](#the-symbol-)
      * [Event arguments](#event-arguments)
  * [Dispatcher class](#dispatcher-class)
      * [Event types](#event-types)
      * [Spawning events from handles](#spawning-events-from-handles)
      * [Passing additional arguments to handles](#passing-additional-arguments-to-handles)
      * [Unbinding handles](#unbinding-handles)
      * [Exceptions in handles](#exceptions-in-handles)
      * [Handle return values](#handle-return-values)
      * [Handle execution order](#handle-execution-order)
  * [Reactors](#reactors)
  * [Super socket class](#super-socket-class)
  * [Spin class](#spin-class)
  * [Basic built\-in handles](#basic-built-in-handles)
  * [Basic Client/Server Applications](#basic-clientserver-applications)
      * [A simple Client (is\_up\.py)](#a-simple-client-is_uppy)
      * [Msg Server (msg\_server\.py)](#msg-server-msg_serverpy)
      * [Msg Client (msg\_client\.py)](#msg-client-msg_clientpy)
      * [Echo Server (echo\_server\.py)](#echo-server-echo_serverpy)
  * [Splits](#splits)
      * [Terminator Split](#terminator-split)
      * [Calc Server (calc\_server\.py)](#calc-server-calc_serverpy)
  * [Timers](#timers)
  * [Coroutines](#coroutines)
      * [A simple chat server (chat\_server\.py)](#a-simple-chat-server-chat_serverpy)
  * [Threads](#threads)
      * [Job class](#job-class)
      * [A basic example (sum\.py)](#a-basic-example-sumpy)
  * [Spawning processes](#spawning-processes)
      * [Expect class](#expect-class)
      * [A basic example (spawn\_process\.py)](#a-basic-example-spawn_processpy)
  * [Tasks](#tasks)
      * [Task class](#task-class)
      * [A Port Scan (port\_scan\.py)](#a-port-scan-port_scanpy)
  * [Reactor flow control](#reactor-flow-control)
      * [The Root exception](#the-root-exception)
      * [The Kill exception](#the-kill-exception)
  * [The requests plugin](#the-requests-plugin)
      * [HTTP GET](#http-get)
        * [Basic HTTP GET example (snake\.py)](#basic-http-get-example-snakepy)
      * [HTTP POST](#http-post)
        * [Basic HTTP POST example (codepad\.py)](#basic-http-post-example-codepadpy)
  * [The IRC Client plugin](#the-irc-client-plugin)
      * [IRC Events](#irc-events)
      * [A basic example (funbot\.py)](#a-basic-example-funbotpy)


What can i create with untwisted?
=================================

Untwisted permits the implementation of networking applications, spawning processes, threads. It is possible
to implement web crawlers, web applications, irc clients, irc servers, ftp clients, ftp servers, talk to processes.

Introduction
============

Untwisted is an event driven lib that offers ways to implement networking applications using a non blocking design.
It is possible to implement abstractions for application layer protocols and use these abstractions in the implementation
of networking applications that run on top of such internet layer protocols.

The rapidserv plugin
====================

Rapidserv is a micro web framework that is built on top of a powerful asynchronous networking library. It shares with flask
some similarities in the design of the applications that are built on top of Rapidserv. Rapidserv is non blocking network I/O
consequently it can scale a lot of connections and it is ideal for some applications. 
Rapidserv uses jinja2 although it doesn't enforce the usage.

### A simple application

The source code for a basic rapidserv application is listed below.

~~~python
from untwisted.plugins.rapidserv import RapidServ, core

app = RapidServ(__file__)

@app.request('GET /')
def send_base(con, request):
    con.add_data('<html> <body> <p> Rapidserv </p> </body> </html>')
    con.done()

if __name__ == '__main__':
    app.bind('0.0.0.0', 80, 50)
    core.gear.mainloop()
~~~

**The basic statements**

~~~python
from untwisted.plugins.rapidserv import RapidServ, core
app = RapidServ(__file__)
~~~

The RapidServ class is the web server instance that handles the HTTP requests. The core module
is untwisted module that is used to call the reactor mainloop.

The argument passed to the RapidServ constructor tells jinja2 where to look for 
templates and rapidserv plugins where to look for static files.

The usage of the decorator app.request tells rapidserv to deliver to the handle send_base HTTP 
requests whose method used is 'GET' and the path is '/'. The send_base handle is a view function.

Notice that it is needed to call the method con.done() in order to get the response sent to the
client.

These lines tells rapidserv to listen for connections on the interface '0.0.0.0' at the port 80.
The value 50 is the backlog.

~~~python
    app.bind('0.0.0.0', 80, 50)
    core.gear.mainloop()
~~~

### The request object

The request object that is passed to a view function holds a set of attributes that are listed below.

~~~python
request.method
request.headers
request.data
request.path
request.query
request.version
~~~

**request.method**

It holds the HTTP method that was used in the user request.

**request.headers**

Obviously, it holds the HTTP headers that were sent by the user.

**request.data**

That is a cgi.FieldStorage instance that holds the body of the request, stuff like files etc.

**request.query**

That is a dict instance that holds the query parameters that were sent in the HTTP request.

For example, if the user has sent a request like:

~~~
GET /path?name=iury HTTP/1.1
~~~

And there were a view defined like:

~~~python
@app.request('GET /path')
def path(con, request):
    print request.query['name'][0]
~~~

Would print 'iury'.

**request.path**

In a request like:

~~~
GET /view?name=iury HTTP/1.01
~~~

That attribute would hold the string '/view'.

**request.version**

It contains the HTTP version that was specified in the user request.

### The basic dir structure 

RapidServ applications are generally built on top of a standard structure of dirs. There is
a folder named templates and a folder named static to hold static files.

~~~
application/
    templates/
    static/
    app.py
~~~

### Quote Application

The Quote application is a simple quote system that permits users to add quotes to a database and view them when
they access the site base.

Let us create the folders and app.

~~~
mkdir quote
cd quote
mkdir templates
mkdir static
~~~

#### quote/static/comment.html

this file will hold the page that is used to add a quote.

~~~html
    <html>
     <body>
    
     <FORM action="/add_quote" method="get">
     <table>
     <tr>
     <td colspan="2">
        <textarea style="width:100%;" name="quote" rows="10" id="quote" cols="30"> 
            The cat was playing in the garden. </textarea> 
     </td>
     </tr> 
    
     <tr>
     <td>
        <INPUT name="name" id="name" type="text">
     </td>
     <td>
        <INPUT type="submit" value="Post">
     </td>
     </tr>
     </FORM>
     </body>
    </html>
~~~

Now it is time to implement the templates.

#### quote/templates/show.html

This template is used to render all the quotes of the database.

~~~html
    <html>
    
    <head>
    
    
    </head>
    
    </body>
    <h1> List of quotes. </h1>
    
     {% for index, name, quote in posts %}
        <h3><a href="/load_index?index={{index}}"> {{name}} {{quote}}... </a></h3>
      {% endfor %}
    
    <h1><a href="comment.html"> Add quote </a></h1>
    </body>
    
    </html>
~~~

#### quote/templates/view.html

This file is used to render a quote when the user clicks on the quote ref in the main page.

~~~html
    <html>
    
    <head>
    
    
    </head>
    
    </body>
    <h1> {{name}} </h1> 
    <h3> {{quote}} </h3> 
    
    </body>
    
    </html>
~~~

#### quote/app.py

It uses sqlite3 to hold the database of quotes. The database initialization could be
placed in another file for consistency if it were a more complicated application.

~~~python
from untwisted.plugins.rapidserv import RapidServ, make
import sqlite3

DB_FILENAME = 'DB'
DB          = sqlite3.connect(make(__file__, DB_FILENAME))
app         = RapidServ(__file__)
DB.execute('CREATE TABLE IF NOT EXISTS quotes (id  INTEGER PRIMARY KEY, name TEXT, quote TEXT)')
DB.commit()

@app.request('GET /')
def send_base(con, request):
    rst = DB.execute('SELECT * FROM quotes')
    con.render('show.jinja', posts = rst.fetchall())
    con.done()

@app.request('GET /load_index')
def load_index(con, request):
    index        = request.query['index']
    rst          = DB.execute('SELECT name, quote FROM quotes where id=?', index)
    name, quote  = rst.fetchone()
    con.render('view.jinja', name=name, quote=quote)
    con.done()

@app.request('GET /add_quote')
def add_quote(con, request):
    name      = request.query['name'][0]
    quote     = request.query['quote'][0]
    DB.execute("INSERT INTO quotes (name, quote) VALUES %s" % repr((name, quote)))
    DB.commit()
    send_base(con, request)

if __name__ == '__main__':
    app.run()
~~~


#### Running 

In order to run the app, issue the command below.

~~~
python2 app.py --addr '0.0.0.0' --port 1234
~~~

### Imup Application

Imup is a simple application to upload images into a shelve database. It shows the usage of the decorator
app.route that is used a shorthand to access query parameters from the request.

First of all it is needed to create the application folder.

~~~
mkdir imup
cd imup
mkdir templates
~~~

Let us implement the template.

#### imup/templates/view.jinja

~~~html
    <!DOCTYPE HTML>
    <html>
    <head>
    <meta http-equiv="content-type" content="text/html; charset=ISO-8859-1">
    
    <title>
    imup
    </title>
    
    </head>
    
    <body>
    <b> Max Image Size 1024 * 5024 bytes </b>
    <br>
    
    <br> <h1> Upload image </h1>
    <form action="/add_image" method="post" enctype="multipart/form-data">
    <input name="file" type="file"> <br> <br>
    <input type="submit" value="Send">
    </form>
    
    <br>
    
    <br>
    
    <h1> Images </h1>
     {% for index in posts %}
         <h3> {{index}} </h3>
        <img src="/load_index?index={{index}}"/>
      {% endfor %}
    
    
    </body>
    </html>
~~~

The template above will be loaded when the user access the base site /.

The code below is used to add a image to the database by using the method post

~~~html
    <br> <h1> Upload image </h1>
    <form action="/add_image" method="post" enctype="multipart/form-data">
    <input name="file" type="file"> <br> <br>
    <input type="submit" value="Send">
    </form>
~~~

This code is used to send a query string to the /load_index view to get the image data based on an index.

~~~html
<h1> Images </h1>
 {% for index in posts %}
     <h3> {{index}} </h3>
    <img src="/load_index?index={{index}}"/>
  {% endfor %}
~~~

The implementation of the app is straightforward now. 

#### imup/app.py

~~~python
from untwisted.plugins.rapidserv import RapidServ, make, HttpRequestHandle
import shelve

DB_FILENAME = 'DB'
DB          = shelve.open(make(__file__, DB_FILENAME))
HttpRequestHandle.MAX_SIZE = 1024 * 1024 * 3
app    = RapidServ(__file__)

@app.overflow
def response(con, request):
    con.set_response('HTTP/1.1 400 Bad request')
    HTML = '<html> <body> <h1> Bad request </h1> </body> </html>'
    con.add_data(HTML)
    con.done()

@app.route('GET /')
def index(con):
    con.render('view.jinja', posts = DB.iterkeys())
    con.done()

@app.route('GET /load_index')
def load_index(con, index):
    con.add_data(DB[index[0]], mimetype='image/jpeg')
    con.done()

@app.route('POST /add_image')
def add_image(con, file):
    DB[file.filename] = file.file.read()
    index(con)

if __name__ == '__main__':
    app.run()
~~~

It sets the max size for images being uploaded.

~~~python
HttpRequestHandle.MAX_SIZE = 1024 * 1024 * 3
~~~

If an user attempts to upload an image that is larger than the specified then this view is called.

~~~python
@app.overflow
def response(con, request):
    con.set_response('HTTP/1.1 400 Bad request')
    HTML = '<html> <body> <h1> Bad request </h1> </body> </html>'
    con.add_data(HTML)
    con.done()
~~~

When the user sends a request like:

~~~
GET /load_index?index=10
~~~

Then the view below is called.

~~~python
@app.route('GET /load_index')
def load_index(con, index):
    con.add_data(DB[index[0]], mimetype='image/jpeg')
    con.done()
~~~

The index variable will hold 10

This handle is used to store the image into the database.

~~~python
@app.route('POST /add_image')
def add_image(con, file):
    DB[file.filename] = file.file.read()
    index(con)
~~~

The file variable holds a cgi.FieldStorage instance, notice that the name file was used when implementing
the template imup/templates/view.jinja

~~~html
    <input name="file" type="file">
~~~

### quickserv script

The quickserv script is used to serve content over http.

~~~

quickserv -p port -b backlog -a addr -f folder
~~~

The command below would permit users to access the content of the ~/Downloads folder through http requests.

~~~
quickserv -p 1024 -f ~/Downloads
~~~


The event-driven paradigm
=========================

The event-driven paradigm is a powerful tool to deal with some specific systems, in the event-driven paradigm
the flow of the program is based on events. Events are intrinsically related to handles, if there is a handle
mapped to an event and such an event occurs then the handle is called. An event can carry arguments that better
characterize the type of happening that is related to the event. 

In untwisted context, events can be any kind of python object, an integer, a function, a class, an exception etc.
It is possible to map one or more handles to a given event, when the event occurs then the handles will be called
with the event's arguments.

In event-driven applications there will exist generally an event loop that is responsible by processing a set of handles
according to some set of events. Untwisted reactor is responsible by processing a set of handles according to a few basic
events. These basic events are related to the state of a given set of sockets. So, when a socket is ready to send data
it spawns an event WRITE, when there is data available for reading then it spawns READ, etc.

The fact of untwisted being such a powerful approach to implement networking applications consists
of being possible to have events that are mapped to handles that spawn other events and so on. It may not
sound obvious at first glance why it turns to be useful but it will make more sense later. 


### Skeletons

The diagrams along this document are a way to express superficially interactions between objects
that are used to implement networking applications on top of untwisted.

Consider:

~~~
Event0  -> Handle0 -> (Event1, Event2)
Event1  -> Handle1
Event2  -> Handle2
~~~

The expression:

~~~
m -> n
~~~

When m and n are either an event or a handle it means that when m is processed then n is processed.
A handle is processed when it is called, an event is processed when it merely happens.

Note that the expression:

~~~
(Event0, event1, event2, ...)
~~~

It means that the sequence of events will be processed.

It is necessary to introduce some notation to simplify the exposition of ideas and facts.

A set of events is denoted by:

~~~
{Event0, Event1, Event2, ...}
~~~

A set of handles is denoted by:

~~~
n = {Handle0, Handle1, Handle2, ...}
~~~

The expression:

~~~
m => n
~~~

When m is an event and n is a handle then when m is processed it may occur of n being called and vice versa. When m is a set of 
events and n is a handle it means that when one of the events happens then it may happen of n being processed. When m is a set of handles
and n is an event then when one of the handles is processed it may occur of n being processed.

on the other hand the expression:

~~~
m -> n
~~~

When m is an event and n is a handle it means when the event is processed then the handle is processed and vice versa. When m is a set
of events and n is a handle it means that when one of the events is processed then the handle will be processed.
The case where m is a set of handles and n is an event the expression means that whenever one of the handles is
called then the event is processed.

The expression:

~~~
m = (Event0, Event1, Event2, ...)
~~~

It means a sequence of events whose order matters. The same occurs with the sequence of handles.

~~~
n = (Handle0, Handle1, Handl2, ...)
~~~

The expression:

~~~
Handle0 -> (Event0, Event1)
~~~

It means that Handle0 will spawn Event0 and Event1 in that exact order. While the expression.

~~~
Handle0 -> {Event0, Event1}
~~~

It means that Handle0 will spawn Event0 and Event1 but not exactly in that order.

Using this scheme of notation it is possible to describe reasonably well the flow of a program that is implemented
using event-driven paradigm. In order to denote arguments that are carried by events, the notation below is used.

~~~
Event0 -(arg0, arg1, ...)-> Handle0
~~~

and

~~~
Event0 =(arg0, arg1, ...)=> Handle0
~~~

Where the symbols -> and => have been explained above.

Events are related to the state of some objects, events are mapped to handles and handles can change
the state of objects that can then generate events. A socket can be abstracted as a object that can
hold a set of possible states. We will be interested initially in the states of it being ready to be read
and ready to be written to.

The expressions below need to be related to some object in order to better express systems.

~~~
m -> n
m => n
~~~

Consider the handles defined below.

~~~
H0 = "Open the umbrella"
H1 = "Close the umbrella"
~~~

These handles are mapped to the events.

~~~
E0 = "It starts raining"
~~~

~~~
E1 = "It stops raining"
~~~

So you would have.

~~~
H0 -> E0
H1 -> E1
~~~

But it is not the case that everyone would open an umbrella when it starts raining, i particularly hate to carry umbrellas.
So, it is related to a specific object in the context it is a given person. A set of relations between events and handles 
are always related to a given object or a set of objects.

The notation below is used to denote when a given set of events and handles are related to a given object:

~~~
object0 { 
    Handle0 -> Event0 -> Handle1 -> Event1
    Event1 -> Handle2
    .
    .
    .

}

~~~

We'll be interested in specific objects when using untwisted, these are sockets, threads, processes etc. It is interesting notice that handles can be 
seen as events and vice versa. 

Consider the situation in which a handle is processed and a set of possible events might occur but just once.
Such a situation is described using the notation below.

~~~
object {
    Handle0 -> *{Event0, Event1, Event2, ...}

}
~~~

That basically means that if Handle0 is processed then one of the events in the set
can be processed but just one and just once. 

**These diagrams will be used sometimes to explain some untwisted workings.**

### Image of objects/handles

When a handle that is associated with an object is processed then a set of events may happen, this set
of possible events is the handle image. 

~~~
handle -> {event0, event1, ...}
~~~

When an object is processed then a set of possible events may happen, such a set is the image of the object.

~~~
object -> {event0, event1, ....}
~~~

### The symbol **

Consider a socket connection to a web server, the socket server can be associated to a set of events, let us consider
for simplicity it is associated with three events. When the server sends data then the socket server will spawn LOAD,
when it is possible to write data back to the server then it spawns WRITE, if the server closes the socket then
it happens the event CLOSE. After that event there will occur no more events because the connection is down.

~~~
server -> {LOAD, WRITE, **CLOSE}
~~~

The event CLOSE that is associated with the socket server connection if it happens just once then
no more events will be processed for that object.

### Event arguments

Events can carry information that better characterizes the event. The notation to express that is shown below.

~~~
LOAD -(str:data)-> handle
~~~

Dispatcher class
================

The dispatcher class is responsible by processing handles that are mapped to events. In order to get a 
clear picture of how implementing networking applications on top of untwisted it is needed to understand
the features of the Dispatcher class. There are other classes that inherit from Dispatcher and these are the
used ones to model applications.

A Dispatcher instance is an object that can hold a set of mappings of the type:

~~~
Dispatcher {
    m0 -> n0 -> m1 ...
    m1 ->  n1 -> ...
    .
    .
    .
}
~~~

The best way to grasp the behavior of Dispatcher objects is testing them in the python interpreter.

~~~python
>>> from untwisted.dispatcher import Dispatcher
>>> dispatcher = Dispatcher()
>>> dir(dispatcher)

['__class__', '__delattr__', '__dict__', '__doc__', '__format__', 
'__getattribute__', '__hash__', '__init__', '__module__', '__new__', 
'__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', 
'__str__', '__subclasshook__', '__weakref__', 'add_handle', 'add_map', 
'add_static_map', 'base', 'del_handle', 'del_map', 'del_static_map',
'drive', 'pool', 'process_base']
~~~

The methods add_map and del_handle are the most used ones. These methods are used to bind handles to events that
are related to the given Dispatcher object. 

As handles and events are related to objects, objects may be related between each other in some way. A given object
may change the state of other object then an event happens. The method drive of the Dispatcher class is used
to fire an event in the Dispatcher object. Once an event is fired in a given Dispatcher object then all handles associated
with that event will be processed. As mentioned before, events can carry arguments that better characterize the event,
the drive method permits to fire events with a given set of arguments associated to the event.

~~~python
>>> dispatcher.drive('RAINING', 'Brasil', 'Rio de Janeiro', 'Rio das ostras')
~~~

The above code spawns an event named 'RAINING' with three arguments that correspond to the country, state and city
that characterizes the event.

Events in untwisted can be all kind of python objects. Handles can be all kind of objects that are
callable.

~~~python
>>> def handle0(dispatcher, country, state, city):
...     print 'It is raining in %s, %s, %s' % (country, state, city)
... 
>>> dispatcher.add_map('RAINING', handle0)
~~~

The above code adds a mapping between the event 'RAINING' and the callback handle0. Now if the event 'RAINING'
occurs then the callback will be called with the arguments.

~~~python
>>> dispatcher.drive('RAINING', 'Brazil', 'Rio de janeiro', 'Rio das ostras')
It is raining in Brazil, Rio de janeiro, Rio das ostras
>>> 
~~~

Let us define a new callback and maps to the 'RAINING' event then check out what happens.

~~~python
>>> def handle1(dispatcher, country, state, city):
...     if country == 'Brazil' and \
...                state == 'Rio de janeiro' and \
...                         city == 'Rio das ostras':
...         print 'It is raining in hell'
... 
>>> dispatcher.add_map('RAINING', handle1)
>>> dispatcher.drive('RAINING', 'Brazil', 'Minas gerais', 'Belo horizonte')
It is raining in Brazil, Minas gerais, Belo horizonte
>>> dispatcher.drive('RAINING', 'Brazil', 'Rio de janeiro', 'Rio das ostras')
It is raining in Brazil, Rio de janeiro, Rio das ostras
It is raining in hell
>>> 
~~~

There is other way to add a mapping between an event and a handle to a Dispatcher object it is
using the xmap function. This function is merely a synonymous for add_map.

~~~python
>>> from untwisted.dispatcher import Dispatcher, xmap, spawn
>>> dispatcher = Dispatcher()
>>> 
>>> def on_alpha(dispatcher):
...     print 'Event ALPHA occured'
... 
>>> xmap(dispatcher, 'ALPHA', on_alpha)
>>> 
~~~

The reasons to use xmap function instead of add_map are aestheticals. 
The same occurs when firing events.

~~~python
>>> spawn(dispatcher, 'ALPHA')
Event ALPHA occured
>>> spawn(dispatcher, 'BETA', 'arg1', 'arg2', 'arg3')
>>> 
~~~

### Event types

Events can be any kind of python objects but it is interesting to have a reliable scheme 
to define new events. Untwisted implements the get_event function that returns a unique event.

~~~python
>>> from untwisted.event import get_event
>>> 
>>> LOAD = get_event()
>>> 
>>> print LOAD
24
>>> FOUND = get_event()
>>> 
>>> print FOUND
25
>>> 
~~~

These events are used for situations where the usage of strings wouldn't be interesting 
or ambiguous in some circumstances.

### Spawning events from handles

Handles that are mapped to events can spawn events inside objects. 

The code below clarifies better:

~~~python
>>> from untwisted.dispatcher import Dispatcher
>>> from untwisted.event import LOAD
>>> 
>>> dispatcher = Dispatcher()
>>> 
>>> def on_load(dispatcher, data):
...     cmd = data.split(' ')
...     dispatcher.drive(cmd.pop(0), cmd)
... 
>>> dispatcher.add_map(LOAD, on_load)
>>> 
~~~

Let us drive a LOAD event inside that dispatcher object.  

~~~python

>>> def on_add(dispatcher, args):
...     print 'Sum:', sum(map(int, args))
... 
>>> dispatcher.add_map('add', on_add)
>>> dispatcher.drive(LOAD, 'add 1 1 2')
Sum: 4
~~~

It creates a new handle named on_add and maps it to the event 'add'.


### Passing additional arguments to handles

There will occur situations that it is necessary to pass addional information
to a handle that is called when an event occurs.  The example below examplifies:

~~~python
>>> from untwisted.event import DONE
>>> 
>>> dispatcher = Dispatcher()
>>> 
>>> def on_done(dispatcher, data, value):
...     print data, value
... 
>>> dispatcher.add_map(DONE, on_done, 100)
>>> dispatcher.drive(DONE, 'Tau')
Tau 100
>>> 
~~~

That example looks useless under a perspective but is enough to explain the feature. You'll find
yourself passing extra arguments to handles a lot of times in some applications. 
Notice that if you call the method drive with more arguments then you'll get an exception.

~~~python
>>> dispatcher.drive(DONE, 1000, 1200)
Traceback (most recent call last):
  File "/usr/lib/python2.7/site-packages/untwisted/dispatcher.py", line 34, in process_base
    seq = handle(self, *(args + data))
TypeError: on_done() takes exactly 3 arguments (4 given)
>>> 
~~~

When it is not known the number of arguments of the event then it is useful to implement the handle with.


~~~python
def on_event(dispatcher, *args):
    pass
~~~

### Unbinding handles

As it is useful to add mappings it is useful to remove them. Removing a mapping may avoid
a chain of events of being processed, there are circumstances where that is necessary as well.

~~~python
>>> from untwisted.dispatcher import Dispatcher
>>> from untwisted.event import LOAD
>>> 
dispatcher = Dispatcher()
>>> >>> 
>>> def on_load(dispatcher, data):
...     print 'LOAD event occured:', data
...     dispatcher.del_map(LOAD, on_load)
... 
>>> dispatcher.add_map(LOAD, on_load)
>>> dispatcher.drive(LOAD, 'cd /glau')
LOAD event occured: cd /glau
>>> dispatcher.drive(LOAD, 'ls')
>>> 
~~~

The method del_map is used to remove a mapping from a Dispatcher object. In the above code,
the handle on_load will be processed just once for the event LOAD.

### Exceptions in handles

When a given handle is called it will process the event arguments and eventually it may occur an exception inside the handle.
The event loop can't stop due to that exception being raised because it is advantageous under some perspectives
to keep the reactor processing other events. There will exist situations that it will not be advantageous to keep
the reactor processing a given list of handles for a given event, in that case there are specific exceptions
that can be raised to change the flow of the events it means avoiding some events to occur or having more
events to occur. So, in untwisted, the flow of the events can be controlled with a set of specific exceptions.

The way of how untwisted is used to model applications doesn't permit to catch exceptions as it is usually done.

~~~python
>>> from untwisted.dispatcher import Dispatcher
>>> dispatcher = Dispatcher()
>>> 
>>> def handle(dispatcher, x, y):
...     print x/y
... 
>>> dispatcher.add_map('div', handle)
>>> dispatcher.drive('div', 1, 2)
0
~~~

That's expected, what about if the event carried the values 1 and 0?

~~~python
>>> dispatcher.drive('div', 1, 0)
Traceback (most recent call last):
  File "/usr/lib/python2.7/site-packages/untwisted/dispatcher.py", line 34, in process_base
    seq = handle(self, *(args + data))
  File "<stdin>", line 2, in handle
ZeroDivisionError: integer division or modulo by zero
>>> 
~~~

When we call a function or class method that could throw an exception it is natural to use a try/except block
to catch the exceptioin then decide what to do based on the exception type. When modelling applications using
untwisted one would use the decorator handle_exception to catch exceptions that might happen from handle calls.

~~~python
>>> from untwisted.dispatcher import Dispatcher
>>> from untwisted.tools import handle_exception
>>> 
>>> dispatcher = Dispatcher()
>>> 
>>> @handle_exception(ZeroDivisionError)
... def handle(dispatcher, x, y):
...     print x/y
... 
>>> dispatcher.add_map('div', handle)
>>> 
~~~

The decorator handle_exception solves the problem of the unhandled exception. When spawning the 'div' event
with values that could cause an exception it will not be printed.

~~~python
>>> dispatcher.drive('div', 4, 2)
2
>>> dispatcher.drive('div', 1, 0)
>>> 
~~~

However, it is not the case that avoiding the exception of being printed is enough, it is important to have
other parts of the code being noticed of the exception. The decorator handle_exception turns an exception
that occured inside a handle into an event of the type (handle, exception).

~~~python
>>> def on_zero_division_error(dispatcher, excpt):
...     print 'The exception was thrown:', excpt
... 
>>> 
>>> dispatcher.add_map((handle, ZeroDivisionError), on_zero_division_error)
>>> dispatcher.drive('div', 1, 0)
The exception was thrown: integer division or modulo by zero
~~~

In the code above, the handle on_zero_division_error was defined to catch the exception ZeroDivisionError that
could occur inside the handle function that does the division of two numbers when the 'div' event occurs.
Using this approach it is possible to have one or more handles deciding what to do when an exception occurs at some
point of the program it increases extensibility and turns modelling of applications more succint and modular.

### Handle return values

When handles are called on events, they aren't supposed to return a value that is advantaged by other parts
of the program unless it is explicitly defined using the mapcall decorator.

Consider the example below:

~~~python
>>> from untwisted.dispatcher import Dispatcher
>>> 
>>> dispatcher = Dispatcher()
>>> 
>>> def handle(dispatcher, x, y):
...     return x/y
... 
>>> dispatcher.add_map('div', handle)
>>> dispatcher.drive('div', 4, 2)
>>> 
~~~

Nothing happened as expected. It is possible to turn handle into an event by using the mapcall decorator.
So, when handle is processed then an event is processed which corresponds to the handle function. The
event carries the return value of the function handle. 

Using mapcall in the code above:

~~~python
>>> from untwisted.dispatcher import Dispatcher
>>> from untwisted.tools import mapcall
>>> 
>>> dispatcher = Dispatcher()
>>> 
>>> @mapcall(ZeroDivisionError)
... def handle(dispatcher, x, y):
...     return x/y
... 
>>> def on_handle(dispatcher, result):
...     print 'Div:', result
... 
>>> dispatcher.add_map('div', handle)
>>> dispatcher.add_map(handle, on_handle)
>>> dispatcher.drive('div', 2, 4)
Div: 0
>>> dispatcher.drive('div', 4, 2)
Div: 2
>>> 
~~~

The mapcall decorator receives arguments that correspond to exceptions that could be raised by the handle function.
The handle function is mapped to the event 'div', when 'div' happens handle is processed and its return value
is carried into an event whose value is the handle function. The code below maps the handle function that turned
into an event to the on_handle function.

~~~python
>>> dispatcher.add_map(handle, on_handle)
~~~

What about if an exception occurs inside handle function? 

~~~python
>>> dispatcher.drive('div', 1, 0)
>>> 
~~~

Well, the exception is automatically handled and turned into an event of the type:

~~~python
(handle, ZeroDivisionError)
~~~

Whose argment carried is a ZeroDivisionError instance. it is possible to define a handle to deal
with the exception that occured like it would be done using handle_exception decorator.

~~~python
>>> def on_zero_division_error(dispatcher, excpt):
...     print 'The exception was thrown:', excpt
... 
>>> dispatcher.add_map((handle, ZeroDivisionError), on_zero_division_error)
>>> dispatcher.drive('div', 1, 2)
Div: 0
>>> dispatcher.drive('div', 1, 0)
The exception was thrown: integer division or modulo by zero
>>> 
~~~

When using the mapcall decorator and an exception occurs inside a handle then there is no event that corresponds
to the handle return value but an event that corresponds to the exception that was raised.

It is interesting to notice that when using handle_exception or mapcall it could be possible to pass a set of
exceptions like:

~~~python
@mapcall(ZeroDivisionError, ValueError)
def handle(dispatcher):
    raise ValueError
~~~

The example below would turn into events all possible exceptions that occured inside handle.

~~~python
@mapcall(Exception):
def handle(dispatcher):
    raise ValueError

~~~

### Handle execution order

Consider the code below, when handle0 is processed it binds handle1 to the event named 'event' but handle1 will be processed
just when 'event' happens again.

~~~python
>>> from untwisted.dispatcher import Dispatcher
>>> dispatcher = Dispatcher()
>>> from untwisted.dispatcher import Dispatcher
>>> 
>>> def handle1(dispatcher):    
...     print 'handle1'
... 
>>> def handle0(dispatcher):
...     dispatcher.add_map('event', handle1)
...     print 'handle0'
... 
>>> dispatcher = Dispatcher()
>>> dispatcher.add_map('event', handle0)
>>> dispatcher.drive('event')
handle0
>>> dispatcher.drive('event')
handle0
handle1
>>> 
~~~

Reactors
========

Untwisted reactor is an event loop that listen for events that are related to file descriptors. When
objects that are associated with file descriptors are created in untwisted then they are registered
in the reactor for reading and writting events.

Untwisted implements the following reactors.

**Select**

The select reactor can be used in Unix and Win32 platforms.

**Epoll**

The epoll reactor is used in Linux platforms, it is default in Linux.

**Poll**

It is used in Unix platforms (Not implemented yet).

Super socket class
==================

As objects can be associated with events and handles as seen previously, it is elegant and useful to think of
a socket as an object that can throw events. The basic events associated to a socket are READ and WRITE.
So, why not having a socket class that has the features of the Dispatcher class? That is what 
the class defined in untwisted.network.SuperSocket is. The SuperSocket class abstracts the behavior of
other classes. The SuperSocket class holds a file descriptor that is associated with objects that can
be associated with a file descriptor. When a SuperSocket instance is created it registers itself
in the untwisted reactor. 

Spin class
==========

The Spin class is a socket class that inherits from Dispatcher class. The untwisted reactor scales
which file descriptors are ready for reading or writting then notifies the Spin instances of such
events. The basic two events that can occur in the Spin class are READ and WRITE. Every other event
that can happen and is associated with a Spin instance is generated from these two ones.

When a Spin class is created and handles are mapped to events it is needed to call the method mainloop
of the reactor in order to get events being processed for the file descriptors.

~~~python
from untwisted.network import Spin, core

sock = Spin()

# Install events in sock.
# Connect the socket to a host.

core.gear.mainloop()
~~~

The method core.gear.mainloop is used to process the events, after such a method being called
the program will be listening for events that are related to the file descriptors.

Basic built-in handles
======================

It is needed some built-in handles to get the usefulness of the Spin instances, these handles are responsible
by spawning more specific events. The reactor spawns just two events READ and WRITE, the remaining ones
that correspond to CLOSE, CONNECT_ERR, CLOSE_ERR, ACCEPT, ACCEPT_ERR are spawned by these built-in handles.

**Built-in TCP/IP handles**

~~~python
untwisted.iostd.Client
untwisted.iostd.Stdin
untwisted.iostd.Stdout
Untwisted.iostd.Server
~~~

The Client class is a handle that spawns the events CONNECT or CONNECT_ERR. In diagram it is equivalent to:

~~~
WRITE -> Client -(), (int:err)-> *{CONNECT, CONNECT_ERR}
~~~

That basically means that if CONNECT is processed then CONNECT_ERR will not be processed and that if 
CONNECT_ERR then CONNECT will not be processed and that CONNECT or CONNECT_ERR will be processed just once.

The Stdin handle is used to send data through a socket asynchronously. It basically monkey patch
a method in a given Spin instance that is used to send data through the socket. The Stdin
handle can spawn the event CLOSE as well.

The Stdout handle spawns the event LOAD that carries the data that was read from the socket. It may
spawns CLOSE, RECV_ERR as well.

~~~
READ -> Stdout -(str:data), (int:err)-> {LOAD, **CLOSE}
~~~

The symbols ** at the left of the event CLOSE means that if CLOSE is processed then
the handle Stdout will no more process other events. So, once CLOSE is processed the event LOAD
will no more be processed.

That basically means that when the handle Stdout is processed then the event LOAD may be processed
and it carries the data that was read from the Spin instance that is a socket. If the CLOSE event
occurs it means the connection is down and the value err corresponds to the error that occured. The
err value should be in the python module errno.errorcode.

The Server handle is responsible by spawning the events ACCEPT or ACCEPT_ERR

~~~
READ -> Server -(Spin:client), (int:err)-> {ACCEPT, ACCEPT_ERR}

~~~

That means when a server socket got a client connected the Server handle will accept the connection
then process the ACCEPT event, if it fails then it processes ACCEPT_ERR.

Basic Client/Server Applications
================================

### A simple Client (is_up.py)

Let us think of a minimal application that receives from the command line two arguments, TCP server address and port number.
Once the arguments are provided then the application tries to connect to the server then either notifies success or failure.

So, it is time to implement the code to do the basic imports at the beginning of the file.

~~~python
from untwisted.network import core, Spin, xmap, die

~~~    

That line imports the core module that holds an instance of the gear class that corresponds to untwisted
reactor.  The xmap function is basically the same as Spin.add_map method.
The die function stops the reactor from processing file descriptors.

It is now time to import the basic handles and events that will be used in the application.

~~~python
from untwisted.iostd import Client, CONNECT, CONNECT_ERR
import errno

~~~

The Client handle is a class that spawns the events CONNECT and CONNECT_ERR. The Client handle
will be attached to the Spin instance to process the events to notify other handles of the connection
status.

Implementing a function named create_connection that will instantiate a Spin instance then
bind handles on the events.

~~~python
def create_connection(addr, port):
    con = Spin()
    Client(con)
~~~

The Client handle will process either CONNECT or CONNECT_ERR events that corresponds to the socket status.
Now, it is time to create the handles for these events.

~~~python

def on_connect(con, addr, port):
    print 'Connected to %s:%s !' % (addr, port)

def on_connect_err(con, err, addr, port):
    print "Failed to connect to %s:%s, errcode " % (addr, port), errno.errorcode[err]
~~~

Once the handles are implemented, it is time to map the events in the create_connection function.

~~~python
    xmap(con, CONNECT, on_connect, addr, port)
    xmap(con, CONNECT_ERR, on_connect_err, addr, port)
    xmap(con, CONNECT, lambda con: die())
    xmap(con, CONNECT_ERR, lambda con, err: die())
~~~

The event CONNNECT only carries one argument that is the Spin instance, at the code above it adds other two arguments
to be passed to the on_connect handle, the arguments are addr and port. The same occurs with CONNECT_ERR
event that carries two arguments, they are the Spin instance and the err value that is an integer whose meaning
is defined in the errno module. The die function is used to stop the reactor from processing the file descriptors.

The game is almost won, now! It is time to connect the socket to the addr and port. In the create_connection function
just add the line.

~~~python
    con.connect_ex((addr, port))
~~~

The method connect_ex is used instead of the connect.

Let us implement the code that gets the addr and the port number.

~~~
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--addr', help='Address')
    parser.add_argument('-p', '--port', type=int, help='Port')
    args = parser.parse_args()
    create_connection(args.addr, args.port)
~~~

If we run the code it wouldn't work as expected because we need to execute the untwisted mainloop.
So, we just add the statement below at the bottom of the file.

~~~
    core.gear.mainloop()
~~~

The complete source code is listed below.

~~~python
from untwisted.network import core, Spin, xmap, die
from untwisted.iostd import Client, CONNECT, CONNECT_ERR
import errno

def on_connect(con, addr, port):
    print 'Connected to %s:%s !' % (addr, port)

def on_connect_err(con, err, addr, port):
    print "Failed to connect to %s:%s, errcode " % (addr, port), errno.errorcode[err]

def create_connection(addr, port):
    con = Spin()
    Client(con)
    xmap(con, CONNECT, on_connect, addr, port)
    xmap(con, CONNECT_ERR, on_connect_err, addr, port)
    xmap(con, CONNECT, lambda con: die())
    xmap(con, CONNECT_ERR, lambda con, err: die())
    
    con.connect_ex((addr, port))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--addr', help='Address')
    parser.add_argument('-p', '--port', type=int, help='Port')
    args = parser.parse_args()

    create_connection(args.addr, args.port)
    core.gear.mainloop()
~~~

Saving that as a file named is_up.py and testing we would get.

~~~python
[tau@lambda extra]$ python2 is_up.py -a www.google.com.br -p 90
Failed to connect to www.google.com.br:90, errcode  ETIMEDOUT
[tau@lambda extra]$ python2 is_up.py -a www.google.com.br -p 80
Connected to www.google.com.br:80 !
~~~

### Msg Server (msg_server.py)

It is the implementation of a simple msg server that receives connections then prints
whatever data the clients send. The application is listed below.

~~~python
from untwisted.network import xmap, Spin, core
from untwisted.iostd import Server, Stdout, Stdin, lose, ACCEPT, LOAD, CLOSE
from socket import socket, AF_INET, SOCK_STREAM
import sys

def setup(server, con):
    Stdin(con)
    Stdout(con)
    xmap(con, CLOSE, lambda con, err: lose(con))
    xmap(con, LOAD, lambda con, data: sys.stdout.write('%s\r\n' % data))

if __name__ == '__main__':    
    from optparse import OptionParser

    parser   = OptionParser()
    parser.add_option("-a", "--addr", dest="addr",
                      metavar="string", default='0.0.0.0')
                  
    parser.add_option("-p", "--port", dest="port",
                      type="int", default=1234)

    parser.add_option("-b", "--backlog", dest="backlog",
                      type="int", default=5)

    (opt, args) = parser.parse_args()
    sock   = socket(AF_INET, SOCK_STREAM)
    server = Spin(sock) 
    server.bind((opt.addr, opt.port))
    server.listen(opt.backlog)
    Server(server)
    
    xmap(server, ACCEPT, setup)
    
    core.gear.mainloop()
~~~

The lines listed below are responsible by creating a socket then wrapping it with the Spin class.

~~~python
    sock   = socket(AF_INET, SOCK_STREAM)
    server = Spin(sock) 
~~~

It just calls the method bind and listen as usually it is used when dealing with socket servers.

~~~python
    server.bind((opt.addr, opt.port))
    server.listen(opt.backlog)
~~~

In the code below it installs the handle Server that spawns the events ACCEPT, ACCEPT_ERR. The ACCEPT one
means that a new connection has arrived.

~~~python
    Server(server)
    xmap(server, ACCEPT, setup)
~~~

The setup function is called when a new connection has arrived, it installs the basic built in handles
Stdin and Stdout, these deal with sending and receiving data.


~~~python
def setup(server, con):
    Stdin(con)
    Stdout(con)
    xmap(con, CLOSE, lambda con, err: lose(con))
    xmap(con, LOAD, lambda con, data: sys.stdout.write('%s\r\n' % data))
~~~

In the setup the line below maps the event CLOSE to the lambda that calls the function lose. The
function lose is used to close the connection and unregister the socket from the reactor.

~~~python
    xmap(con, CLOSE, lambda con, err: lose(con))
~~~

The line below just maps the event LOAD that is spawned by the handle Stdin to a lambda that writes
to stdout.

~~~python
    xmap(con, LOAD, lambda con, data: sys.stdout.write('%s\r\n' % data))
~~~

Saving the file as msg_server.py and running it with:

~~~
python2 msg_server.py -a '0.0.0.0' -p 1235 -b 50
~~~

Then connecting from a telnet with:

~~~
telnet localhost 1235
~~~

You'll get all the text that was sent from the telnet printed in the msg server window.

### Msg Client (msg_client.py)

This is the counter part of the msg server application. The program listed below
is using essentially the basic features of the msg_server.py one.

~~~python
from untwisted.network import xmap, Spin, core
from untwisted.iostd import Client, Stdout, Stdin, CONNECT, DUMPED
from socket import socket, AF_INET, SOCK_STREAM
from untwisted.core import die

def setup(con, msg):
    Stdout(con)
    Stdin(con)
    con.dump(msg)
    xmap(con, DUMPED, lambda con: die('Msg dumped!'))

def create_connection(addr, port, msg):
    sock = socket(AF_INET, SOCK_STREAM)
    con  = Spin(sock)

    Client(con)
    con.connect_ex((addr, port))
    xmap(con, CONNECT, setup, msg)

if __name__ == '__main__':
    from optparse import OptionParser

    parser   = OptionParser()
    parser.add_option("-a", "--addr", dest="addr",
                      metavar="string", default='localhost')
                  
    parser.add_option("-p", "--port", dest="port",
                      type="int", default=1234)

    parser.add_option("-m", "--msg", dest="msg",
                      metavar="string")

    (opt, args) = parser.parse_args()
    create_connection(opt.addr, opt.port, opt.msg)
    core.gear.mainloop()
~~~

The line below merely dumps the message that was specified by the user through the socket. The Stdin
handle monkey patch the method dump.

~~~python
    con.dump(msg)
~~~

When all the data was sent then Stdin handle spawns the event DUMPED in the Spin instance that it was
added to.

~~~
    xmap(con, DUMPED, lambda con: die('Msg dumped!'))
~~~

When the event dumped happens then it calls die to stop the reactor then prints a msg on the screen.

Place the source code above inside a file named msg_client.py then run the msg_server.py with:

~~~
python2 msg_server.py -a '0.0.0.0' -p 1235 -b 50
~~~

It is possible to send messages to the msg_server.py instance by running msg_client.py with.

~~~
python2 msg_client.py -a 'localhost' -p 1234 -m 'it is gonna be cool'
~~~

### Echo Server (echo_server.py)

The example below shows a simple echo server application that uses the shorthand function create_server.
Such a function instantiates a Spin instance and installs the basic handles in the server socket
and in the new incoming connection sockets. 

~~~python
from untwisted.network import Spin, xmap, core
from untwisted.iostd import create_server, ACCEPT, LOAD

class EchoServer(object):
    def __init__(self, server):
        xmap(server, ACCEPT, lambda server, con: 
                     xmap(con, LOAD, lambda con, data: con.dump(data)))

if __name__ == '__main__':
    EchoServer(create_server('0.0.0.0', 1234, 5))
    core.gear.mainloop()
~~~

Consider the line:

~~~python
        xmap(server, ACCEPT, lambda server, con: 
                     xmap(con, LOAD, lambda con, data: con.dump(data)))
~~~

That basically adds a mapping LOAD -(str:data)-> print to the con object that corresponds
to the new connection. When the event LOAD happens in one of the cliet connections then it dumps back
the data that was received.

Splits
======

Application layer protocols are mostly based on string tokens, these tokens models the communication between client
and server applications. An example is the HTTP protocol that uses '\r\n\r\n' to separate HTTP headers from HTTP content
in a HTTP request.

The fundamental idea of untwisted is providing a set of tools to parse application layer protocols into meaningful
chunks of data then spawning events. These events can be used to model applications either in the client side or server side
applications.

### Terminator Split

The Terminator split is a handle that is processed on the LOAD event. It accumulates data that is
carried with the LOAD event until a specific token appears. When the specified token appears in the data
then it splits all the data that was accumulated into a list of chunks and it spawns the event Terminator.FOUND
sequentially with each one of the chunks.

The best way to understand the Terminator handle is testing it in the python interpreter.

~~~python
>>> from untwisted.splits import Terminator
>>> from untwisted.dispatcher import Dispatcher
>>> from untwisted.event import LOAD
>>> 
>>> con = Dispatcher()
>>> terminator = Terminator(con, delim=',')
~~~

The code above instantiates a Dispatcher instance named con that simulates a Spin socket. It installs
the handle Terminator with the delimiter ','. Whenever the LOAD event happens in the con instance
it will check for the token ',' if it appears then it splits the data into chunks that are delimited by ',' otherwise
it accumulates the data.

~~~python
>>> def on_found(con, data):
...     print 'msg:', data
... 
>>> con.add_map(Terminator.FOUND, on_found)
>>> 
~~~

When the event Terminator.FOUND happens then calls on_found handle with the chunk.

~~~python
>>> con.drive(LOAD, 'word1,word2,wor')
msg: word1
msg: word2
>>> con.drive(LOAD, 'd3,word4')
msg: word3
>>> con.drive(LOAD, ',')
msg: word4
>>> 
~~~

When Terminator is installed in a Spin socket and a READ event is dispatched by the reactor
then a LOAD event happens and the handle Terminator is processed.

~~~
READ -> Stdout => LOAD -(str:data)-> Terminator =(str:chk)=> Terminator.FOUND
~~~

### Calc Server (calc_server.py)

This example implements a simple application layer protocol that uses as token '\r\n' to separate meaningful
chunks of text. Clients would connect to the server by using a telnet then start sending commands to do
computations.

**Example of commands**

~~~
add 1 2 3
sub 0 2
div 4 2 2 4
~~~

The complete source code is listed below.

~~~python
from untwisted.network import core, Spin, xmap, spawn
from untwisted.iostd import Server, Stdin, Stdout, CLOSE, ACCEPT
from untwisted.splits import Terminator
from untwisted.tools import handle_exception
import operator

class CalcParser(object):
    def __init__(self, client):
        xmap(client, Terminator.FOUND, self.handle_found)

    @handle_exception(ValueError)
    def handle_found(client, data):
        op, args = data.split(' ', 1)
        args     = map(float, args.split(' '))
        spawn(client, op, args)

class CalcServer(object):
    """ 
    """

    def __init__(self, server):
        xmap(server, ACCEPT, self.handle_accept)

    def handle_accept(self, server, client):
        Stdin(client)
        Stdout(client)
        Terminator(client, delim='\r\n')
        parser = CalcParser(client)
        
        xmap(client, 'add', self. on_add)    
        xmap(client, 'sub', self.on_sub)    
        xmap(client, 'mul', self.on_mul)    
        xmap(client, 'div', self.on_div)    
        xmap(client, (parser.handle_found, ValueError), self.on_error)    

        xmap(client, CLOSE, self.handle_close)

    def on_add(self, client, args):
        self.send_msg(client, reduce(operator.add, args, 0))

    def on_sub(self, client, args):
        self.send_msg(client, reduce(operator.sub, args, 0))

    def on_div(self, client, args):
        self.send_msg(client, reduce(operator.div, args, args.pop(0)))

    def on_mul(self, client, args):
        self.send_msg(client, reduce(operator.mul, args, args.pop(0)))

    def on_error(self, client, excpt):
        self.send_msg(client, excpt)

    def handle_close(self, client, err):
        client.destroy()
        client.close()

    def send_msg(self, client, msg):
        client.dump('%s\r\n' % msg)

if __name__ == '__main__':
    server = Spin()
    server.bind(('', 1234))
    server.listen(5)

    Server(server)
    CalcServer(server)
    core.gear.mainloop()
~~~

The code below implements the handle CalcParser that is processed when Terminator.FOUND is processed.

~~~python
class CalcParser(object):
    def __init__(self, client):
        xmap(client, Terminator.FOUND, self.handle_found)

    @handle_exception(ValueError)
    def handle_found(client, data):
        op, args = data.split(' ', 1)
        args     = map(float, args.split(' '))
        spawn(client, op, args)
~~~

When one of the clients sends a message like:

~~~
cmd arg0 arg1 arg2 ...\r\n
~~~

The Terminator.FOUND event will be processed then handle_found will be processed and it will receive that string.
The string will be split using ' ' as token and the first chunk will turn into an event, the remaining chunks
will be converted to float numbers.

So, if one of the clients sends:

~~~
add 1 2
~~~

It will occur an event named 'add' and it will carry the arguments (1, 2). Whatever handle that is mapped to the event 'add'
will be processed. 

The handle_exception decorator is used to get an event-exception like (CalcParser.handle_found, ValueError). If
one of the clients sends a message like:

~~~
add 1 2 x
~~~

It will raise an exception ValueError inside handle_found then it will be turned into an event that can be trigged
by other handles. In the example, the event (CalcParser.handle_found, ValueError) was mapped to the handle on_error
that sends back the exception to the client.

The code below is used to destroy the Spin instance then close the underlying socket.

~~~python
    def handle_close(self, client, err):
        client.destroy()
        client.close()
~~~

Saving the file as calc_server.py and running it with:

~~~
python2 calc_server.py
~~~

Then connecting to the server with:

~~~
tee >(telnet localhost 1234)
Trying ::1...
Trying 127.0.0.1...
Connected to localhost.
Escape character is '^]'.
add 1 2
3.0
sub 2 -1
-1.0
div 2 2 2
0.5
add 2 x 0
could not convert string to float: x
add 1 0 2323
2324.0
add 2 0 lksjc
could not convert string to float: lksjc
~~~

Timers
======

Timers are a way to get handles executed after a given interval of time. 

Let us test how it works.

~~~python
Python 2.7.11 (default, Dec  6 2015, 15:43:46) 
[GCC 5.2.0] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> from untwisted.timer import Timer
>>> from untwisted import core
>>> 
>>> def handle(msg):
...     print msg
... 
>>> timer = Timer(10, handle, 'hello world')
>>> core.gear.mainloop()
hello world
~~~

The Timer object is used to execute a handle just once. It is possible to cancel the handle call by calling
the method Timer.cancel.

The Sched object is used to get a handle executed periodically.

~~~python
>>> from untwisted.timer import Sched
>>> from untwisted import core
>>> 
>>> def handle(msg):
...     print msg
... 
>>> timer = Sched(2, handle, 'hello world')
>>> core.gear.mainloop()
hello world
hello world
hello world
hello world
hello world
~~~

The exception CancelCall that is defined in the untwisted.timer module can be raised
in order to get the handle call canceled.

~~~python
from untwisted.timer import Sched, CancelCall
from untwisted import core

def handle(*args):
    if some_condition:
        raise CancelCall
    
timer = Sched(inc, handle, arg0, arg1, ...)
core.gear.mainloop()
~~~

Coroutines
==========

Untwisted coroutines are used from handles to stop code execution until a given event happens with some Dispatcher instance.

Let us play with untwisted coroutines from the interpreter.


~~~python
>>> from untwisted.dispatcher import Dispatcher
>>> from untwisted.tools import coroutine
>>> from untwisted.event import get_event
>>> 
>>> @coroutine
... def handle(dispatcher):
...     value, = yield dispatcher, 'cond0'
...     print 'Value:', value
...     value, = yield dispatcher, 'cond1'
...     print 'Value:', value
...     value, = yield dispatcher, 'cond2'
...     print 'Value:', value
... 
>>> 
>>> dispatcher = Dispatcher()
>>> handle(dispatcher)
>>> dispatcher.drive('cond0', 10)
Value: 10
>>> dispatcher.drive('cond1', 20)
Value: 20
>>> dispatcher.drive('cond2', 30)
Value: 30
>>> dispatcher.drive('cond0', 40)
>>> 
~~~

The handle function receives a dispatcher instance then uses the yield statement to wait for
incoming events from the dispatcher instance. When the events occur then the code is processed.

A more complicated example would be:

~~~python
>>> from untwisted.dispatcher import Dispatcher
>>> from untwisted.tools import coroutine
>>> from untwisted.event import LOAD, DUMPED
>>> 
>>> @coroutine
... def handle(dispatcher, number):
...     print 'coroutine started!'
...     while True:
...         value, = yield dispatcher, LOAD
...         if value > number:
...             break
...     print 'number', number
...     print 'Value:', value
... 
>>> dispatcher = Dispatcher()
>>> dispatcher.add_map(DUMPED, handle)
>>> dispatcher.drive(DUMPED, 20)
coroutine started!
>>> dispatcher.drive(LOAD, 10)
>>> dispatcher.drive(LOAD, 15)
>>> dispatcher.drive(LOAD, 30)
number 20
Value: 30
>>> 
~~~

When the event DUMPED is processed then handle is processed and it waits for the event LOAD
to happen from the dispatcher instance. When the LOAD happens then it checks whether the value it carried
matches the condition if it matches then it breaks the while loop.

### A simple chat server (chat_server.py)

The chat server source that is listed below is a neat example of how coroutines can turn into a powerful tool.

~~~python
from untwisted.network import core, Spin, xmap
from untwisted.iostd import create_server, ACCEPT, CLOSE, lose
from untwisted.splits import Terminator
from untwisted.tools import coroutine

class ChatServer(object):
    def __init__(self, server):
        xmap(server, ACCEPT, self.handle_accept)
        self.pool = []

    @coroutine
    def handle_accept(self, server, client):
        Terminator(client, delim='\r\n')
        xmap(client, CLOSE, lambda client, err: self.pool.remove(client))

        client.dump('Type a nick.\r\nNick:')    
        client.nick, = yield client, Terminator.FOUND

        xmap(client, Terminator.FOUND, self.echo_msg)
        self.pool.append(client)

    def echo_msg(self, client, data):
        for ind in self.pool:
            if not ind is client:
                ind.dump('%s:%s\r\n' % (client.nick, data))

if __name__ == '__main__':
    server = create_server('', 1234, 5)
    ChatServer(server)
    core.gear.mainloop()
~~~

When clients connect to the server it asks for a nickname to be sent. The implementation uses untwisted coroutines
to wait for a Terminator.FOUND event to set the user's nickname to its corresponding Spin instance.

After the nick being set in the user socket instance then it maps the event Terminator.FOUND to the method echo_msg
that echoes any msg to other users.

**Testing**

Run the chat server with:

~~~
python chat_server.py
~~~

Connect from a telnet with:

~~~
telnet 'localhost' 1234
~~~

Threads
=======

Untwisted reactor is implemented on top of a non blocking design that uses  select, poll 
functions to wait for I/O completion. The code that is being executed in the untwisted reactor thread can't
hang otherwise the reactor scales poorly. In situations where heavy computations need to be done it is
needed to use threads.

### Job class

The job class constructor takes a function that is executed inside a new thread.

### A basic example (sum.py)

The example below spawns some threads that perform simple calculations.

~~~python
from untwisted.network import core, xmap
from untwisted.job import Job, DONE
import time

def sum(x, y):
    time.sleep(3)
    return x + y

def show(job, result):
    print result

for ind in xrange(100):
    job = Job(sum, ind, 1000)
    xmap(job, DONE, show)

core.gear.mainloop()
~~~

The function sum is called with two arguments then processed in a new thread when it returns the show function
is called with the sum return value and the Job instance.

Spawning processes
==================

Processes are created with the Expect class it uses threads to read and write to the process.


### Expect class

The expect class takes the name of the process and arguments it should be started witn. It inherits from Dispatcher
as well.

~~~python
expect = Expect('process_name', 'arg0', 'arg1', ...)
~~~

### A basic example (spawn_process.py)

~~~python
from untwisted.expect import Expect, LOAD, CLOSE
from untwisted.network import core, xmap, die

def handle(expect, data):
    print data

expect = Expect('python', '-i', '-u')
xmap(expect, LOAD, handle)
xmap(expect, CLOSE, lambda expect: die())
expect.send('print "hello world"\nquit()\n')
core.gear.mainloop()
~~~

Whenever the event LOAD happens it means that the process has output then handle is called with
the available data. If the process dies then the event CLOSE happens and the reactor is stopped
through the function die.

Tasks
=====

When dealing with socket events it may be needed to have a handle called when a given set of events occurs.
Untwisted implements the Task class to handle situations like that.

~~~
{event0, event1, event2, ... } -> *handle
~~~

That means when one of the events described in the set is processed then handle is called just once.

### Task class

The Task class inherits from Dispatcher class and implements a method named add. The method add receives
a Dispatcher instance and a sequence of events. The sequence of events specifies which events when processed 
it should get the handle processed.

~~~python
>>> from untwisted.dispatcher import Dispatcher
>>> from untwisted.task import Task, DONE
>>> 
>>> def on_done(task):
...     print 'it is done.'
... 
>>> 
>>> dispatcher = Dispatcher()
>>> task       = Task()
>>> task.add(dispatcher, 'event0', 'event1', 'event2')
>>> task.add_map(DONE, on_done)
>>> task.count
1
>>> dispatcher.drive('event4')
>>> dispatcher.drive('event0')
it is done.
>>> dispatcher.drive('event1')
>>> dispatcher.drive('event2')
>>> 
~~~

When the event 'event4' is processed then nothing happens, when the event 'event0' is processed
then the handle on_done is called. If the events 'event1', 'event2' had been processed then on_done
would be called as well.

Let us try something new.

~~~python
>>> def on_done(task):
...     print 'DONE'
... 
>>> sock0 = Dispatcher()
>>> sock1 = Dispatcher()
>>> task  = Task()
>>> task.add(sock0, 'load', 'close')
>>> task.add(sock1, 'load', 'close')
>>> task.add_map(DONE, on_done)
>>> task.count
2
>>> sock0.drive('load')
>>> task.count
1
>>> sock1.drive('close')
DONE
>>> task.count
0
>>> 
~~~

### A Port Scan (port_scan.py)

The example below implements a port scan.

~~~python
from untwisted.network import core, Spin, xmap
from untwisted.iostd import Client, lose, CONNECT, CONNECT_ERR
from untwisted.task import Task, DONE
from untwisted.network import die
from socket import *

def is_open(spin, port):
    print 'Port %s is open.' % port

def create_connection(addr, port):
    sock = socket(AF_INET, SOCK_STREAM)
    spin = Spin(sock)
    Client(spin)
    xmap(spin, CONNECT, is_open, port)
    spin.connect_ex((addr, port))
    return spin

def scan(addr, min, max):
    task = Task()
    for ind in xrange(min, max):
        task.add(create_connection(addr, ind), CONNECT, CONNECT_ERR)
    
    xmap(task, DONE, lambda task: die())

if __name__ == '__main__':
    from optparse import OptionParser
    parser   = OptionParser()
    parser.add_option("-a", "--addr", dest="addr", metavar="string", default='localhost')
    parser.add_option("-x", "--max", dest="max", metavar="integer", default=9999)
    parser.add_option("-n", "--min", dest="min", metavar="integer", default=70)

    (opt, args) = parser.parse_args()
    scan(opt.addr, int(opt.min), int(opt.max))
    core.gear.mainloop()
~~~

It uses the Task class to determine when all the opened connections spawned either CONNECT or CONNECT_ERR.
When all the opened connections spawned one of the two events then it is time to stop the reactor with the function die.

**Running**

~~~
python2 portscan.py -a www.google.com -x 90 -n 70
~~~

The command above would scan the range of ports from 70 to 90.

Reactor flow control
====================

The ways to control the reactor flow, it is through raising exceptions.

### The Root exception

The Root exception is used to avoid other events/handles from being processed in the actual event chain after a given condition
is satisfied.

~~~
from untwisted.core import Root

def handle0(spin):
    raise Root

def handle1(spin):
    print 'It will not be printed'

xmap(spin, WRITE, handle0)
xmap(spin, WRITE, handle1)
~~~

### The Kill exception

The Kill exception is used to stop the reactor from processing remaining events.

~~~python
from untwisted.core import Kill

def handle(spin):
    raise Kill

core.gear.mainloop()
~~~

The requests plugin
===================

The requests plugin is an implementation of the HTTP protocol over the client side perspective. It is possible
to spawn multiple requests asynchronously.

### HTTP GET 

Untwisted requests plugin uses its get function to perform a HTTP GET request. The example below
examplifies:

#### Basic HTTP GET example (snake.py)

~~~python
from untwisted.plugins.requests import get, HttpResponseHandle
from untwisted.network import xmap, core

def on_done(con, response):
    print response.headers
    print response.code
    print response.version
    print response.reason 
    print response.fd.read()

if __name__ == '__main__':
    urls = ['www.bol.uol.com.br', 'www.google.com']
    
    for ind in urls:
        con = get(ind, 80, '/')
        xmap(con, HttpResponseHandle.HTTP_RESPONSE, on_done)
    core.gear.mainloop()

~~~

The get function returns a Spin object that corresponds to the web server connection. When the response
has arrived then an event HttpResponseHandle.HTTP_RESPONSE happens in the Spin object that was returned by
the get function.

### HTTP POST 

The next example shows how to perform a HTTP POST request using untwisted requests plugin. The implementation
is trivial.

#### Basic HTTP POST example (codepad.py)

~~~python
from untwisted.plugins.requests import HttpResponseHandle, post
from untwisted.network import Spin, xmap, core, die
import argparse

def on_done(spin, response):
    print 'URL:%s' % response.headers['location']
    die()

if __name__ == '__main__':
    parser= argparse.ArgumentParser()
    parser.add_argument('-f', '--filename',  default='0.0.0.0', help='filename')
    parser.add_argument('-t', '--type',  default='Plain Text', 
                                help='Type should be Python, Haskell, etc..')
    parser.add_argument('-r', '--run',  action='store_true', help='run')
    args = parser.parse_args()

    fd   = open(args.filename, 'r')
    code = fd.read()
    fd.close()

    payload = {
                    'code':code,
                    'lang':' '.join(map(lambda ind: ind.capitalize(), 
                                        args.type.split(' '))),
                    'submit':'Submit',
                    'run': args.run
              }
    
    con = post('codepad.org', 80, '/', payload)
    xmap(con, HttpResponseHandle.HTTP_RESPONSE, on_done)
    core.gear.mainloop()
~~~

**Example:**

~~~
[tau@lambda requests]$ python2 codepad.py -f snake.py -t python --run
URL: http://codepad.org/HfJoaeJn

~~~

The IRC Client plugin
=====================

Untwisted implements an abstraction for the IRC protocol under the client side perspective. The set of tools
provided by untwisted turns it a joyful task to implement IRC Clients, IRC Bots etc.

### IRC Events

The server messages follow a defined pattern, these messages transmit events whose purpose is notifying the client of 
random happenings and replying to the client's actions. When an user sends a command like:

~~~
JOIN #channel
~~~

The server will send back a message that notifies the user of it joining the channel or not.

Consider the following messages sent by an irc server through a Spin instance.

~~~
irc.server.name WHOIS foo
irc.server.name 311 bar foo ~Ident name-B21D62.lolhat.com :Foo Jenkins
irc.server.name 319 bar foo :+#foobar @#kekelar %#scripting
irc.server.name 312 bar foo irc.server.name :Server Description
irc.server.name 307 bar foo :has identified for this nick
irc.server.name 335 bar foo :is a Bot on name 
irc.server.name 671 bar foo :is using a Secure Connection
irc.server.name 318 bar foo :End of /WHOIS list.
~~~

The IRC server messages are parsed by untwisted irc plugin then turned into string events. The events occur in the Spin
instance of the server connection. In the examplle above, there would occur the events '311', '319', '307', '335', '671', '318'.


### A basic example (funbot.py)

~~~python
from untwisted.network import xmap, Spin, core
from untwisted.iostd import CLOSE, LOAD, CONNECT, CONNECT_ERR, Stdout, Stdin, Client, lose
from untwisted.splits import Terminator, logcon
from untwisted.plugins.irc import Irc, send_cmd, send_msg
from socket import *

class FunBot(object):
    """ Bot class """
    def __init__(self, ip, port, nick, user, password, *chan_list):
        """ It sets up the bot instance. """
        sock = socket(AF_INET, SOCK_STREAM)

        # We have to wrap our socket with a Spin instance
        # in order to have our events issued when data comes
        # from the socket.
        con = Spin(sock)
        
        # This protocol is required by uxirc.irc protocol.
        # It spawns CONNECT.
        Client(con)

        # We use connect_ex since we do not want an exception.
        # Untwisted uses non blocking sockets.
        con.connect_ex((ip, port))

        # We save whatever we might need.
        self.nick      = nick
        self.user      = user
        self.password  = password
        self.chan_list = chan_list
        self.ip        = ip
        self.port      = port

        # It maps CONNECT to self.send_auth so
        # when our socket connects it sends NICK and USER info.
        xmap(con, CONNECT, self.send_auth)
        xmap(con, CONNECT_ERR, lambda con, err: lose(con))

    def send_auth(self, con):
        # It is what we use to send data. send_msg function uses
        # spin.dump function to dump commands.
        Stdin(con)

        # Shrug protocols requires Stdout that spawns LOAD
        # when data arrives. 
        Stdout(con)

        # This protocol spawns FOUND whenever it finds \r\n.
        Terminator(con)

        Irc(con)
        
        xmap(con, CLOSE, lambda con, err: lose(con))

        # Now, it basically means: when it '376' irc command is
        # issued by the server then calls self.auto_join.
        # We use auto_join to send the sequence of JOIN
        # commands in order to join channels.
        xmap(con, '376', self.auto_join)

        # Below the remaining stuff follows the same pattern.
        xmap(con, 'JOIN', self.on_join)
        xmap(con, 'PING', self.on_ping)
        xmap(con, 'PART', self.on_part)
        xmap(con, '376', self.on_376)
        xmap(con, 'NOTICE', self.on_notice)
        xmap(con, 'PRIVMSG', self.on_privmsg)
        xmap(con, '332', self.on_332)
        xmap(con, '001', self.on_001)
        xmap(con, '001', self.on_002)
        xmap(con, '003', self.on_003)
        xmap(con, '004', self.on_004)
        xmap(con, '333', self.on_333)
        xmap(con, '353', self.on_353)
        xmap(con, '366', self.on_366)
        xmap(con, '474', self.on_474)
        xmap(con, '302', self.on_302)


        send_cmd(con, 'NICK %s' % self.nick)
        send_cmd(con, 'USER %s' % self.user)
        send_msg(con, 'nickserv', 'identify %s' % self.password)

    def auto_join(self, con, *args):
        for ind in self.chan_list:
            send_cmd(con, 'JOIN %s' % ind)

    def on_ping(self, con, prefix, servaddr):
        # If we do not need pong we are disconnected.
        print 'on_ping', (prefix, servaddr)
        reply = 'PONG :%s\r\n' % servaddr
        send_cmd(con, reply)
        
    def on_join(self, con, nick, user, host, chan):
        print 'on_join\n', (nick, user, host, chan)

    def on_part(self, con, nick, user, host, chan):
        print 'on_part\n', (nick, user, host, chan)

    def on_privmsg(self, con, nick, user, host, target, msg):
        print 'on_privmsg\n', (nick, user, host, target, msg)

    def on_332(self, con, prefix, nick, chan, topic):
        print 'on_332\n', (prefix, nick, chan, topic)

    def on_302(self, con, prefix, nick, info):
        print 'on_302\n', (prefix, nick, info)

    def on_333(self, con, prefix, nick_a, chan,  nick_b, ident):
        print 'on_333\n', (prefix, nick_a, chan, nick_b, ident)

    def on_353(self, con, prefix, nick, mode, chan, peers):
        print 'on_353\n', (prefix, nick, mode, chan, peers)

    def on_366(self, con, prefix, nick, chan, msg):
        print 'on_366\n', (prefix, nick, chan, msg)

    def on_474(self, con, prefix, nick, chan, msg):
        print 'on_474\n', (prefix, nick, chan, msg)

    def on_376(self, con, prefix, nick, msg):
        print 'on_376\n', (prefix, nick, msg)

    def on_notice(self, con, prefix, nick, msg, *args):
        print 'on_notice\n', (prefix, nick, msg), args

    def on_001(self, con, prefix, nick, msg):
        print 'on_001\n', (prefix, nick, msg)

    def on_002(self, con, prefix, nick, msg):
        print 'on_002\n', (prefix, nick, msg)

    def on_003(self, con, prefix, nick, msg):
        print 'on_004\n', (prefix, nick, msg)

    def on_004(self, con, prefix, nick, *args):
        print 'on_004\n', (prefix, nick, args)
    
    def on_005(self, con, prefix, nick, *args):
        print 'on_005', (prefix, nick, args)

bot = FunBot('irc.freenode.com', 6667, 'Fourier1', 'kaus keus kius :kous', '', '##calculus')
core.gear.mainloop()
~~~

The lines below are responsible by doing the basic imports.

~~~python
from untwisted.network import xmap, Spin, core
from untwisted.iostd import CLOSE, LOAD, CONNECT, CONNECT_ERR, Stdout, Stdin, Client, lose
from untwisted.splits import Terminator, logcon
from untwisted.plugins.irc import Irc, send_cmd, send_msg
from socket import *
~~~

Notice the import:

~~~python
from untwisted.plugins.irc import Irc, send_cmd, send_msg

~~~

The Irc class is responsible by parsing the IRC server messages and turning these into events in the Spin instance of the server.

The constructor of the Funbot class takes arguments that are needed to instantiate the connection and a list of strings
that maps to the IRC channels to get in after the connection is stabilished and the MOTD is sent.

~~~python
    def __init__(self, ip, port, nick, user, password, *chan_list):
        """ It sets up the bot instance. """
        sock = socket(AF_INET, SOCK_STREAM)

        # We have to wrap our socket with a Spin instance
        # in order to have our events issued when data comes
        # from the socket.
        con = Spin(sock)
        
        # This protocol is required by uxirc.irc protocol.
        # It spawns CONNECT.
        Client(con)

        # We use connect_ex since we do not want an exception.
        # Untwisted uses non blocking sockets.
        con.connect_ex((ip, port))

        # We save whatever we might need.
        self.nick      = nick
        self.user      = user
        self.password  = password
        self.chan_list = chan_list
        self.ip        = ip
        self.port      = port

        # It maps CONNECT to self.send_auth so
        # when our socket connects it sends NICK and USER info.
        xmap(con, CONNECT, self.send_auth)
        xmap(con, CONNECT_ERR, lambda con, err: lose(con))
~~~

When the event CONNECT happens then the method of the class Funbot will be processed. Once it is processed
then the Stdin, Stdout, and Irc handles are installed in the Spin instance of the server. 

~~~python
    def send_auth(self, con):
        # It is what we use to send data. send_msg function uses
        # spin.dump function to dump commands.
        Stdin(con)

        # Shrug protocols requires Stdout that spawns LOAD
        # when data arrives. 
        Stdout(con)

        # This protocol spawns FOUND whenever it finds \r\n.
        Terminator(con)

        Irc(con)
        
        xmap(con, CLOSE, lambda con, err: lose(con))

        # Now, it basically means: when it '376' irc command is
        # issued by the server then calls self.auto_join.
        # We use auto_join to send the sequence of JOIN
        # commands in order to join channels.
        xmap(con, '376', self.auto_join)

        # Below the remaining stuff follows the same pattern.
        xmap(con, 'JOIN', self.on_join)
        xmap(con, 'PING', self.on_ping)
        xmap(con, 'PART', self.on_part)
        xmap(con, '376', self.on_376)
        xmap(con, 'NOTICE', self.on_notice)
        xmap(con, 'PRIVMSG', self.on_privmsg)
        xmap(con, '332', self.on_332)
        xmap(con, '001', self.on_001)
        xmap(con, '001', self.on_002)
        xmap(con, '003', self.on_003)
        xmap(con, '004', self.on_004)
        xmap(con, '333', self.on_333)
        xmap(con, '353', self.on_353)
        xmap(con, '366', self.on_366)
        xmap(con, '474', self.on_474)
        xmap(con, '302', self.on_302)


        send_cmd(con, 'NICK %s' % self.nick)
        send_cmd(con, 'USER %s' % self.user)
        send_msg(con, 'nickserv', 'identify %s' % self.password)
~~~

Notice the event 'PING' is mapped to the method self.on_ping.

~~~python
    def on_ping(self, con, prefix, servaddr):
        # If we do not need pong we are disconnected.
        print 'on_ping', (prefix, servaddr)
        reply = 'PONG :%s\r\n' % servaddr
        send_cmd(con, reply)

~~~

It is needed to reply to the server with a PONG otherwise the client gets disconnected.

The event '376' corresponds to the end of motd, whenn such an event occurs then the handle:

~~~python
    def auto_join(self, con, *args):
        for ind in self.chan_list:
            send_cmd(con, 'JOIN %s' % ind)
~~~

That sends the commands to get the user joined in the previous defined list of channels.

**Running funbot.py**

Once running the bot with.

~~~
python2 funbot.py
~~~

The output will be something similar to:

~~~
[tau@lambda irc]$ python2 -u funbot.py
on_notice
('tepper.freenode.net', '*', '*** Looking up your hostname...') ()
on_notice
('tepper.freenode.net', '*', '*** Checking Ident') ()
on_notice
('tepper.freenode.net', '*', '*** No Ident response') ()
on_notice
('tepper.freenode.net', '*', "*** Couldn't look up your hostname") ()
on_001
('tepper.freenode.net', 'Fourier1', 'Welcome to the freenode Internet Relay Chat Network Fourier1')
on_002
('tepper.freenode.net', 'Fourier1', 'Welcome to the freenode Internet Relay Chat Network Fourier1')
on_004
('tepper.freenode.net', 'Fourier1', 'This server was created Thu Jun 18 2015 at 19:57:19 UTC')
on_004
('tepper.freenode.net', 'Fourier1', ('tepper.freenode.net', 'ircd-seven-1.1.3', 'DOQRSZaghilopswz', 'CFILMPQSbcefgijklmnopqrstvz', 'bkloveqjfI'))
on_376
('tepper.freenode.net', 'Fourier1', 'End of /MOTD command.')
on_join
('Fourier1', '~kaus', '189.84.255.251', '##calculus')
on_332
('tepper.freenode.net', 'Fourier1', '##calculus', 'If you have a question, ask and be patient. | Sharing: http://mathb.in http://www.twiddla.com | Reference: http://mathworld.wolfram.com http://www.encyclopediaofmath.org http://www.proofwiki.org')
on_333
('tepper.freenode.net', 'Fourier1', '##calculus', 'Hafydd', '1441090725')
on_353
('tepper.freenode.net', 'Fourier1', '=', '##calculus', 'Fourier1 tau chaosflaws MKCoin WaffleZ stux|RC-only tumdedum dualbus minsky Hafydd')
on_366
('tepper.freenode.net', 'Fourier1', '##calculus', 'End of /NAMES list.')
on_notice
('NickServ', 'NickServ', 'services.') ('Fourier1', 'Insufficient parameters for \x02IDENTIFY\x02.')
on_notice
('NickServ', 'NickServ', 'services.') ('Fourier1', 'Syntax: IDENTIFY [nick] <password>')
on_ping (None, 'tepper.freenode.net')
on_ping (None, 'tepper.freenode.net')
on_ping (None, 'tepper.freenode.net')
on_ping (None, 'tepper.freenode.net')
on_ping (None, 'tepper.freenode.net')
on_ping (None, 'tepper.freenode.net')
~~~

IRC messages are turned into events that carry arguments. The arguments are passed to the handles in the exact order that they appear in the messages.







