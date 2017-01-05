__description__ = \
"""
"""
__author__ = "Michael J. Harms"
__date__ = "2017-01-01"

import multiprocessing, random, time

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
                 num_iterations=1000):
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
                        
        return generating another generator. 
 
        """

        self._generator = generator
        self._display = display
        self._generator_configs = generator_configs
        self._plot_configs = plot_configs
        self.sampling_rate = sampling_rate
        self.iteration_interval = iteration_interval
        self.num_iterations = num_iterations

        self._run_loop = False

        self._create_new_generator()

    def run(self):
        """
        Run the main loop.
        """

        self._run_loop = True
        self._p = multiprocessing.Process(target=self._run)
        self._p.start()

    def _create_new_generator(self):
        """
        Choose a new generator and new display setting.
        """

        # Create a new generator
        config = {}
        if len(self._generator_configs) != 0:
            config = random.choice(self._generator_configs)
        self._iterator = self._generator(**config)

        # Choose a new plotting style
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
        self._next_time = -1

        while self._run_loop:

            # Update the display if we've waited long enough
            if time.time() > self._next_time:
                self._iterator.iterate()
                self._display.draw(self._iterator.as_rgba(**self._plot_setting))
                self._next_time = time.time() + self.iteration_interval
                self._iteration_counter += 1

            # Create a new generator, if we've run this generator for enough iterations
            if self._iteration_counter > self._num_iterations:
                self._create_new_generator()
                self._iteration_counter = 0

            # Check sensor(s), if loaded, and update based on those sensors.
            self._check_sensors() 

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


    def add_sensor(self):
        """
        """

        pass


