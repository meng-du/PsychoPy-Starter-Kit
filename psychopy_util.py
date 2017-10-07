#
# Utilities for PsychoPy experiments
# Author: Meng Du
# October 2017
#

import os
import json
import logging
from psychopy import gui, visual, core, event, info


def show_form_dialog(items, validation_func=None, reset_after_error=True, title='', order=(), tip=None, logger=None):
    """
    Show a form to be filled within a dialog. The user input values will be stored in items.
    See wxgui.DlgFromDict
    :param items: a dictionary with item name strings as keys, e.g. {'Subject ID': ''}
    :param validation_func: a function that takes the items dictionary, checks whether inputs are valid,
                            and returns a tuple valid (a boolean), message (a string)
    :param reset_after_error: a boolean; if true, all filled values will be reset in case of error
    :param title: a string form title
    :param order: a list containing keys in items, indicating the order of the items
    :param tip: a dictionary of tips for the items
    :param logger: (string / Unicode) a specific logger name to log information. Will log to the root logger if None
    """
    log = logging.getLogger(logger)
    while True:
        original_items = items.copy()
        dialog = gui.DlgFromDict(dictionary=items, title=title, order=order, tip=tip)
        if dialog.OK:
            if validation_func is None:
                break
            # validate
            valid, message = validation_func(items)
            if valid:
                break
            else:
                log.error('Error: ' + message)
                if reset_after_error:
                    items = original_items
        else:
            log.warning('User cancelled')
            core.quit()


class Presenter:
    """
    Methods that help to draw stuff in a window
    """
    def __init__(self, fullscreen=True, window=None, info_logger=None, trigger=None):
        """
        :param fullscreen: a boolean indicating either full screen or not
        :param window: an optional psychopy.visual.Window
                       a new full screen window will be created if this parameter is not provided
        :param info_logger: (string / Unicode) a specific logger name to log information. Will log to the root logger if None
        :param trigger: an ASCII character trigger when this is an fMRI task
        """
        self.window = window if window is not None else visual.Window(fullscr=fullscreen)
        self.expInfo = info.RunTimeInfo(win=window, refreshTest=None, verbose=False)
        self.trigger = trigger
        # logging
        self.logger = logging.getLogger(info_logger)
        self.logger.info(self.expInfo)
        # Positions
        self.CENTRAL_POS = (0.0, 0.0)
        self.LEFT_CENTRAL_POS = (-0.5, 0.0)
        self.RIGHT_CENTRAL_POS = (0.5, 0.0)
        self.LIKERT_SCALE_INSTR_POS = (0, 0.8)
        self.LIKERT_SCALE_OPTION_INTERVAL = 0.2
        self.LIKERT_SCALE_OPTION_POS_Y = -0.2
        self.LIKERT_SCALE_LABEL_POS_Y = -0.35
        self.FEEDBACK_POS_Y_DIFF = -0.4
        # Selection
        self.SELECTED_STIM_OPACITY_CHANGE = 0.5

    def pixel2norm(self, length):
        """
        Convert a length in pixels to two lengths in Psychopy normalised units on x and y axis respectively
        :param length: an integer or float length in pixels
        :return: a tuple of two float lengths
        """
        x0, y0 = self.window.size
        x = float(length) / x0
        y = float(length) / y0
        return x, y

    def load_all_images(self, img_path, img_extension, img_prefix=None):
        """
        Read all image files in img_path that end with img_extension, and create corresponding ImageStim.

        :param img_path: a string path which should end with '/'
        :param img_extension: a string of image file extension
        :param img_prefix: a string prefix of file names. If specified, files without this prefix wouldn't be loaded
        :return: a list of psychopy.visual.ImageStim
        """
        img_files = [filename for filename in sorted(os.listdir(img_path)) if filename.endswith(img_extension)]
        if img_prefix is not None:
            img_files = [filename for filename in img_files if filename.startswith(img_prefix)]
        img_files = [img_path + filename for filename in img_files]
        img_stims = [visual.ImageStim(self.window, image=img_file) for img_file in img_files]
        logging.info(img_extension + ' images loaded from ' + img_path)
        return img_stims

    def draw_stimuli_for_duration(self, stimuli, duration, wait_trigger=False):
        """
        Display the given stimuli for a given duration. If wait_trigger is True, the stimuli will be displayed until
        a <duration> number of triggers are received

        :param stimuli: either a psychopy.visual stimulus or a list of them to draw
        :param duration: a float time duration in seconds, or if waiting for a scanner trigger, an integer number of
                         triggers to wait for
        :param wait_trigger: (boolean) whether to wait for triggers or seconds
        """
        if isinstance(stimuli, visual.BaseVisualStim):
            stimuli.draw()
        else:
            for stim in stimuli:
                if stim is not None:  # skipping "None"
                    stim.draw()
        self.window.flip()
        if duration is not None:
            if wait_trigger:
                for _ in range(duration):
                    event.waitKeys(keyList=[self.trigger])
                    self.logger.info('Received trigger ' + self.trigger)
            else:
                core.wait(duration)

    def draw_stimuli_for_response(self, stimuli, response_keys, max_wait=float('inf'), wait_trigger=False):
        """
        :param stimuli: either a psychopy.visual stimulus or a list of them to draw
        :param response_keys: a list containing strings of response keys
        :param max_wait: a numeric value indicating the maximum number of seconds to wait for keys.
                         By default it waits forever
        :param wait_trigger: (boolean) whether to wait for triggers or seconds
                             If true, the program will wait for a <max_wait> number of triggers before proceeding
        :return: a tuple (key_pressed, reaction_time_in_seconds). Only the first response will be returned if there
                 are multiple.
        """
        if max_wait is None:
            max_wait = float('inf')
        self.draw_stimuli_for_duration(stimuli, duration=None)

        if wait_trigger:
            if isinstance(max_wait, int):
                duration = max_wait
            else:
                duration = 1
                self.logger.warning('Invalid duration, waiting for one trigger')  # TODO
            i = 0
            responses = []
            clock = core.Clock()
            while i != duration:
                results = event.waitKeys(keyList=[self.trigger] + response_keys, timeStamped=clock)
                for resp in results:
                    self.logger.info('Received signal ' + resp[0] + ' after ' + str(resp[1]) + ' seconds')
                    if resp[0] == self.trigger:
                        i += 1
                    else:
                        responses.append(resp)
            if len(responses) == 0:
                return None
            return responses[0]
        else:
            # wait for a time duration
            response = event.waitKeys(maxWait=max_wait, keyList=response_keys, timeStamped=core.Clock())
            if response is None:  # timed out without a response
                return None
            self.logger.info('Received response ' + str(response))
            return response[0]

    def show_instructions(self, instructions, position=(0, 0), other_stim=(), key_to_continue='space',
                          next_page_text='Press space to continue', next_page_pos=(0.0, -0.8), duration=None,
                          wait_trigger=False):
        """
        Show an instruction string, or a list of instructions strings with one on each page

        :param instructions: an instruction string, or a list containing instruction strings
        :param position: a tuple (x, y) position for the instruction text
        :param other_stim: a list of other psychopy.visual stimuli to be displayed on each page of instructions
        :param key_to_continue: a string of the key to press
        :param next_page_text: a string to show together with each page of instruction, could be None
        :param next_page_pos: a tuple of floats, position for the above string
        :param duration: (float or integer) if specified, the instructions will be shown for a maximum length of this
                         number of seconds (or triggers if using a scanner)
        """
        if type(instructions) is str:
            instructions = [instructions]
        if next_page_text is not None:
            next_page_stim = visual.TextStim(self.window, text=next_page_text, pos=next_page_pos)
        else:
            next_page_stim = None
        self.logger.info('Showing instructions')
        for i, instr in enumerate(instructions):
            instr_stim = visual.TextStim(self.window, text=instr, pos=position, wrapWidth=1.5)
            log_text = 'Instruction: ' + instr[:30].replace('\n', ' ')
            self.logger.info(log_text + '...' if len(instr) >= 30 else log_text)
            self.draw_stimuli_for_response(list(other_stim) + [instr_stim, next_page_stim], [key_to_continue],
                                           max_wait=duration, wait_trigger=wait_trigger)
        self.logger.info('End of instructions')

    def show_fixation(self, duration, pos=(0, 0), wait_trigger=False):
        """
        Show a '+' for a specified duration
        :param duration: a time duration in seconds
        :param pos: a position tuple for the fixation
        """
        plus_sign = visual.TextStim(self.window, text='+', pos=pos, height=0.2)
        self.logger.info('Showing fixation at ' + str(pos) + ' for ' + str(duration) + ' second(s)')
        self.draw_stimuli_for_duration(plus_sign, duration, wait_trigger)
        self.logger.info('End of fixations')

    def show_two_fixations(self, duration, color, pos=(0, 0), wait_trigger=False):
        """
        Show a '+' for a specified duration
        :param duration: a time duration in seconds
        """
        plus_signs = [visual.TextStim(self.window, text='+'),
                      visual.TextStim(self.window, text='+', pos=pos, color=color, height=0.2)]
        self.logger.info('Showing fixation at ' + str(pos))
        self.draw_stimuli_for_duration(plus_signs, duration, wait_trigger)
        self.logger.info('End of fixations')

    def show_blank_screen(self, duration, wait_trigger=False):
        """
        Show a blank screen for a specified duration
        :param duration: a time duration in seconds
        """
        blank = visual.TextStim(self.window, text='')
        self.logger.info('Showing blank screen')
        self.draw_stimuli_for_duration(blank, duration, wait_trigger)
        self.logger.info('End of blank screen')

    def likert_scale(self, instruction, num_options, option_texts=None, option_labels=None, side_labels=None,
                     response_keys=None, wait_trigger=False):
        """
        Show a Likert scale of the given range of numbers and wait for a response

        :param instruction: a string instruction to be displayed
        :param num_options: an integer number of options, should be greater than 1 and less than 11
        :param option_texts: a list of strings to be displayed as the options. If not specified, the default texts are
                             the range from 1 to num_options if num_options < 10, or 0 to 9 if num_options equals 10.
                             Length of this list should be the same as num_options.
        :param option_labels: a list of strings to be displayed alongside the option numbers.
                              Length of this list should be the same as num_options.
        :param side_labels: a tuple of two strings to be shown under the leftmost and rightmost options,
                            e.g. ('Not at all', 'Extremely')
        :param response_keys: an optional list of response keys. If not specified, the default keys are the range from 1
                              to num_options if num_options < 10, or 0 to 9 if num_options equals 10.
        :return: a tuple (response, reaction_time_in_seconds)
        """
        if num_options < 2 or num_options > 10:
            raise ValueError('Number of Likert scale options has to be greater than 1 and less than 11')
        if option_texts is not None and len(option_texts) != num_options:
            raise ValueError('Number of Likert scale option texts does not match the number of options')
        if option_labels is not None and len(option_labels) != num_options:
            raise ValueError('Number of Likert scale option labels does not match the number of options')
        if side_labels is not None and len(side_labels) != 2:
            raise ValueError('Number of Likert scale side labels has to be 2')

        # instruction
        stimuli = [visual.TextStim(self.window, text=instruction, pos=self.LIKERT_SCALE_INSTR_POS)]
        # option texts
        if option_texts is None:
            if num_options == 10:
                option_texts = [str(i) for i in range(num_options)]
            else:
                option_texts = [str(i + 1) for i in range(num_options)]
        # side labels
        if side_labels is not None:
            if len(side_labels) != 2:
                raise ValueError('Length of side labels must be 2')
            option_labels = [side_labels[0]] + [''] * (num_options - 2) + [side_labels[1]]
        # positions of options/labels
        scale_width = (len(option_texts) - 1) * self.LIKERT_SCALE_OPTION_INTERVAL
        if scale_width > 2:
            pos_x = [float(pos) / 100 for pos in range(-100, 100, int(200 / (len(option_texts) - 1)))]
        else:
            pos_x = [float(pos) / 100 for pos in range(-int(scale_width * 50), int(scale_width * 50) + 2,
                                                       int(self.LIKERT_SCALE_OPTION_INTERVAL * 100))]
        # construct stimuli
        for i in range(len(option_texts)):
            stimuli.append(visual.TextStim(self.window, text=option_texts[i],
                                           pos=(pos_x[i], self.LIKERT_SCALE_OPTION_POS_Y)))
        if option_labels is not None:
            for i in range(len(option_texts)):
                stimuli.append(visual.TextStim(self.window, text=option_labels[i],
                                               pos=(pos_x[i], self.LIKERT_SCALE_LABEL_POS_Y)))
        # response
        if response_keys is None:
            response_keys = [str(i + 1) for i in range(num_options)]
            if num_options == 10:
                response_keys[9] = '0'
        self.logger.info('Showing Likert scale')
        response = self.draw_stimuli_for_response(stimuli, response_keys, wait_trigger=wait_trigger)
        self.logger.info('End of Likert scale')
        return response

    def select_from_stimuli(self, stimuli, response_keys, max_wait=float('inf'), post_selection_time=1,
                            highlight=None, no_response_stim=None, no_resp_feedback_time=1, resp_wait_trigger=False,
                            post_select_wait_trigger=False, feedback_wait_trigger=False):
        """
        Draw stimuli on one screen and wait for a selection (key response). The selected stimulus can be optionally
        highlighted.

        The response_keys can be a dictionary with string response keys (e.g. 'f', 'j') as dictionary keys. The index
        of stimuli options associated with each response key should be specified as the dictionary values,
            e.g. {'f': 1, 'j': 2} means to press 'f' to select the second stimulus in the stimuli list, and press 'j'
            to select the third stimulus in the stimuli list
        Alternatively, response_keys could also be a list of string response keys, and the associated stimuli indexes
        will be assumed to be a sequence starting from zero, i.e. response_keys=['f', 'j'] is same as
        response_keys={'f': 0, 'j': 1}

        The stimulus index associated with the pressed response key will be returned.

        :param stimuli: a list of psychopy.visual stimulus to be displayed
        :param response_keys: a dictionary where keys are strings of response keys, and values are the corresponding
                              indexes of stimuli (in the stimuli list) that can be selected by the response key.
                              If passing a list or tuple of response keys, then the indexes are assumed to start from 0.
        :param max_wait: a numeric value indicating the maximum number of seconds to wait for keys.
                         By default it waits forever.
        :param post_selection_time: the duration (in seconds) to display the selected stimulus with a highlight (or
                                    reduced opacity if highlight is None).
        :param highlight: a psychopy.visual stimuli to be displayed at same position as the selected stimulus during
                          both post_selection_time and feedback_time. If None, the selected stimulus will be shown with
                          reduced opacity
        :param no_response_stim: a psychopy.visual stimulus to be displayed when participants respond too slow (i.e. no
                                 no response received with in max_wait seconds, if max_wait is an integer)
        :param no_resp_feedback_time: time (in seconds) to display feedback in case no response received
        :return: a dictionary containing the selected stimulus index and reaction time.
        """
        if type(response_keys) is not dict:
            response_keys = {key: i for i, key in enumerate(response_keys)}
        # display stimuli and get response
        self.logger.info('Showing options')
        response = self.draw_stimuli_for_response(stimuli, response_keys.keys(), max_wait, resp_wait_trigger)
        self.logger.info('End of options')
        if response is None or len(response) == 0:  # response too slow
            if no_response_stim is None:
                return
            # show feedback and return
            self.logger.info('No response received, showing feedback')
            self.draw_stimuli_for_duration(no_response_stim, no_resp_feedback_time, feedback_wait_trigger)
            self.logger.info('End of feedback')
            return
        else:
            key_pressed = response[0]
            rt = response[1]
            selection = response_keys[key_pressed]

            # post selection screen
            selected_stim = stimuli[selection]
            self.logger.info('Showing highlighted selection')
            if highlight is None:
                selected_stim.opacity -= self.SELECTED_STIM_OPACITY_CHANGE
                self.draw_stimuli_for_duration(stimuli, post_selection_time, post_select_wait_trigger)
                selected_stim.opacity += self.SELECTED_STIM_OPACITY_CHANGE
            else:
                highlight.pos = selected_stim.pos
                stimuli.append(highlight)
                self.draw_stimuli_for_duration(stimuli, post_selection_time, post_select_wait_trigger)
            self.logger.info('End of highlighted selection')

            return {'selection': selection, 'rt': rt}


class DataLogger:
    """
    Write data or messages to file
    """
    def __init__(self, filepath, filename, log_name='', logging_info=False):
        """
        Open file
        :param filepath: a string data file path
        :param filename: a string data file name
        :param log_name: a name for the log
        :param logging_info: if True, messages or data will be logged with timestamps and logging levels
        """
        if filepath[len(filepath) - 1] != '/':
            filepath += '/'
        if not os.path.isdir(filepath):
            os.mkdir(filepath)
        elif os.path.isfile(filepath + filename):
            raise IOError(filepath + filename + ' already exists')

        handler = logging.FileHandler(filepath + filename)
        if logging_info:
            handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)8s %(message)s'))
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(handler)

    def write_json(self, data):
        """
        Write data to file
        """
        string = json.dumps(data)
        self.logger.info(string)
