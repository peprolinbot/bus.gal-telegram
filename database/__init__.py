from datetime import datetime

from .models import Base, User, Stop, Expedition

def _api_stop_to_database_stop(stop):
    stop = Stop(id=stop.id, name=stop.name, type=stop.type, type_id=stop.type_id)

    return stop

def get_user(session, user_id):
    user = (
        session.query(User)
        .filter(User.id == user_id)
        .one_or_none()
    )

    return user

def add_user(session, user_id):
    user = User(id=user_id)
    session.add(user)

    session.commit()

def get_favorite_stops(session, user_id):
    user = get_user(session, user_id)
    
    return user.favorite_stops

def add_favorite_stop(session, user_id, stop):
    user = get_user(session, user_id)
    stop = session.query(Stop).filter(Stop.id == stop.id).one_or_none() or _api_stop_to_database_stop(stop)
    user.favorite_stops.append(stop)
    
    session.commit()

def delete_favorite_stop(session, user_id, stop):
    user = get_user(session, user_id)
    favorite_stops = user.favorite_stops
    for favorite_stop in favorite_stops:
        if favorite_stop.id == stop.id:
            favorite_stops.remove(favorite_stop)
            break

    session.commit()

def get_cached_stops(session, user_id):
    user = get_user(session, user_id)
    
    return user.cached_stops

def add_cached_stop(session, user_id, stop):
    user = get_user(session, user_id)
    stop = session.query(Stop).filter(Stop.id == stop.id).one_or_none() or _api_stop_to_database_stop(stop)
    user.cached_stops.append(stop)
    
    session.commit()

def add_multiple_cached_stops(session, user_id, stops):
    user = get_user(session, user_id)
    for stop in stops:
        stop = session.query(Stop).filter(Stop.id == stop.id).one_or_none() or _api_stop_to_database_stop(stop)
        user.cached_stops.append(stop)
    
    session.commit()

def delete_cached_stop(session, user_id, stop):
    user = get_user(session, user_id) 
    cached_stops = user.cached_stops
    for cached_stop in cached_stops:
        if cached_stop.id == stop.id:
            cached_stops.remove(cached_stop)
            break

    session.commit()

def delete_all_cached_stops(session, user_id):
    user = get_user(session, user_id) 
    user.cached_stops = []
    
    session.commit()

def insert_to_expedition(session, user_id, origin=None, destination=None, date=None):
    user = get_user(session, user_id)
    expedition = user.expedition

    if expedition is None:
        session.add(Expedition(user_id=user_id))
        session.commit()
        user = get_user(session, user_id)
        expedition = user.expedition

    if not origin is None:    
        stop = session.query(Stop).filter(Stop.id == origin.id).one_or_none() or _api_stop_to_database_stop(origin)
        expedition.origin = stop

    elif not destination is None:      
        stop = session.query(Stop).filter(Stop.id == destination.id).one_or_none() or _api_stop_to_database_stop(destination)
        expedition.destination = stop
    
    elif not date is None:
        expedition.date = date.strftime("%d-%m-%Y") # Only day matters
    
    session.commit()

def delete_expedition(session, user_id):
    user = get_user(session, user_id)
    session.delete(user.expedition)

    session.commit()

def get_expedition(session, user_id):
    user = get_user(session, user_id)
    expedition = user.expedition
    if expedition is None:
        return None
    date = expedition.date
    if not date is None:
        date = datetime.strptime(expedition.date, "%d-%m-%Y")
    return_expedition = Expedition(user_id=expedition.user_id, origin_id=expedition.origin_id, origin=expedition.origin, destination_id=expedition.destination_id, destination=expedition.destination, date=date)

    return return_expedition

def set_state(session, user_id, state):
    possible_states = ["main_menu", "favorites_menu", "search_menu", "stop_menu"]
    if not state in possible_states:
        raise Exception(f"State msut be one of the following: {', '.join(possible_states)}")
    
    user = get_user(session, user_id)
    user.state = state

    session.commit()

def get_state(session, user_id):
    user = get_user(session, user_id)

    return user.state

def delete_everything_from_user(session, user_id):
    user = get_user(session, user_id)
    session.delete(user)

    session.commit()