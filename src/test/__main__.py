from engine import Vector, Engine
from engine.formula import gravity, electrostatic

if __name__ == '__main__':
    engine = Engine()

    #gravity
    gravitational_field = engine.add_field(
        'gravity',
        formula = gravity,
        units = 'kg'
    )
    #electrostatic
    electrostatic_field = engine.add_field(
        'electrostatic',
        formula = electrostatic,
        units = 'C'
    )

    #proton group
    proton_mass = gravitational_field.has(magnitude = 1.673e-27)
    proton_charge = electrostatic_field.has(magnitude = 1.6e-19)
    proton_ensemble = engine.add_ensemble(
        name = 'proton',
        forces = (proton_mass, proton_charge)
    )

    #neutron group
    neutron_mass = gravitational_field.has(magnitude = 1.675e-27)
    neutron_ensemble = engine.add_ensemble(
        name = 'neutron',
        forces = neutron_mass
    )

    #electron group
    electron_mass = gravitational_field.has(magnitude = 9.11e-31)
    electron_charge = electrostatic_field.has(magnitude = -1.6e-19)
    electron_ensemble = engine.add_ensemble(
        name = 'electron',
        forces = (electron_mass, electron_charge)
    )

    #init
    proton = engine.add_particle(
        Vector(0, 3),
        ensemble = proton_ensemble
    )
    electron = engine.add_particle(
        Vector(3, 3),
        ensemble = electron_ensemble
    )
    neutron = engine.add_particle(
        Vector(0, 1),
        ensemble = neutron_ensemble 
    )

    # gravity_force_vector = gravity(proton, electron, gravitational_field)
    # electrostatic_force_vector = electrostatic(proton, neutron, electrostatic_field)

    engine.animate()
    print(engine)