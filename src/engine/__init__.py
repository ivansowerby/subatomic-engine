from __future__ import annotations
from typing import Union, Callable, Optional, Any
from engine.ludus import Ludus
from engine.util.overload import BinaryNumericOverload
from engine.util.typing import Number, Array, Object, decimalize
from collections import defaultdict
from functools import reduce
from math import factorial as fact
from decimal import Decimal, getcontext as decimal_context
from termcolor import colored
from engine.util.log import Log

class Vector(BinaryNumericOverload):
    def __init__(self, *vector: Number) -> None:
        self.vector = list(vector)

    def dimensionality(self) -> int:
        return len(self.vector)
    
    def extend(self, *scalars: Number) -> None:
        self.vector.extend(scalars)

    def fill(scalar: Number, dimensionality: int) -> Vector:
        return Vector(*[scalar for _ in range(dimensionality)])
    
    def solve(vectors: Union[tuple[Vector], list[Vector]]) -> Vector:
        if len(vectors) == 0: raise ValueError
        return reduce(lambda f, g: f + g, vectors)

    def magnitude(self) -> Number:
        return sum([scalar ** 2 for scalar in self.vector]).sqrt()
    
    def magnitude_mapping(self, to_magnitude: Number ) -> Vector:
        from_magnitude = self.magnitude()
        scalar_hat = to_magnitude / from_magnitude if from_magnitude != 0 else 0
        return self * scalar_hat
    
    def type_mapping(self, map: Callable[[Number], Any]) -> None:
        self.vector = [map(scalar) for scalar in self.vector]
    
    def decimalize(*tensors: Tensor) -> Vector|list[Vector]:
        if len(tensors) == 0: return Vector()
        vectors = []
        for tensor in tensors:
            if isinstance(tensor, Number): decimal = decimalize(tensor)
            elif isinstance(tensor, Vector): decimal = Vector(*[decimalize(scalar) for scalar in tensor.vector])
            else: raise ValueError
            vectors.append(decimal)
        if len(vectors) == 1: return vectors[0]
        return vectors

    def constant(self) -> Callable[[Number], Vector]:
        return lambda _ = None: self

    def __len__(self) -> int:
        return self.dimensionality()

    def __repr__(self) -> str:
        return str(tuple(self.vector))
    
    def __iter__(self) -> Number:
        for scalar in self.vector: yield scalar

    def __operation__(
            self,
            other: Union[Vector, Number],
            operator: Callable,
            is_augmented: bool = False
        ) -> Vector:
        if isinstance(other, Number):
            other = Vector.fill(other, len(self))
        if not isinstance(other, Vector): return NotImplemented
        output = Vector()
        for i in range(max(len(self), len(other))):
            output_scalar = operator(*map(lambda v: v.vector[i] if i < len(v) else 0, (self, other)))
            output.extend(output_scalar)
        if is_augmented:
            self.vector = list(output.vector)
            return self
        else:
            return output
    
    def dumps(self) -> list:
        return [float(scalar) for scalar in self.vector]

Tensor = Union[Vector, Number]

class Kinematics:
    SERIES_FORMULA = lambda d, i, t = 1: d * (t ** i) * Vector.decimalize(1 / fact(i))

    def __init__(
            self,
            velocity: Vector = Vector(),
            /,
            *higher_degrees: Vector
        ) -> None:
        self.velocity = Vector.decimalize(velocity)
        self.degrees = [self.velocity, *Vector.decimalize(*higher_degrees)]
    
    def __check__(self, degree: int) -> None:
        if degree < 1: raise ValueError
        elif len(self.degrees) == 0:
            velocity = velocity if isinstance(self.velocity, Number) else 0 
            self.degrees.append(velocity)
        [self.degrees.append(Vector()) for _ in range(degree - len(self.degrees))]

    def set_motion(self, vector: Vector, degree: int) -> None:
        self.__check__(degree)
        #zero-based indexing
        degree -= 1
        self.degrees[degree] = Vector.decimalize(vector)

    def add_motion(self, vector: Vector, degree: int) -> None:
        self.__check__(degree)
        #zero-based indexing
        degree -= 1
        motion = Vector.solve((self.degrees[degree], Vector.decimalize(vector)))
        self.degrees[degree] = motion
    
    def dumps(self) -> list:
        return [degree.dumps() if isinstance(degree, Vector) else [] for degree in self.degrees]

class Force(BinaryNumericOverload):
    def __init__(
        self,
        id: str,
        magnitude: Number,
        center: Tensor
    ) -> None:
        self.id = id
        self.magnitude = Vector.decimalize(magnitude)
        self.center = Vector.decimalize(center)
    
    def collapse(self) -> Number:
        return self.magnitude * self.center
    
    def solve(forces: Union[tuple[Force], list[Force]]) -> Force:
        if len(forces) == 0: raise ValueError
        return reduce(lambda f, g: f + g, forces)
    
    __PRINTER__ = lambda magnitude: colored(magnitude, color = 'light_cyan')
    def __repr__(self) -> str:
        return f'{Force.__PRINTER__(str(self.magnitude))} @ {self.id}'
    
    def __operation__(
            self,
            other: Force,
            operator: Callable,
            is_augmented: bool = False
        ) -> Force:
        if not isinstance(other, Force): return NotImplemented
        elif self.id != other.id: raise ValueError('force must be of same field. Both GIDs must be equal')
        #magnitude scalar
        output_magnitude = operator(self.magnitude, other.magnitude)
        #center magnitude-weighted mean
        output_center = operator(self.collapse(), other.collapse()) / (self.magnitude + other.magnitude)
        output = Force(self.id, output_magnitude, output_center)
        if is_augmented:
            self.magnitude = output.magnitude
            self.center = output.center
            return self
        else:
            return output
    
    def dumps(self) -> dict:
        return {
            'id': self.id,
            'magnitude': float(self.magnitude),
            'center': float(self.center) if isinstance(self.center, Number) else self.center.dumps() 
        }

class Field:
    def __init__(
            self,
            id: str,
            name: str,
            formula: Callable = None,
            units: str = None
        ) -> None:
        self.id = id
        self.name = name
        self.formula = formula
        self.units = units
    
    def has(
            self,
            magnitude: Number,
            relative_center: Tensor = 0.5
        ) -> Force:
        return Force(self.id, magnitude, relative_center)
    
    def calculate_force(self, *args) -> Vector:
        if self.formula == None: return Vector(0)
        return self.formula(*args)
    
    __PRINTER__ = lambda name: colored(name, 'cyan')
    def __repr__(self) -> str:
        return f'{Field.__PRINTER__(self.name.capitalize())}=={self.id}'
    
    def dumps(self) -> dict:
        # return {
        #     'id': self.id,
        #     'name': self.name,
        #     'formula': self.formula,
        #     'units': self.units
        # }
        return vars(self)

Fields = Union[Array, Field]

class Ensemble:
    def __init__(
            self,
            id: str,
            name: str,
            forces: Union[Array, Force],
            rest_energy: Number 
        ) -> None:
        self.id = id
        self.name = name
        self.forces = []
        self.add_forces(forces)
        self.solve_forces()
        self.rest_energy = Vector.decimalize(rest_energy)
    
    def add_forces(self, forces: Union[Array, Force]) -> None:
        if isinstance(forces, Force): forces = [forces]
        elif type(forces) == tuple: forces = list(forces)
        elif not type(forces) == list: raise TypeError
        self.forces.extend(forces)
    
    def __getitem__(self, key: str) -> Force:
        for force in self.forces:
            if key == force.id: return force 
        return None
    
    #solve alike-forces
    def solve_forces(self) -> None:
        if len(self.forces) <= 1: return None
        fields = defaultdict(list)
        while len(self.forces) > 1:
            force: Force = self.forces.pop()
            field = force.id
            fields[field].append(force)
        for forces in fields.values():
            solved_force = reduce(lambda f, g: f + g, forces)
            self.forces.append(solved_force)
    
    __PRINTER__ = lambda name: colored(name, 'blue')
    def __repr__(self) -> str:
        return f'{Ensemble.__PRINTER__(self.name.capitalize())}=={self.id}'

    def dumps(self) -> dict:
        if not isinstance(self.forces, Array): self.forces = [self.forces]
        return {
            'id': self.id,
            'name': self.name,
            'forces': [force.dumps() for force in self.forces if isinstance(force, Force)],
            'rest_energy': float(self.rest_energy)
        }

class Particle:
    def __init__(
            self,
            id: str,
            position: Vector,
            kinematics: Kinematics,
            ensemble: Ensemble = None
        ) -> None:
        self.id = id
        self.position = Vector.decimalize(position)
        self.kinematics = kinematics
        self.ensemble = ensemble
    
    def force(self, id: str) -> Force:
        forces = self.ensemble.forces
        return Force.solve([force for force in forces if force.id == id])

    def __repr__(self) -> str:
        return self.id
    
    def dumps(self) -> dict:
        return {
            'id': self.id,
            'position': self.position.dumps(),
            'kinematics': self.kinematics.dumps(),
            'ensemble': self.ensemble.dumps()
        }

def index_for_object(d: dict) -> Object:
    return d[Object]

class Engine(Ludus):
    def __init__(self, precision: int = 50) -> None:
        super().__init__(encoded = False)
        self.time = 0
        context = decimal_context()
        context.prec = precision
    
    def add_field(
            self,
            name: Optional[str] = None,
            formula: Callable[[Particle, Particle, Fields], Vector] = None,
            units: str = None
        ) -> Field:
        id = self.new_group()
        field = Field(id, name, formula, units)
        self.add_attribute(id, field)
        return field

    def assign_field(
        self,
        field: Field,
        formula: Callable[[Particle, Particle, Fields], Vector],
        units: str = None
        ) -> None:
        field.formula = formula
        if units != None: self.units = units

    def add_ensemble(
            self,
            name: Optional[str] = None,
            forces: Array = [],
            rest_energy: Number = 0
        ) -> Ensemble:
        id = self.new_group()
        ensemble = Ensemble(id, name, forces, rest_energy)
        self.add_attribute(id, ensemble)
        return ensemble
    
    def remove_ensemble(
            self,
            id: Union[Ensemble, str] 
        ) -> None:
        """
        id(entifier) can be:
        the Ensemble-class object iself,
        the (g)id of the Ensemble object, or
        the the name attribute of the Ensemble object(s) 
        """
        ids = []
        if isinstance(id, Ensemble): id = id.id
        if type(id) == str:
            if Ludus.is_id(id, Ludus.GID):
                ids = [id]
            else:
                name = id
                for group in map(index_for_object, self.attributes.values()):
                    if isinstance(group, Ensemble) and name == group.name:
                        id = group.id
                        ids.append(id)
            [self.clear_attributes(gid) for gid in ids]
        else: raise ValueError

    def add_particle(
            self,
            position: Union[Vector, Array],
            kinematics: Union[Kinematics, Vector, Array] = Kinematics(),
            ensemble: Optional[Ensemble] = None,
        ) -> Particle:
        id = self.new_object()
        if isinstance(position, Array): position = Vector(*position)
        if isinstance(kinematics, Array): kinematics = Vector(*kinematics)
        if isinstance(kinematics, Vector): kinematics = Kinematics(kinematics)
        particle = Particle(id, position, kinematics, ensemble)
        self.add_property(id, particle)
        self.attach_group(uid = id, gid = [force.id for force in ensemble.forces])
        return particle
    
    def remove_particle(
            self,
            id: Union[Ensemble, str]
    ) -> None:
        """
        id(entifier) can be:
        the Ensemble-class object iself, or
        the (u)id of the Ensemble object
        """
        if isinstance(id, Particle): id = id.id
        if type(id) == str and Ludus.is_id(id, Ludus.UID):
            self.remove_object(uid = id)
        else: raise ValueError

    def animate(self, t: Number = 1) -> None:
        if not isinstance(t, Decimal): t = decimalize(t)
        self.time += t
        #for each field
        for gid, objects in self.groups.items():
            group = self.attributes[gid]
            field: Field = index_for_object(group)
            #for each particle, in field
            for i, uid_1 in enumerate(objects):
                object_1 = self.objects[uid_1]
                particle_1: Particle = index_for_object(object_1)
                # groups_1 = object_1['gid']
                # if gid not in groups_1: continue
                for uid_2 in objects[i+1:]:
                    object_2 = self.objects[uid_2]
                    particle_2: Particle = index_for_object(object_2)
                    # groups_2 = object_2['gid']
                    # if gid not in groups_2: continue
                    force_vector = field.calculate_force(
                        particle_1,
                        particle_2,
                        field
                    )

                    #particle 1
                    force_1 = particle_1.force(gid)
                    acceleration_1 = force_vector / force_1.magnitude
                    kinematics_1 = particle_1.kinematics
                    kinematics_1.add_motion(acceleration_1, degree = 2)
                    #particle 2
                    force_2 = particle_2.force(gid)
                    acceleration_2 = force_vector / force_2.magnitude
                    kinematics_2 = particle_2.kinematics
                    kinematics_2.add_motion(acceleration_2, degree = 2)
        for object in self.objects.values():
            particle: Particle = index_for_object(object)
            position = particle.position
            kinematics = particle.kinematics
            degrees = kinematics.degrees
            #position
            particle.position = Vector.solve([Kinematics.SERIES_FORMULA(degree, i, t) for i, degree in enumerate((position, *degrees), 1)])
            #kinematics
            velocity = Vector.solve([Kinematics.SERIES_FORMULA(degree, i, t) for i, degree in enumerate(degrees)])
            kinematics.set_motion(velocity, degree = 1)
            kinematics.set_motion(Vector(), degree = 2)

    #literal colour
    __TIME_LABEL__ = colored('time elapsed', on_color = 'on_black')
    __POSITION_LABEL__ = colored('position', color = 'red')
    __VELOCITY_LABEL__ = colored('velocity', color = 'green')
    __ENSEMBLE_LABEL__ = colored('ensemble', color = 'blue')
    __FIELDS_LABEL__ = colored('fields', color = 'cyan')
    #lambda colour
    __PARTICLE_PRINTER__ = lambda name: colored(name, color = 'magenta')
    __UNITS_PRINTER__ = lambda name: colored(name if name != None else 'a.u.', color = 'blue', attrs = ['bold'])
    def __repr__(self) -> str:
        log = Log()
        log.pair(Engine.__TIME_LABEL__, f'{self.time}s')
        for object in self.objects.values():
            particle: Particle = index_for_object(object)
            log.pair(
                Engine.__PARTICLE_PRINTER__(particle.ensemble.name),
                value = str(particle),
                delimiter = '@'
            )
            log.open_section()

            log.pair(Engine.__POSITION_LABEL__, str(particle.position))

            log.pair(Engine.__VELOCITY_LABEL__, str(particle.kinematics.degrees[0]))

            ensemble: Ensemble = particle.ensemble
            log.pair(Engine.__ENSEMBLE_LABEL__, str(ensemble))

            forces: list[Force] = ensemble.forces
            log.open_list(Engine.__FIELDS_LABEL__)
            for force in forces:
                object = self.attributes[force.id]
                field: Field = index_for_object(object)
                log.pair(
                    str(force),
                    str(field),
                    delimiter = f'({Engine.__UNITS_PRINTER__(field.units)}) =>'
                )
            log.close_list()
            log.close_section()
        return log.log.rstrip('\n')

    def dumps(self) -> dict:
        dump = defaultdict(list)
        for object in map(index_for_object, (*self.objects.values(), *self.attributes.values())):
            for object_class, key in (
                    (Particle, 'particles'),
                    (Field, 'fields'),
                    (Ensemble, 'ensembles')
                ):
                if not isinstance(object, object_class): continue
                dump[key].append(object.dumps())
                break
        return dict(dump)
