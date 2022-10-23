class Session():
    
    def __init__(self):
        self.sessions_id = []

    def id_is_already(self, id):
        for i in self.sessions_id:
            if id == i[0]:
                return True
        return False

    def set_id_and_password(self, id_session, password_session):
        self.sessions_id.append([id_session, password_session])
    def del_id_and_password(self, id_and_session):
        self.sessions_id.remove(id_and_session)