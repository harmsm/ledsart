import time

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(10)

class Sensor:
    """
    Class to wrap a sensor and modify some installation value (property_to_mod)
    in response to the sensor value.
    """

    def __init__(self,sensor,property_to_mod,
                 half_value=1.0,max_value=300,steepness=4):
        """
        Initialize sensor.

        sensor: instance of some sensor class that has an exposed .read()
                function. 
        property_to_mod: string of some property to modify in the ArtInstallation
                         class. ("sampling_rate","iteration_interval",
                         "num_iterations")
        half_value: point where value sets property to 1/2 of max_value
        max_value: maximum value of property_to_mod
        steepness: how steeply property_to_mod changes with sensor value.
        """

    def read_and_process(self):
        """
        """

        v = self.sensor.read()
        A = (v/self.half_value)**self.steepness

        return A/(1 + A)*self.max_value
        
class Pin:
    """
    Class that controls a raspberry pi GPIO pin.
    """

    def __init__(self,pin_number,frequency=50,duty_cycle=100,as_input=False):

        self.pin_number = pin_number
        self.duty_cycle = duty_cycle
        self.frequency = frequency
        self.as_input = as_input 
 
        self._pwm = None

        if self.as_input == True:
            GPIO.setup(self.pin_number, GPIO.IN)
        else:
            GPIO.setup(self.pin_number, GPIO.OUT)
            self.down()

    def up(self):
        """
        Put a pin in the "up" state.
        """

        if self._pwm == None:
            GPIO.output(self.pin_number,True)
        else:
            err = "cannot set to 'up': pulse width modulation running on pin.\n"
            raise ValueError(err)

    def down(self):
        """
        Put a pin in the "down" state.
        """

        if self._pwm == None:
            GPIO.output(self.pin_number,False)
        else:
            err = "cannot set to 'down': pulse width modulation running on pin.\n"
            raise ValueError(err)
      
    def input(self):
        """
        Read the state of a pin.
        """

        return GPIO.input(self.pin_number)

    def start_pwm(self):
        """
        Start pulse width modulation running (using self.frequency and
        self.duty_cycle).
        """

        self._pwm = GPIO.PWM(self.pin_number,self.frequency)
        self._pwm.start(self.duty_cycle)

    def stop_pwm(self):
        """
        Stop pulse width modulation.  (Doesn't throw an error if it wasn't 
        running in the first place).
        """


        if self._pwm != None:
            self._pwm.stop()    
            self._pwm = None

    def set_frequency(self,frequency):
        """
        Change pulse width modulation frequency.  If PWM is already running, it
        will be stopped and restarted with the new frequency.
        """
 
        self.frequency = frequency
        if self._pwm != None:
            self.stop_pwm()
            self.start_pwm()

    def set_duty_cycle(self,duty_cycle):
        """
        Change pulse width modulation duty cycle.  If PWM is already running, it
        will be stopped and restarted with the new duty cycle.
        """
        
        self.duty_cycle = duty_cycle
        if self._pwm != None:
            self.stop_pwm()
            self.start_pwm()

    def stop(self):
        """
        Shutdown a gpio pin, cleaning up.  
        """

        # Put the pin in the down state
        if self._pwm != None:
            self.stop_pwm()
        self.down()   

        GPIO.cleanup(self.pin_number)



class UltrasonicRange:
    """
    Class for controlling an ultrasonic range finder via two gpio pins (a 
    trigger pin that sends out a pulse and a echo pin that recieves the return).
    """

    def __init__(self,trigger_pin,echo_pin,timeout=100):

        self.trigger_pin = Pin(trigger_pin)
        self.echo_pin = Pin(echo_pin,as_input=True)

        self.timeout = timeout

        # Allow module to settle
        time.sleep(0.5)
    
    def read(self):
        """
        Calculate the distance to a target based on the length of the return
        echo. Returns a negative value of the system times out.
        """

        # Send 10 us pulse trigger
        self.trigger_pin.up()
        time.sleep(0.00001)
        self.trigger_pin.down()

        # Find start of echo
        counter = 0 
        start = time.time()
        while self.echo_pin.input() == 0 and counter < self.timeout:
            start = time.time()
            counter += 1

        if counter == self.timeout:
            return -1.0

        # Find end of echo
        counter = 0 
        stop = time.time()
        while self.echo_pin.input() == 1 and counter < self.timeout:
            stop = time.time()
            counter += 1

        if counter == self.timeout:
            return -1.

        # multiply high time by 340 m/s divided by 2 (ping went there and back)
        # to give distance in m
        return (stop - start)*170

    def stop(self):
        """
        Shut down and clean up the pins.
        """     
 
        self.trigger_pin.stop()
        self.echo_pin.stop()
       

    
 
