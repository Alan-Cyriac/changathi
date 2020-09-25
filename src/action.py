
class Utter_greet:
    def run(self):
        return "Hi"

class Utter_askname:
    def run(self):
        return "Please give name:"

class Utter_askclass:
    def run(self):
        return "Which class?"

class Utter_askdivision:
    def run(self):
        return "Which division?"

class Utter_start:
    def run(self):
        return 0

class Utter_restart:
    def run(self):
        return 1
class Utter_stop:
    def run(self):
        return 2

class Utter_action_listner:
    def run(self):
        return 3
class Response:
    def actions(self, response):
        switcher={
                0:Utter_start().run(),
                1:Utter_restart().run() ,
                2:Utter_stop().run() ,
                3:Utter_action_listner().run() ,
                4:Utter_greet().run() ,
                5:Utter_askname().run() ,
                6:Utter_askclass().run() ,
                7:Utter_askdivision().run() 
             }
        return switcher.get(response,"Select from the available item number please.")       

