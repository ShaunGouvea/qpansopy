from enum import Flag,auto
import math


class classproperty(property):
    """A decorator that behaves like @property but works on the class level.

    Allows accessing class-level computed properties without instantiating the class.
    Useful for returning values derived from class attributes via property-like syntax.
    """
    def __get__(self, instance,owner):
        return self.fget(owner)


class QPANSOPYUnitType(Flag):


    ##Ignores the following variables as they are not integers. they will be populated as dictionaries outside of this class
    _ignore_ = ["_unit_category","_category_lookup"]

    ##TODO: Check all spelling
    NAUTICAL_MILE = NAUTICAL_MILES = auto()
    STATUTE_MILE = STATUTE_MILES = MILE = MILES = auto()
    METRE = METRES = auto()
    KILOMETRE = KILOMETRES = auto()
    FEET = FOOT = auto()
    NAUTICAL_MILES_PER_SECOND = auto()
    NAUTICAL_MILES_PER_MINUTE = auto()
    NAUTICAL_MILES_PER_HOUR = KNOTS = auto()
    METRES_PER_SECOND = auto()
    METRES_PER_MINUTE = auto()
    METRES_PER_HOUR = auto()
    STATUTE_MILES_PER_HOUR = MILES_PER_HOUR = auto()
    KILOMETRES_PER_HOUR = auto()
    CELSIUS = CENTIGRADE = auto()
    FAHRENHEIT = auto()
    KELVIN = auto()
    SECOND = auto()
    MINUTE = auto()
    HOUR = auto()
    PERCENT = auto()
    DEGREES = auto()
    RADIANS = auto()
    DEGREES_PER_SECOND = auto()
    DEGREES_PER_MINUTE = auto()
    DEGREES_PER_HOUR = auto()

    _unit_category = {}
    _category_lookup = {}


    @classproperty
    def distance_units(cls):
        return cls._unit_category["DISTANCE"]
    

    @classproperty
    def speed_units(cls):
        return cls._unit_category["SPEED"]


    @classproperty
    def temperature_units(cls):
        return cls._unit_category["TEMPERATURE"]
    

    @classproperty
    def distance_units(cls):
        return cls._unit_category["DISTANCE"]


    @classproperty
    def time_units(cls):
        return cls._unit_category["TIME"]


    @classproperty
    def angle_units(cls):
        return cls._unit_category["ANGLE"]


    @classproperty
    def turn_rate_units(cls):
        return cls._unit_category["TURN_RATE"]


    def get_category(unit:'QPANSOPYUnitType') -> str:
        return QPANSOPYUnitType._category_lookup.get(unit)


class QPANSOPYUnit:

    _abbreviation = {QPANSOPYUnitType.NAUTICAL_MILE: "nm",
                    QPANSOPYUnitType.STATUTE_MILE: "mi",
                    QPANSOPYUnitType.METRE: "m",
                    QPANSOPYUnitType.KILOMETRE: "Km",
                    QPANSOPYUnitType.FOOT: "ft",
                    QPANSOPYUnitType.NAUTICAL_MILES_PER_SECOND: "nm/s",
                    QPANSOPYUnitType.NAUTICAL_MILES_PER_MINUTE: "nm/min",
                    QPANSOPYUnitType.NAUTICAL_MILES_PER_HOUR: "nm/hr",
                    QPANSOPYUnitType.METRES_PER_SECOND: "m/s",
                    QPANSOPYUnitType.METRES_PER_MINUTE: "m/min",
                    QPANSOPYUnitType.METRES_PER_HOUR: "m/hr",
                    QPANSOPYUnitType.STATUTE_MILES_PER_HOUR: "mph",
                    QPANSOPYUnitType.KILOMETRES_PER_HOUR: "km/h",
                    QPANSOPYUnitType.CELSIUS: "°C",
                    QPANSOPYUnitType.FAHRENHEIT: "°F",
                    QPANSOPYUnitType.KELVIN: "°K",
                    QPANSOPYUnitType.SECOND: "sec",
                    QPANSOPYUnitType.MINUTE: "min",
                    QPANSOPYUnitType.HOUR: "hr",
                    QPANSOPYUnitType.PERCENT: "%",
                    QPANSOPYUnitType.DEGREES: "deg",
                    QPANSOPYUnitType.RADIANS: "rad",
                    QPANSOPYUnitType.DEGREES_PER_SECOND: "deg/s",
                    QPANSOPYUnitType.DEGREES_PER_MINUTE: "deg/min",
                    QPANSOPYUnitType.DEGREES_PER_HOUR: "deg/hr"}

    _speed_conversion = {QPANSOPYUnitType.NAUTICAL_MILES_PER_SECOND: {QPANSOPYUnitType.NAUTICAL_MILES_PER_SECOND:1,QPANSOPYUnitType.NAUTICAL_MILES_PER_MINUTE:0.0166667,QPANSOPYUnitType.NAUTICAL_MILES_PER_HOUR:0.000277778,QPANSOPYUnitType.METRES_PER_SECOND:1852,QPANSOPYUnitType.METRES_PER_MINUTE:111120,QPANSOPYUnitType.METRES_PER_HOUR:6667200,QPANSOPYUnitType.KILOMETRES_PER_HOUR: 6667200000,QPANSOPYUnitType.STATUTE_MILES_PER_HOUR:4142.806},
                         QPANSOPYUnitType.NAUTICAL_MILES_PER_MINUTE: {QPANSOPYUnitType.NAUTICAL_MILES_PER_SECOND:0.0166667,QPANSOPYUnitType.NAUTICAL_MILES_PER_MINUTE:1,QPANSOPYUnitType.NAUTICAL_MILES_PER_HOUR:60,QPANSOPYUnitType.METRES_PER_SECOND:30.8667,QPANSOPYUnitType.METRES_PER_MINUTE:1852,QPANSOPYUnitType.METRES_PER_HOUR:111120,QPANSOPYUnitType.KILOMETRES_PER_HOUR: 111.12,QPANSOPYUnitType.STATUTE_MILES_PER_HOUR:69.0468},
                         QPANSOPYUnitType.NAUTICAL_MILES_PER_HOUR: {QPANSOPYUnitType.NAUTICAL_MILES_PER_SECOND:0.000277778,QPANSOPYUnitType.NAUTICAL_MILES_PER_MINUTE:0.0166667,QPANSOPYUnitType.NAUTICAL_MILES_PER_HOUR:1,QPANSOPYUnitType.METRES_PER_SECOND:0.514444,QPANSOPYUnitType.METRES_PER_MINUTE:30.8667,QPANSOPYUnitType.METRES_PER_HOUR:1852,QPANSOPYUnitType.KILOMETRES_PER_HOUR: 1.852,QPANSOPYUnitType.STATUTE_MILES_PER_HOUR:1.15078},
                         QPANSOPYUnitType.METRES_PER_SECOND :{QPANSOPYUnitType.NAUTICAL_MILES_PER_SECOND:0.000539957,QPANSOPYUnitType.NAUTICAL_MILES_PER_MINUTE:0.0323974,QPANSOPYUnitType.NAUTICAL_MILES_PER_HOUR:1.94384,QPANSOPYUnitType.METRES_PER_SECOND:1,QPANSOPYUnitType.METRES_PER_MINUTE:60,QPANSOPYUnitType.METRES_PER_HOUR:3600,QPANSOPYUnitType.KILOMETRES_PER_HOUR: 3.6,QPANSOPYUnitType.STATUTE_MILES_PER_HOUR:2.23694},
                         QPANSOPYUnitType.METRES_PER_MINUTE: {QPANSOPYUnitType.NAUTICAL_MILES_PER_SECOND:0.0000089993,QPANSOPYUnitType.NAUTICAL_MILES_PER_MINUTE:0.000539957,QPANSOPYUnitType.NAUTICAL_MILES_PER_HOUR:0.0323974,QPANSOPYUnitType.METRES_PER_SECOND:0.0166667,QPANSOPYUnitType.METRES_PER_MINUTE:1,QPANSOPYUnitType.METRES_PER_HOUR:60,QPANSOPYUnitType.KILOMETRES_PER_HOUR: 0.06,QPANSOPYUnitType.STATUTE_MILES_PER_HOUR:0.0372823},
                         QPANSOPYUnitType.METRES_PER_HOUR: {QPANSOPYUnitType.NAUTICAL_MILES_PER_SECOND:0.000000149988,QPANSOPYUnitType.NAUTICAL_MILES_PER_MINUTE:0.00000899928,QPANSOPYUnitType.NAUTICAL_MILES_PER_HOUR:0.000539957,QPANSOPYUnitType.METRES_PER_SECOND:0.000277778,QPANSOPYUnitType.METRES_PER_MINUTE:0.0166667,QPANSOPYUnitType.METRES_PER_HOUR:1,QPANSOPYUnitType.KILOMETRES_PER_HOUR: 1000,QPANSOPYUnitType.STATUTE_MILES_PER_HOUR:1609.34},
                         QPANSOPYUnitType.KILOMETRES_PER_HOUR: {QPANSOPYUnitType.NAUTICAL_MILES_PER_SECOND:0.000149988,QPANSOPYUnitType.NAUTICAL_MILES_PER_MINUTE:0.00899928,QPANSOPYUnitType.NAUTICAL_MILES_PER_HOUR:0.539957,QPANSOPYUnitType.METRES_PER_SECOND:0.277778,QPANSOPYUnitType.METRES_PER_MINUTE:16.6667,QPANSOPYUnitType.METRES_PER_HOUR:1000,QPANSOPYUnitType.KILOMETRES_PER_HOUR: 1,QPANSOPYUnitType.STATUTE_MILES_PER_HOUR:0.621371},
                         QPANSOPYUnitType.STATUTE_MILES_PER_HOUR: {QPANSOPYUnitType.NAUTICAL_MILES_PER_SECOND:0.000241382,QPANSOPYUnitType.NAUTICAL_MILES_PER_MINUTE:0.0144829,QPANSOPYUnitType.NAUTICAL_MILES_PER_HOUR:0.868976,QPANSOPYUnitType.METRES_PER_SECOND:0.44704,QPANSOPYUnitType.METRES_PER_MINUTE:26.8224,QPANSOPYUnitType.METRES_PER_HOUR:1609.34,QPANSOPYUnitType.KILOMETRES_PER_HOUR: 1.60934,QPANSOPYUnitType.STATUTE_MILES_PER_HOUR:1}}

    _distance_conversion = {QPANSOPYUnitType.METRE: {QPANSOPYUnitType.METRE:1,QPANSOPYUnitType.KILOMETRE:0.001,QPANSOPYUnitType.NAUTICAL_MILE:0.0005399568035,QPANSOPYUnitType.MILE:0.0006213711922,QPANSOPYUnitType.FOOT:3.280839895},
                            QPANSOPYUnitType.KILOMETRE: {QPANSOPYUnitType.METRE:1000,QPANSOPYUnitType.KILOMETRE:1,QPANSOPYUnitType.NAUTICAL_MILE:0.5399568035,QPANSOPYUnitType.MILE:0.6213711922,QPANSOPYUnitType.FOOT:3280.839895},
                            QPANSOPYUnitType.NAUTICAL_MILE: {QPANSOPYUnitType.METRE:1852,QPANSOPYUnitType.KILOMETRE:1.852,QPANSOPYUnitType.NAUTICAL_MILE:1,QPANSOPYUnitType.MILE:1.15078,QPANSOPYUnitType.FOOT:6076.1184021},
                            QPANSOPYUnitType.MILE: {QPANSOPYUnitType.METRE:1609.344,QPANSOPYUnitType.KILOMETRE:1.609344,QPANSOPYUnitType.NAUTICAL_MILE:0.8689762419,QPANSOPYUnitType.MILE:1,QPANSOPYUnitType.FOOT:5280},
                            QPANSOPYUnitType.FOOT: {QPANSOPYUnitType.METRE:0.3048,QPANSOPYUnitType.KILOMETRE:0.0003048,QPANSOPYUnitType.NAUTICAL_MILE:0.000164579,QPANSOPYUnitType.MILE:0.000189394,QPANSOPYUnitType.FOOT:1}}

    _time_conversion = {QPANSOPYUnitType.SECOND:{QPANSOPYUnitType.SECOND:1,QPANSOPYUnitType.MINUTE:0.0166667,QPANSOPYUnitType.HOUR:0.000277778},
                        QPANSOPYUnitType.MINUTE:{QPANSOPYUnitType.SECOND:60,QPANSOPYUnitType.MINUTE:1,QPANSOPYUnitType.HOUR:0.0166667},
                        QPANSOPYUnitType.HOUR:{QPANSOPYUnitType.SECOND:3600,QPANSOPYUnitType.MINUTE:60,QPANSOPYUnitType.HOUR:1}}


    ##TODO: the idea for this is to create a property for each in a forloop to cut down on additional coding and allow for the plural and singular unit to be a property
    all_units = list(_speed_conversion.keys()) + list(_distance_conversion.keys()) + list(_time_conversion.keys())


    def __init__(self,quantity: float,unit:QPANSOPYUnitType) -> None:
        """
        QPANSOPY Unit Class is an easy way to store, convert and perform mathematical operations on values with differing units.\n\n
        Mathematical operations can be performed on two different units within the same unit category\n
        e.g. two units of distance added together\n
            Metre + NauticalMile results in Metre unit\n\n
        For some units it supports the cancellation and combining of units e.g.\n
            Metre_per_Second / Second results in Metre\n
            Meter / Second results in Metre_per_Second\n
            Metre_per_Second * Second results in Metre\n
            :param float quantity: value or quantity of the requested unit
            :param unit: Instance of Enum QPANSOPYUnitType
            :type unit: QPANSOPYUnitType"""
        
        ##ensures entered quantity for degrees is less than or equal to 360
        if unit == QPANSOPYUnitType.DEGREES:
            self.quantity = quantity % 360
        else:
            self.quantity = quantity
        self.unit = unit


    @staticmethod
    def split_unit(unit_instance: QPANSOPYUnitType,category:str = None,not_category:bool = False) -> list[QPANSOPYUnitType]:
        """
        Returns the base units of a QPANSOPYUnitType e.g. METRES_PER_SECOND -> [METRE,SECOND]
        If a category is specified only the units of that category will be returned e.g. METRES_PER_SECOND with category TIME -> [SECOND]
        If not_category is equal to True, then the opposite unit will be returned METRES_PER_SECOND not category TIME -> [METRE]
        
        :param unit_instance: instance of UnitType to return
        :type unit_instance: QPANSOPYUnitType
        :param category: string name of the unit category to filter for
        :type category: str
        :param not_category: If True, this will return any unit that is not of the requested category
        :type not_category: bool
        """

        units = unit_instance.name.split("_PER_")
        return_units = []
        if category is None:
            for unit_name in units:
                return_units.append(QPANSOPYUnitType[unit_name])
        else:
            if category in QPANSOPYUnitType._unit_category.keys():
                for unit in units:
                    unit_instance = QPANSOPYUnitType[unit]
                    if QPANSOPYUnitType.get_category(unit_instance) == category and not_category is False:
                        return_units.append(unit_instance)
                    if QPANSOPYUnitType.get_category(unit_instance) != category and not_category is True:
                        return_units.append(unit_instance)
            else: 
                raise KeyError("Category '{}' is not valid, please use one of: {}".format(category,QPANSOPYUnitType._unit_category.keys()))

        return return_units
        


    @staticmethod
    def same_unit_category(*units:QPANSOPYUnitType) -> bool:
        """
        Checks a set of units to determine if they are in the same unit category
           :param units: any number of arguments for comparison
           :type units: QPANSOPYUnitType
           :return bool: True / False
           """
        last_unit:QPANSOPYUnitType = None
        same_units = True
        for unit in units:
            if last_unit is None:
                last_unit = unit
            elif unit in QPANSOPYUnitType.distance_units and last_unit in QPANSOPYUnitType.distance_units or \
            unit in QPANSOPYUnitType.speed_units and last_unit in QPANSOPYUnitType.speed_units or \
            unit in QPANSOPYUnitType.time_units and last_unit in QPANSOPYUnitType.time_units or \
            unit in QPANSOPYUnitType.temperature_units and last_unit in QPANSOPYUnitType.temperature_units:
                next
            else:
                same_units = False
        return same_units
        

    @staticmethod
    def common_unit_category(*units: QPANSOPYUnitType,return_least_common:bool = False) -> bool:
        """
        Returns the most or least common unit category defaults to most occurrences
        :param units: units to get common category for
        :type units: QPANSOPYUnitType
        :param return_least_common: returns the units with the lowest occurrences
        :type return_least_common: bool
        """
        base_units = [QPANSOPYUnitType[name] for unit in units for name in unit.name.split("_PER_")]
        category_count = {}
        for unit in base_units:
            unit_category = QPANSOPYUnitType.get_category(unit)
            if type(unit_category) is str:
                if unit_category not in category_count.keys():
                    category_count[unit_category] = 1  
                else:
                    category_count[unit_category] += 1
            else:
                raise TypeError("Unit is: {} of category type: {} is not valid".format(unit,unit_category))
        if return_least_common:
            return min(category_count,key=category_count.get)
        else:
            return max(category_count,key=category_count.get)


    @property
    def metres(self) -> float:
        return self.convert_unit(self.quantity,self.unit,QPANSOPYUnitType.METRE)


    @property
    def kilometres(self) -> float:
        return self.convert_unit(self.quantity,self.unit,QPANSOPYUnitType.KILOMETRE)
    

    @property
    def feet(self) -> float:
        return self.convert_unit(self.quantity,self.unit,QPANSOPYUnitType.FOOT)
    

    @property
    def miles(self) -> float:
        return self.convert_unit(self.quantity,self.unit,QPANSOPYUnitType.MILE)
    

    @property
    def nautical_miles(self) -> float:
        return self.convert_unit(self.quantity,self.unit,QPANSOPYUnitType.NAUTICAL_MILE)


    @property
    def seconds(self) -> float:
        return self.convert_unit(self.quantity,self.unit,QPANSOPYUnitType.SECOND)
    
    
    @property
    def minutes(self) -> float:
        return self.convert_unit(self.quantity,self.unit,QPANSOPYUnitType.MINUTE)
    
    
    @property
    def hours(self) -> float:
        return self.convert_unit(self.quantity,self.unit,QPANSOPYUnitType.HOUR)


    @property
    def knots(self) -> float:
        return self.convert_unit(self.quantity,self.unit,QPANSOPYUnitType.NAUTICAL_MILES_PER_HOUR)


    @property
    def metres_per_second(self) -> float:
        return self.convert_unit(self.quantity,self.unit,QPANSOPYUnitType.METRES_PER_SECOND)


    @property
    def kilometres_per_hour(self) -> float:
        return self.convert_unit(self.quantity,self.unit,QPANSOPYUnitType.KILOMETRES_PER_HOUR)


    @property
    def miles_per_hour(self) -> float:
        return self.convert_unit(self.quantity,self.unit,QPANSOPYUnitType.MILES_PER_HOUR)


    @property
    def degrees_per_second(self) -> float:
        return self.convert_unit(self.quantity,self.unit,QPANSOPYUnitType.DEGREES_PER_SECOND)

    @property
    def percent(self) -> float:
        if self.unit == QPANSOPYUnitType.DEGREES:
            return math.tan(math.radians(self.quantity))
        elif self.unit == QPANSOPYUnitType.RADIANS:
            return math.tan(self.quantity)
        else:
            return self.quantity


    @property
    def radians(self) -> float:
        if self.unit == QPANSOPYUnitType.DEGREES:
            return math.radians(self.quantity)
        elif self.unit == QPANSOPYUnitType.PERCENT:
            return math.tanh(self.quantity)
        else:
            return self.quantity


    @property
    def degrees(self) -> float:
        if self.unit == QPANSOPYUnitType.RADIANS:
            return math.degrees(self.quantity)
        elif self.unit == QPANSOPYUnitType.PERCENT:
            return math.tanh(math.radians(self.quantity))
        else:
            return self.quantity


    @property
    def celsius(self) -> float:
        if self.unit == QPANSOPYUnitType.CELSIUS:
            return self.quantity
        elif self.unit == QPANSOPYUnitType.KELVIN:
            return self.quantity-272.15
        elif self.unit == QPANSOPYUnitType.FAHRENHEIT:
            return (self.quantity - 32) * 5/9


    @property
    def kelvin(self) -> float:
        if self.unit == QPANSOPYUnitType.CELSIUS:
            return self.quantity + 273.15
        elif self.unit == QPANSOPYUnitType.KELVIN:
            return self.quantity
        elif self.unit == QPANSOPYUnitType.FAHRENHEIT:
            return ((self.quantity - 32) * 5/9) + 273.15


    @property
    def fahrenheit(self) -> float:
        if self.unit == QPANSOPYUnitType.CELSIUS:
            return (self.quantity * 9/5) + 32
        elif self.unit == QPANSOPYUnitType.KELVIN:
            return (self.quantity - 273.15) * 9/5 + 32
        elif self.unit == QPANSOPYUnitType.FAHRENHEIT:
            return self.quantity


    @property
    def category(self) -> str:
        this_category:str = QPANSOPYUnitType._category_lookup.get(self.unit)
        return this_category


    @classmethod
    def convert_unit(cls,quantity:float,current_units:QPANSOPYUnitType,requested_units:QPANSOPYUnitType) -> float:
        if current_units in QPANSOPYUnitType.speed_units and requested_units in QPANSOPYUnitType.speed_units:
            return quantity * cls._speed_conversion[current_units][requested_units]
        if current_units in QPANSOPYUnitType.distance_units and requested_units in QPANSOPYUnitType.distance_units:
            return quantity * cls._distance_conversion[current_units][requested_units]
        if current_units in QPANSOPYUnitType.time_units and requested_units in QPANSOPYUnitType.time_units:
            return quantity * cls._time_conversion[current_units][requested_units]
        else:
            raise TypeError("Cannot convert from {} to {}".format(current_units.name,requested_units.name))



    def __add__(self,other) -> 'QPANSOPYUnit':
        """
        Addition arithmetic for QPANSOPYUnit\n
        :param QPANSOPYUnit | float | int other: value to add to Instance of QPANSOPYUnit
        :return QPANSOPYUnit: new instance of QPANSOPYUnit is returned
        """
        if type(other) is QPANSOPYUnit:
                if self.same_unit_category(self.unit,other.unit):
                    new_quantity = self.quantity + self.convert_unit(other.quantity,other.unit,self.unit)
                    return QPANSOPYUnit(new_quantity,self.unit)
                else:
                    raise TypeError("Cannot add {} to {}".format(self.unit.name,other.unit.name))
        elif type(other) is float or type(other) is int:
            return QPANSOPYUnit(self.quantity + other,self.unit)
        else:
            raise TypeError("Cannot add {} to QPANSOPYUnit.".format(type(other.unit)))


    def __radd__(self,other) -> 'QPANSOPYUnit':
        if type(other) is float or type(other) is int:
            return QPANSOPYUnit(self.quantity + other,self.unit)
        else:
            raise TypeError("Cannot add {} to QPANSOPYUnit.".format(type(other)))


    def __sub__(self,other) -> 'QPANSOPYUnit':
        """
        subtraction arithmetic for QPANSOPYUnit\n
        :param QPANSOPYUnit | float | int other: value to subtract from Instance of QPANSOPYUnit
        :return QPANSOPYUnit: new instance of QPANSOPYUnit is returned
        """
        if type(other) is QPANSOPYUnit:
                if self.same_unit_category(self.unit,other.unit):
                    new_quantity = self.quantity - self.convert_unit(other.quantity,other.unit,self.unit)
                    return QPANSOPYUnit(new_quantity,self.unit)
                else:
                    raise TypeError("Cannot subtract {} from {}".format(type(self.unit,type(other.unit))))
        elif type(other) is float or type(other) is int:
            return QPANSOPYUnit(self.quantity - other,self.unit)
        else:
            raise TypeError("Cannot subtract {} from QPANSOPYUnit.".format(type(other)))
        

    def __rsub__(self,other) -> 'QPANSOPYUnit':
        if type(other) is float or type(other) is int:
            return QPANSOPYUnit(self.quantity - other,self.unit)
        else:
            raise TypeError("Cannot subtract QPANSOPYUnit from {}.".format(type(other)))


    def __mul__(self,other) -> 'QPANSOPYUnit':
        """
        multiplication arithmetic for QPANSOPYUnit\n
        :param QPANSOPYUnit | float | int other: value to multiply to Instance of QPANSOPYUnit
        :return QPANSOPYUnit: new instance of QPANSOPYUnit is returned
        """
        if type(other) is QPANSOPYUnit:
            if self.unit == other.unit:
                #This would be units^2, right now this is ignored and value is returned in the source units, unsure if this should raise error or if UNIT_SQUARED (area_units) should be supported
                return QPANSOPYUnit(self.quantity * other.quantity,self.unit)
            elif self.unit != other.unit:
                new_units = "{}_PER_{}".format(self.unit,other.unit)
                new_quantity = self.quantity * self.convert_unit(other.quantity,other.unit,self.unit)
                try:
                    return QPANSOPYUnit(new_quantity,QPANSOPYUnitType[new_units])
                except KeyError:
                    return NotImplementedError("Cannot multiply {} with {}, unit {}_PER_{} is not implimented".format(self.unit,other.unit,self.unit,other.unit))
        elif type(other) is float or type(other) is int:
            return QPANSOPYUnit(self.quantity * other,self.unit)
        else:
            raise TypeError("Cannot multiply {} with QPANSOPYUnit.".format(type(other)))


    def __truediv__(self,other) -> 'QPANSOPYUnit':
        """
        division arithmetic for QPANSOPYUnit\n
        :param QPANSOPYUnit | float | int other: value to divide from Instance of QPANSOPYUnit
        :return QPANSOPYUnit: new instance of QPANSOPYUnit is returned
        """
        if type(other) is QPANSOPYUnit:
            if self.unit == other.unit:
                return QPANSOPYUnit(self.quantity / other.quantity,self.unit)
            else:
                #This (self) unit is a compound unit e.g. Speed or Turn Rate, This would result in an acceleration unit
                if "_PER_" in self.unit.name:
                    raise NotImplementedError("Units of Acceleration are not currently supported")
                #Other unit is a compound unit e.g. Speed or Turn Rate
                elif "_PER_" in other.unit.name:
                    #Get the common category for both units, common category is the one that will cancel out as part of the divide operation
                    common_category = self.common_unit_category(self.unit,other.unit)
                    #figure out which of the fundamental units is the common one, this will be converted to work out the new quantity
                    requested_unit:QPANSOPYUnitType = self.split_unit(other.unit,common_category)[0]
                    #Figure out which of the fundamental units is not the common category, this will be the final units (common category will cancel)
                    final_units:str = self.split_unit(other.unit,common_category,True)[0].name
                    # This calculates the new quantity
                    new_quantity: float = self.convert_unit(self.quantity,self.unit,requested_unit) / other.quantity
                #Both sets of units are a compound unit e.g Speed or Turn Rate, a new compound unit would be the result
                elif "_PER_" in self.unit.name and "_PER_" in other.unit.name:
                    raise NotImplementedError("Creation of new units for rate of change are not currently supported")
                #Units are of the same category but different units, so the quantity of other is converted first
                elif QPANSOPYUnitType.get_category(self.unit) == QPANSOPYUnitType.get_category(other.unit): 
                    new_quantity:float = self.quantity / self.convert_unit(other.quantity,other.unit,self.unit)
                    final_units = self.unit.name
                else:
                    raise NotImplementedError("Cannot divide {} with {}, unit {}_PER_{} is not implimented".format(self.unit,other.unit,self.unit.name,other.unit.name))
                try:
                    new_units:QPANSOPYUnit = QPANSOPYUnitType[final_units]
                    return QPANSOPYUnit(new_quantity,new_units)
                except KeyError:
                    return KeyError("Unit {} is not a valid unit".format(final_units))
        elif type(other) is float or type(other) is int:
            return QPANSOPYUnit(self.quantity / other,self.unit)
        else:
            raise TypeError("Cannot divide {} with QPANSOPYUnit.".format(type(other)))
        
    def __rtruediv__(self):
        raise NotImplementedError("Unit Scaling is not currently supported")




#Redefine the Unit Category dictionaries outside of the QPANSOPYUnitType Enum class
QPANSOPYUnitType._unit_category = {\
                    #Speed Units
                    "SPEED": QPANSOPYUnitType.NAUTICAL_MILES_PER_SECOND |\
                             QPANSOPYUnitType.NAUTICAL_MILES_PER_MINUTE |\
                             QPANSOPYUnitType.NAUTICAL_MILES_PER_HOUR |\
                             QPANSOPYUnitType.METRES_PER_SECOND |\
                             QPANSOPYUnitType.METRES_PER_MINUTE |\
                             QPANSOPYUnitType.METRES_PER_HOUR,
                    #Distance Units
                    "DISTANCE": QPANSOPYUnitType.NAUTICAL_MILE |\
                                QPANSOPYUnitType.METRE |\
                                QPANSOPYUnitType.FOOT |\
                                QPANSOPYUnitType.MILE,
                    #Temperature Units
                    "TEMPERATURE": QPANSOPYUnitType.CELSIUS |\
                                   QPANSOPYUnitType.FAHRENHEIT |\
                                   QPANSOPYUnitType.KELVIN,
                    #Turn Rate Units
                    "TURN_RATE": QPANSOPYUnitType.DEGREES_PER_HOUR |\
                                 QPANSOPYUnitType.DEGREES_PER_MINUTE |\
                                 QPANSOPYUnitType.DEGREES_PER_SECOND,
                    #Time Units
                    "TIME": QPANSOPYUnitType.HOUR |\
                            QPANSOPYUnitType.MINUTE|\
                            QPANSOPYUnitType.SECOND,
                    #Angle Units
                    "ANGLE": QPANSOPYUnitType.PERCENT |\
                             QPANSOPYUnitType.DEGREES}

#Inverted Dictionary for reverse lookup
QPANSOPYUnitType._category_lookup = {unit: category for category in QPANSOPYUnitType._unit_category for unit in QPANSOPYUnitType._unit_category[category]}
    
