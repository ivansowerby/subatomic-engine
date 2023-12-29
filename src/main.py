import eel
from engine import Vector, Kinematics, Particle, Ensemble, Force, Field, Engine
from engine.subatomic import SubatomicEngine

WEB_ROOT = 'web'
WEB_FILENAME = 'index.html'

@eel.expose
def engineBegin() -> None:
    global subatomic
    subatomic = SubatomicEngine()

if __name__ == '__main__':
    eel.init(WEB_ROOT)
    eel.start(WEB_FILENAME, port = 8000)
