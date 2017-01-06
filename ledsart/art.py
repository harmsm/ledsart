__description__ = \
"""
"""
__author__ = "Michael J. Harms"
__date__ = "2017-01-01"

import random, time

class ArtInstallation:
    """
    Iterate some generator and display its output on a set of LED panels.  Also
    integrate sensor input for an interactive display.
    """
    def __init__(self,
                 generator,
                 display,
                 generator_configs=({},),
                 plot_configs=({},),
                 sampling_rate=0.1,
                 iteration_interval=1,
                 num_iterations=1000,
                 burn_in=50):
        """
        Initialize an ArtInstallation object.

        generator: a class (NOT instance!) that will be used to generate each
                   round.  The class should take **kwargs in generator_configs
                   to its __init__ function, expose the expose .iterate() and
                   .as_rgba().  .as_rgba should take the **kwargs in
                   plot_configs.

        display: an instance of a class that actually draws the output of the
                 generator.  It should expose .draw(), which takes the 
                 output of the generator as an argument.

        generator_config: list of dictionaries.  Each of dictionary should be
                          passable as **kwargs to the generator __init__ 
                          function.  While running, the art installation will
                          randomly select different generator configurations.
                        
        plot_config: list of dictionaries.  Each dictionary should be passable
                     as **kwargs to the .as_rgba function of the generator. The
                     installation will randomly select different plotting
                     configurations.

        sampling_rate: how long to wait between loops in the main .run()
                       function.

        iteration_interval: how long (in seconds) to wait between iterations.   

        num_iterations: how long to iterate each generator before randomly 

        burn_in: how many times to run the iterate() before first display                        
 
        """

        self._generator = generator
        self._display = display
        self._generator_configs = generator_configs
        self._plot_configs = plot_configs
        self.sampling_rate = sampling_rate
        self.iteration_interval = iteration_interval
        self.num_iterations = num_iterations
        self.burn_in = burn_in
        self.choose_new_generator = False
        self.choose_new_plot = False

        self._run_loop = False
        self._loaded_sensors = []

        self._choose_new_generator()
        self._choose_new_plot()

    def run(self):
        """
        Run the main loop.
        """

        self._run_loop = True
        self._run()

    def _choose_new_generator(self):
        """
        Choose a new generator and burn in.
        """

        # Create a new generator
        config = {}
        if len(self._generator_configs) != 0:
            config = random.choice(self._generator_configs)
        self._iterator = self._generator(**config)

        for i in range(self.burn_in):
            self._iterator.iterate()

    def _choose_new_plot(self):
        """
        Choose a new plot style.
        """

        plot_config = {}
        if len(self._plot_configs) != 0:
            plot_config = random.choice(self._plot_configs)
        self._plot_setting = plot_config


    def _run(self):
        """
        Main loop that runs continuously on its own thread.  Only invoke by
        self.run().
        """

        self._iteration_counter = 0
        self._last_time_switched = time.time() - self.iteration_interval

        while self._run_loop:

            # Update the display if we've waited long enough
            if time.time() - self._last_time_switched > self.iteration_interval:
                self._iterator.iterate()
                self._display.draw(self._iterator.as_rgba(**self._plot_setting))

                self._last_time_switched = time.time()
                self._iteration_counter += 1

            # Create a new generator, if we've run this generator for enough iterations
            if self._iteration_counter > self.num_iterations:
                self._choose_new_generator()
                self._choose_new_plot()
                self._iteration_counter = 0

            # Check sensor(s), if loaded, and update based on those sensors.
            self._check_sensors() 

            if self.choose_new_plot:
                self.choose_new_plot = False
                self._choose_new_plot()

            if self.choose_new_generator:
                self.choose_new_generator = False
                self._choose_new_generator()

            # Wait until next time step
            time.sleep(self.sampling_rate)

        return None

    def stop(self):
        """
        Stop execution of the loop.
        """

        self._run_loop = False
   
    def _check_sensors(self):

        for s in self._loaded_sensors:
            self.__dict__[s.property_to_mod] = s.read_and_process()

    def add_sensor(self,s):
        """
        """

        self._loaded_sensors.append(s)

