import eel
from engine import Vector, Kinematics, Particle, Ensemble, Force, Field, Engine
from engine.util.typing import Object
from engine.subatomic import SubatomicEngine

WEB_ROOT = 'web'
WEB_FILENAME = 'index.html'

@eel.expose
def engineBegin() -> None:
    global subatomic
    subatomic = SubatomicEngine()
    
    #test
    subatomic.add_proton((0, 0, 0))
    subatomic.add_electron((2e-15, 0, 0))

PLANCK_SECOND = 1e-45

@eel.expose()
def engineAnimate(t: float) -> None:
    subatomic.animate(t * PLANCK_SECOND)

@eel.expose
def getEngine() -> dict:
    return subatomic.dumps()

@eel.expose
def getEngineAndAnimate(t: float) -> dict:
    engineAnimate(t)
    return getEngine()

if __name__ == '__main__':
    eel.init(WEB_ROOT)
    eel.start(WEB_FILENAME, port = 8000)