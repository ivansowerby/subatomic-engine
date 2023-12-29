from typing import Union
from engine import Vector, Particle, Ensemble, Engine
from engine.formula import gravity, electrostatic
from engine.util.typing import Number, Array

#by inheritance
class SubatomicEngine(Engine):
    def __init__(self, precision: int = 50) -> None:
        super().__init__(precision)
        self.gravitational_field = self.add_field(
            'gravity',
            formula = gravity,
            units = 'kg'
        )
        self.electrostatic_field = self.add_field(
            'electrostatic',
            formula = electrostatic,
            units = 'C'
        )

        self.proton_ensemble = self.add_simple_ensemble(
            name = 'proton',
            mass = 1.673e-27,
            charge = 1.6e-19
        )
        self.neutron_ensemble = self.add_simple_ensemble(
            name = 'neutron',
            mass = 1.675e-27
        )
        self.electron_ensemble = self.add_simple_ensemble(
            name = 'electron',
            mass = 9.11e-31,
            charge = -1.6e-19
        )

    def add_simple_ensemble(
            self,
            name: str,
            mass: Number,
            charge: Number = 0
        ) -> Ensemble:
        if mass == 0: raise ValueError
        forces = [self.gravitational_field.has(mass)]
        if charge != 0 or charge != None:
            forces.append(self.electrostatic_field.has(charge))
        return self.add_ensemble(
            name,
            tuple(forces)
        )
    
    def add_proton(self, position: Union[Vector, Array]) -> Particle:
        return self.add_particle(position, ensemble = self.proton_ensemble)
    
    def add_neutron(self, position: Union[Vector, Array]) -> Particle:
        return self.add_particle(position, ensemble = self.neutron_ensemble)

    def add_electron(self, position: Union[Vector, Array]) -> Particle:
        return self.add_particle(position, ensemble = self.electron_ensemble)
