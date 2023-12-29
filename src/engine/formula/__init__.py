from engine import Vector, Particle, Field, Fields
from engine.util.typing import Array
from decimal import Decimal

def inverse_square(
        particle_1: Particle,
        particle_2: Particle,
        field: Fields
    ) -> Vector:
    if isinstance(field, Array):
        if len(field) != 1: raise ValueError
        field = field[0]
    if not isinstance(field, Field): raise TypeError
    
    field_1 = particle_1.ensemble[field.id] 
    field_2 = particle_2.ensemble[field.id]
    if field_1 == None or field_2 == None: return Vector(0)

    position_1 = particle_1.position + field_1.center
    position_2 = particle_2.position + field_2.center
    delta_position = position_2 - position_1
    divisor = delta_position.magnitude() ** 2
    force = ((field_1.magnitude * field_2.magnitude) / divisor) if divisor != 0 else 0 
    force_vector = delta_position.magnitude_mapping(force)
    return force_vector

#G
GRAVITATIONAL_CONSTANT = Decimal('6.674e-11')
def gravity(
        particle_1: Particle,
        particle_2: Particle,
        field: Fields
    ) -> Vector:
    force_vector = inverse_square(particle_1, particle_2, field) * GRAVITATIONAL_CONSTANT
    return force_vector

#k_e
COLOUMBS_CONSTANT = Decimal('8.988e9')
def electrostatic(
        particle_1: Particle,
        particle_2: Particle,
        field: Fields
    ) -> Vector:
    force_vector = inverse_square(particle_1, particle_2, field) * COLOUMBS_CONSTANT
    return force_vector