def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]
    return inner

jour_semaine = {'0':'dimanche',
                '1':'lundi',
                '2':'mardi',
                '3':'mercredi',
                '4':'jeudi',
                '5':'vendredi',
                '6':'samedi'}
cate_map = {
        1: 'Expositions',
        2: 'Animations',
        3: 'Spectacles',
        4: 'Événements',
        5: 'Concerts'}
