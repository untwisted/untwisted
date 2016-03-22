Untwisted Framework
===================

What can i create with untwisted?
=================================

Untwisted plugins
=================

How to read this book?
======================

The rapidserv plugin
====================

Rapidserv is a micro web framework that is built on top of a powerful asynchronous networking library. It shares with flask
some similarities in the design of the applications that are built on top of Rapidserv. Rapidserv is non blocking network I/O
consequently it can scale a lot of connections and it is ideal for some applications. 
Rapidserv uses jinja2 although it doesn't enforce the usage.

### A simple application

### The basic dir structure 

#### Static files

#### Template files

### Application setup

### View functions

#### The Rapidserv.route decorator

#### The Rapidserv.request decorator

#### The Rapidserv.accept decorator

### Responses

### Redirects

### Errors

### Rendering templates

### Sessions

### Routers

### The quote web app

The requests plugin
===================

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

The diagram below examplifies the scheme:
    
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

When a given handle is called it will process the event arguments and eventually it may occur an exception inside the handle.
The event loop can't stop due to that exception being raised because it is advantageous under some perspectives
to keep the reactor processing other events. There will exist situations that it will not be advantageous to keep
the reactor processing a given list of handles for a given event, in that case there are specific exceptions
that can be raised to change the flow of the events it means avoiding some events to occur or having more
events to occur. So, in untwisted, the flow of the events can be controlled with a set of specific exceptions.

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

Using this approach it is possible to describe reasonably well almost all philosophical entities that can be built
in order to understand the reality surrounding our mind senses. However, we'll be interested in specific objects
when using untwisted, these are sockets, threads, processes etc. It is interesting notice that handles can be 
seen as events and vice versa. 

### Related objects

### Adding dynamically mappings to objects

### Domain of handles

### Image of handle events

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

The methods 'add_map' and 'del_handle' are the most used ones. These methods are used to bind handles to events that
are related to the given Dispatcher object. 

As handles and events are related to objects, objects may be related between each other in some way. A given object
may change the state of other object then an event happens. The method 'drive' of the Dispatcher class is used
to fire an event in the Dispatcher object. Once an event is fired in a given Dispatcher object then all handles associated
with that event will be processed. As mentioned before, events can carry arguments that better characterize the event,
the 'drive' method permits to fire events with a given set of arguments associated to the event.

~~~python
dispatcher.drive('RAINING', 'Brasil', 'Rio de Janeiro', 'Rio das ostras')
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

The above code adds a mapping between the event 'RAINING' and the callback 'handle0'. Now if the event 'RAINING'
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

There is a other way to add a mapping between an event and a handle to a Dispatcher object it is
using the xmap function. This function is merely a synonymous for 'add_map'.

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

The reasons to use 'xmap' function instead of add_map are aestheticals. 
The same occurs when firing events.

~~~python
>>> spawn(dispatcher, 'ALPHA')
Event ALPHA occured
>>> spawn(dispatcher, 'BETA', 'arg1', 'arg2', 'arg3')
>>> 
~~~

### Event creation

Events can be any kind of python objects but it is interesting to have a reliable scheme 
to define new events. Untwisted implements the 'get_event' function that returns a unique event.

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
from untwisted.dispatcher import Dispatcher, xmap, spawn
from untwisted.event import LOAD

dispatcher = Dispatcher()

def on_load(dispatcher, data):
    cmd = data.split(' ')
    spawn(dispatcher, cmd.pop(0), cmd)

dispatcher.add_map(LOAD, on_load)
~~~

The code above corresponds to:

~~~
dispatcher {
    LOAD -(data)-> on_load -(args)-> $cmd

}
~~~

Where $cmd may be any python string that is carried by LOAD and processed by on_load handle.
Let us drive a LOAD event inside that dispatcher object.  

~~~python

>>> def on_add(dispatcher, args):
...     print 'Sum:', sum(map(int, args))
... 
>>> dispatcher.add_map('add', on_add)
>>> dispatcher.drive(LOAD, 'add 1 1 2')
Sum: 4
~~~

It creates a new handle named 'on_add' and maps it to the event 'add'.
The dispatcher object with the mappings previously defined should look like.

~~~
dispatcher {
    LOAD -(data)-> on_load -(args)-> $cmd
    $cmd('add') -(args)-> on_add
~~~

The symbol below means that 'cmd' is an event variable that can assume the value 'add' 
and when such an event occurs then the handle 'on_add' is processed.

~~~
$cmd('add') -(args)-> on_add
~~~

it is interesting notice that the diagram below is equivalent to the above but not describe
all the system.

~~~
dispatcher {
    LOAD -(data)-> on_load -(args)-> $cmd
    'add' -(args)-> on_add
~~~

The same occurs with:

~~~
dispatcher {
    LOAD -> on_load -> $cmd
    'add' -> on_add
}
~~~

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

### Exceptions in handles

### Dispatcher flow control

### Static handles

### binding static handles to events

### Unbinding static handles to events

Super socket class
==================

Spin class
==========

Reactors
========

### Select 

### Epoll

### Poll

Reactor mainloop
================

Reactor flow control
====================

Basic events
============

Basic built-in handles
======================

Internet protocol events
========================

Clients
=======

Servers
=======

Timers
======

Coroutines
==========

Tasks
=====

SSL Clients
===========

SSL Servers
===========

Threads
=======

Spawning processes
==================

The IRC Client plugin
=====================

Debugging
=========

Tests
=====







